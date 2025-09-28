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
    player = None

    @sio.event
    async def connect():
        print(f"[sender] 서버에 연결됨: {camera_id}")
        await sio.emit("join", {"role": "sender", "camera_id": camera_id})

    @sio.event
    async def joined(data):
        nonlocal player
        if data.get("role") != "sender":
            return

        print(f"[sender] 송신자로 조인됨: {camera_id}")

        try:
            # MediaPlayer로 카메라 스트림 생성
            player = MediaPlayer(camera_dev) if sys.platform != "win32" else MediaPlayer(0)
            if player and player.video:
                pc.addTrack(player.video)
                print(f"[sender] 비디오 트랙 추가됨: {camera_id}")
            if player and player.audio:
                pc.addTrack(player.audio)
                print(f"[sender] 오디오 트랙 추가됨: {camera_id}")

            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            await sio.emit("offer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
            print(f"[sender] 오퍼 전송됨: {camera_id}")

        except Exception as e:
            print(f"[sender] 카메라 설정 실패: {e}")

    @sio.event
    async def answer(data):
        try:
            await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
            print(f"[sender] 연결 완료: {camera_id}")
        except Exception as e:
            print(f"[sender] 응답 처리 실패: {e}")

    @sio.event
    async def disconnect():
        print(f"[sender] 연결 끊김: {camera_id}")
        if player:
            try:
                player.video.stop() if player.video else None
                player.audio.stop() if player.audio else None
            except:
                pass

    # PeerConnection 상태 모니터링
    @pc.on("iceconnectionstatechange")
    async def on_ice_change():
        print(f"[sender] ICE 상태 변경: {camera_id} -> {pc.iceConnectionState}")

    @pc.on("connectionstatechange")
    async def on_connection_change():
        print(f"[sender] 연결 상태 변경: {camera_id} -> {pc.connectionState}")

    try:
        await sio.connect(SERVER_URL)
        print(f"[sender] 시작됨: {camera_id}")
        await sio.wait()
    except KeyboardInterrupt:
        print(f"[sender] 종료 중: {camera_id}")
    except Exception as e:
        print(f"[sender] 오류: {e}")
    finally:
        # 정리 작업
        if player:
            try:
                if player.video:
                    player.video.stop()
                if player.audio:
                    player.audio.stop()
            except:
                pass

        if pc.connectionState != 'closed':
            await pc.close()

        await sio.disconnect()

if __name__ == "__main__":
    cam_id = sys.argv[1] if len(sys.argv) > 1 else "webcam1"
    cam_dev = sys.argv[2] if len(sys.argv) > 2 else "/dev/video0"
    asyncio.run(main(cam_id, cam_dev))