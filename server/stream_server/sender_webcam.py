import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import ssl
import signal
import sys

sio = socketio.AsyncClient()
pc = RTCPeerConnection()

async def cleanup(camera_id):
    print("Cleanup camera sender ...")
    await sio.emit("sender_left", {"role": "sender", "camera_id": camera_id})
    try:
        if sio.connected:
            await sio.disconnect()
        await pc.close()
    except Exception as e:
        print("cleanup error:", e)
        pass

async def main(camera_id):
    # sio = socketio.AsyncClient(engineio_options={
    #   'aiohttp_session_get_kwargs': {'ssl': False}
    # })
    sio = socketio.AsyncClient(ssl_verify=False)
    await sio.connect("http://100.65.221.86:3010")

    # join (sender 등록)
    await sio.emit("join", {"role": "sender", "camera_id": camera_id})

    # 카메라 or 영상 파일 열기
    player = MediaPlayer("/dev/video0", format="v4l2",
                        #  options={"framerate":"30","video_size":"1280x720"})
                         options={"input_format":"mjpeg","video_size": "640x480", "framerate": "30"})  # Linux 카메라 장치
    if not player.video:
        print(f"{camera_id} 화면을 열지 못했습니다.")
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

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await cleanup(camera_id)

if __name__ == "__main__":
    camera_id = sys.argv[1]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = loop.create_task(main(camera_id))

    async def _shutdown(task, cam):
        if not task.done():
            task.cancel()
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

        try:
            await cleanup(cam)
        except Exception:
            pass
        loop.stop()

    def _schedule_shutdown():
        try:
            asyncio.create_task(_shutdown(main_task, camera_id))
        except RuntimeError:
            pass

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _schedule_shutdown)
        except NotImplementedError:
            pass

    try:
        loop.run_forever()
    finally:
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass
        loop.close()