#!/usr/bin/env python3
"""
ESP32 MJPEG → WebRTC sender client for relay_server_v1.py

Usage examples:
  python sender.py \
    --esp-url http://192.168.0.62:81/stream \
    --server http://100.65.221.86:3100 \
    --camera-id cam1

Requirements:
  pip install opencv-python av aiohttp python-socketio aiortc

Notes:
- This client connects to your relay_server_v1.py via Socket.IO, joins as role=sender,
  captures frames from ESP32's MJPEG stream, and publishes a WebRTC video track.
- The relay server will fan out this track to any receivers.
"""

import argparse
import asyncio
import signal
import time
from typing import Optional

import cv2
import numpy as np
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCConfiguration, RTCIceServer
import av


class ESP32VideoTrack(VideoStreamTrack):
    """
    Pulls frames from an ESP32 MJPEG URL using OpenCV in a non-blocking way.
    Maintains a small latest-frame buffer to keep latency low.
    """

    def __init__(self, url: str, target_fps: float = 15.0, width: Optional[int] = None, height: Optional[int] = None):
        super().__init__()
        self.url = url
        self.cap = cv2.VideoCapture(url)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open ESP32 stream: {url}")

        # Optional resize
        self.resize = (width, height) if width and height else None

        # Timing control
        self.target_fps = max(1.0, float(target_fps))
        self.min_interval = 1.0 / self.target_fps
        self._next_due = time.perf_counter()

        # Last frame cache
        self._last_bgr: Optional[np.ndarray] = None

        # Warm-up: grab one frame
        ok, bgr = self.cap.read()
        if ok:
            self._last_bgr = bgr
        else:
            raise RuntimeError("Failed to read initial frame from ESP32 stream")

    async def recv(self) -> av.VideoFrame:
        pts, time_base = await self.next_timestamp()

        # Keep the capture non-blocking-ish by reading as fast as possible,
        # but throttling what we *send* to target_fps.
        ok, bgr = self.cap.read()
        if ok:
            self._last_bgr = bgr
        else:
            # If read failed momentarily, fallback to last frame (freezes instead of dropping track)
            bgr = self._last_bgr
            if bgr is None:
                # As a last resort, sleep briefly and retry
                await asyncio.sleep(0.01)
                ok, bgr = self.cap.read()
                if ok:
                    self._last_bgr = bgr
                else:
                    # Still failing: raise to let aiortc handle track end
                    raise av.AVError("ESP32 read failure")

        # Optional resize to reduce bandwidth
        if self.resize is not None:
            bgr = cv2.resize(bgr, self.resize, interpolation=cv2.INTER_AREA)

        # FPS gate: if called early, wait
        now = time.perf_counter()
        if now < self._next_due:
            await asyncio.sleep(self._next_due - now)
        self._next_due = time.perf_counter() + self.min_interval

        # Convert to RGB for av.VideoFrame
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        frame = av.VideoFrame.from_ndarray(rgb, format="rgb24")
        frame.pts = pts
        frame.time_base = time_base
        return frame

    def stop(self):
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        return super().stop()


async def run(esp_url: str, server_url: str, camera_id: str, fps: float, width: Optional[int], height: Optional[int], stun: Optional[str]):
    # Socket.IO client for signaling
    sio = socketio.AsyncClient()

    # Peer connection (STUN optional; TURN not required for Tailscale/local)
    rtc_config = None
    if stun:
        rtc_config = RTCConfiguration(iceServers=[RTCIceServer(urls=[stun])])
    pc = RTCPeerConnection(rtc_config)

    # Graceful cleanup
    async def cleanup():
        try:
            await pc.close()
        except Exception:
            pass
        if sio.connected:
            try:
                await sio.disconnect()
            except Exception:
                pass

    @pc.on("iceconnectionstatechange")
    async def on_ice_state_change():
        print("[pc] ICE state:", pc.iceConnectionState)
        if pc.iceConnectionState in ("failed", "disconnected", "closed"):
            await cleanup()

    # Connect to relay server and join as sender
    await sio.connect(server_url)
    join_reply = await sio.emit("join", {"role": "sender", "camera_id": camera_id}, callback=True)
    if join_reply and isinstance(join_reply, dict) and join_reply.get("camera_id"):
        camera_id = join_reply["camera_id"]
    print(f"[join] role=sender, camera_id={camera_id}")

    # Create and add video track
    track = ESP32VideoTrack(esp_url, target_fps=fps, width=width, height=height)
    pc.addTrack(track)

    # Create offer → send via Socket.IO → await answer → set remote
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # Send offer; expect an "answer" event response via callback pattern
    answer_fut = asyncio.get_event_loop().create_future()

    @sio.on("answer")
    def on_answer(data):
        if not answer_fut.done():
            answer_fut.set_result(data)

    await sio.emit("offer", {"role": "sender", "sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

    data = await answer_fut
    await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
    print("[webrtc] sender connected and streaming")

    # Keep alive until interrupted
    stop_event = asyncio.Event()

    def _signal_handler(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_running_loop().add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # Windows
            pass

    await stop_event.wait()

    # Cleanup
    await cleanup()


def main():
    p = argparse.ArgumentParser(description="ESP32→Relay WebRTC Sender")
    p.add_argument("--esp-url", required=True, help="ESP32 MJPEG stream URL (e.g., http://<ip>:81/stream)")
    p.add_argument("--server", required=True, help="Relay server URL (e.g., http://<host>:3010)")
    p.add_argument("--camera-id", required=True, help="Logical camera id")
    p.add_argument("--fps", type=float, default=15.0, help="Target FPS to send")
    p.add_argument("--width", type=int, default=None, help="Optional width for downscale")
    p.add_argument("--height", type=int, default=None, help="Optional height for downscale")
    p.add_argument("--stun", default=None, help="Optional STUN URL, e.g., stun:stun.l.google.com:19302")
    args = p.parse_args()

    try:
        asyncio.run(run(args.esp_url, args.server, args.camera_id, args.fps, args.width, args.height, args.stun))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
