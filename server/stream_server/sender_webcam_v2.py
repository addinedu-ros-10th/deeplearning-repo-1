import sys
import cv2
import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

SERVER_URL = "http://100.65.221.86:3010"  # 변경하세요

async def main(camera_id: str, camera_dev:str):
    sio = socketio.AsyncClient()
    pc = RTCPeerConnection()

    @sio.event
    async def connect():
        await sio.emit("join", {"role": "sender", "camera_id": camera_id})

    @sio.event
    async def joined(data):
        if data.get("role") != "sender":
            return
        # Attach webcam track(s)
        # OpenCV/MediaPlayer 중 하나 선택, 여기서는 OpenCV로 간단히
        # cap = cv2.VideoCapture(camera_dev)
        # if not cap.isOpened():
        #     print("[sender] cannot open camera")
        #     return

        # Use aiortc's MediaPlayer for stability if preferred
        player = MediaPlayer(camera_dev) if sys.platform != "win32" else MediaPlayer(0)
        if player and player.video:
            pc.addTrack(player.video)
        if player and player.audio:
            pc.addTrack(player.audio)

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await sio.emit("offer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

    @sio.event
    async def answer(data):
        await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
        print("[sender] connected")

    await sio.connect(SERVER_URL)
    await sio.wait()

if __name__ == "__main__":
    cam_id = sys.argv[1] if len(sys.argv) > 1 else "webcam1"
    cam_dev = sys.argv[2] if len(sys.argv) > 2 else "/dev/video0"
    asyncio.run(main(cam_id, cam_dev))