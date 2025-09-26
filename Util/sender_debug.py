import sys
import cv2
import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import logging # 로깅 모듈 추가

# --- 로깅 설정 ---
LOG_FILE = "app_error.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
# -----------------

# SERVER_URL = "http://100.65.221.86:3010"  # 변경하세요
SERVER_URL = "http://192.168.0.129:3010"  # 변경하세요

async def main(camera_id: str, camera_dev:str):
    sio = socketio.AsyncClient()
    pc = RTCPeerConnection()
    
    # --- 주요 로직 시작 로그 ---
    logger.info(f"Attempting to connect to {SERVER_URL} with Camera ID: {camera_id}, Device: {camera_dev}")
    # ---------------------------

    @sio.event
    async def connect():
        logger.info("[sender] SocketIO connected.")
        await sio.emit("join", {"role": "sender", "camera_id": camera_id})

    @sio.event
    async def disconnect():
        # --- 소켓 연결 끊김 로그 ---
        logger.warning("[sender] SocketIO disconnected. Process might terminate soon.")
        # ---------------------------

    @sio.event
    async def joined(data):
        if data.get("role") != "sender":
            return
            
        logger.info("[sender] Successfully joined as sender. Initializing media player.")
        
        try:
            player = MediaPlayer(camera_dev) if sys.platform != "win32" else MediaPlayer(0)
            if player and player.video:
                pc.addTrack(player.video)
                logger.info("[sender] Video track added.")
            if player and player.audio:
                pc.addTrack(player.audio)
                logger.info("[sender] Audio track added.")
            
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            await sio.emit("offer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
            logger.info("[sender] WebRTC Offer sent.")

        except Exception as e:
            # --- 미디어 플레이어/WebRTC 관련 예외 로그 ---
            logger.error(f"[sender] Error during media initialization or offer: {e}", exc_info=True)
            # 예외 발생 시 프로그램 종료를 위해 여기서 종료 처리를 시도할 수 있습니다.
            # await sio.disconnect() 
            # raise # 에러를 올려서 프로세스를 종료시킬 수도 있습니다.
            # ---------------------------------------------

    @sio.event
    async def answer(data):
        await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
        logger.info("[sender] WebRTC connected successfully.")

    await sio.connect(SERVER_URL)
    # --- sio.wait()는 블로킹 지점입니다. 여기서 예외가 발생할 가능성이 높습니다. ---
    await sio.wait()
    # -------------------------------------------------------------------------


if __name__ == "__main__":
    cam_id = sys.argv[1] if len(sys.argv) > 1 else "webcam1"
    cam_dev = sys.argv[2] if len(sys.argv) > 2 else "/dev/video0"
    
    try:
        # --- 메인 함수 실행 ---
        asyncio.run(main(cam_id, cam_dev))
        # --- 프로그램 정상 종료 로그 ---
        logger.info("Program finished execution (clean exit).")
        # -----------------------------
        
    except KeyboardInterrupt:
        # --- Ctrl+C에 의한 종료 로그 ---
        logger.warning("Program interrupted by user (KeyboardInterrupt).")
        sys.exit(0)
        # -----------------------------
        
    except Exception as e:
        # --- 예상치 못한 프로그램 종료 로그 (가장 중요) ---
        logger.critical(f"UNEXPECTED FATAL ERROR: {e}", exc_info=True)
        # exc_info=True를 사용하면 Traceback이 로그 파일에 기록됩니다.
        # ---------------------------------------------------
        sys.exit(1) # 비정상 종료 코드 (1)를 반환하여 재시작 스크립트가 인식하도록 합니다.






