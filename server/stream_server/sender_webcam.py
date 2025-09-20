import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import ssl

sio = socketio.AsyncClient()
pc = RTCPeerConnection()

async def main():
    # sio = socketio.AsyncClient(engineio_options={
    #   'aiohttp_session_get_kwargs': {'ssl': False}
    # })
    sio = socketio.AsyncClient(ssl_verify=False)
    await sio.connect("http://100.65.221.86:3010")

    # join (sender 등록)
    await sio.emit("join", {"role": "sender", "camera_id": "cam2"})

    # 카메라 or 영상 파일 열기
    player = MediaPlayer("/dev/video0", format="v4l2",
                         options={"input_format":"mjpeg","video_size": "640x480", "framerate": "30"})  # Linux 카메라 장치
    if not player.video:
        print("/dev/video0 비디오 트랙을 열지 못했습니다.")
        return
    pc.addTrack(player.video)

    # offer 생성 후 signaling 서버로 전송
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    await sio.emit("offer", {"role": "sender", "sdp": offer.sdp, "type": offer.type})

    # 서버에서 answer 받기
    @sio.on("answer")
    async def on_answer(msg):
        await pc.setRemoteDescription(RTCSessionDescription(
            sdp=msg["sdp"], type=msg["type"]
        ))
        print("Sender connected!")

    await asyncio.sleep(3600)  # 1시간 동안 송출

asyncio.run(main())