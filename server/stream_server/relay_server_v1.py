import asyncio
import ssl
import uuid
from aiohttp import web
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

import cv2

# --- 전역 상태 ---
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

pcs = set()  # 전체 PeerConnection 관리
relay = MediaRelay()

# sender_tracks: { camera_id: [track1, track2, ...] }
sender_tracks = {}

# 9.18 추가
sender_sources = {}
pc_subs = {}

# --- 시그널링 이벤트 핸들러 ---
@sio.event
async def join(sid, data):
    role = data.get("role")
    camera_id = data.get("camera_id", str(uuid.uuid4()))
    print(f"[join] sid={sid}, role={role}, camera_id={camera_id}")

    if role == "sender":
        # sender는 tracks를 저장할 준비만
        sender_tracks[camera_id] = []
        sender_tracks[camera_id] = [] # 9.18 추가
        await sio.enter_room(sid, f"sender:{camera_id}")

    elif role == "receiver":
        await sio.enter_room(sid, "receivers")

    return {"camera_id": camera_id}


@sio.event
async def offer(sid, data):
    role = data.get("role")
    sdp = data.get("sdp")
    type_ = data.get("type")

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_ice():
        print(f"[pc] ICE state={pc.iceConnectionState}")
        if pc.iceConnectionState in ("failed", "disconnected", "closed"):
            await cleanup_pc(pc)

    if role == "sender":
        # sender → 트랙을 받아서 relay에 등록
        @pc.on("track")
        def on_track(track):
            print(f"[sender] new track kind={track.kind}")
            if track.kind == "video" or track.kind == "audio":
                # camera_id는 join 때 부여한 방에서 꺼냄
                for room in sio.rooms(sid):
                    if room.startswith("sender:"):
                        camera_id = room.split(":", 1)[1]
                        sender_tracks[camera_id].append(relay.subscribe(track))
                        # sender_sources.setdefault(camera_id, []).append(track) # 9.18 추가
                        d = sender_sources.setdefault(camera_id, {})
                        old = d.get(track.kind)
                        if old and hasattr(old, "stop"):
                            try: old.stop()
                            except: pass
                        d[track.kind] = track
    # --- SDP 교환 ---
    offer = RTCSessionDescription(sdp=sdp, type=type_)
    await pc.setRemoteDescription(offer)

    if role == "receiver":
        # receiver → 모든 sender_tracks를 붙여줌
        for camera_id, tracks in sender_tracks.items():
            for track in tracks:
                pc.addTrack(track)
        
        subs = []
        for camera_id, kinds in sender_sources.items():
            for kind, orig in kinds.items():
                sub = relay.subscribe(orig)
                pc.addTrack(sub)
                subs.append(sub)

        pc_subs[pc] = subs

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await sio.emit("answer", {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }, room=sid)


@sio.event
async def candidate(sid, data):
    # ICE candidate는 aiortc에서 gather → browser로 전달
    # 브라우저→서버 candidate도 받을 수 있음 (여기선 생략 가능)
    pass


@sio.event
async def disconnect(sid):
    print(f"[disconnect] sid={sid}")
    # sender가 나간 경우 트랙 정리
    for room in list(sio.rooms(sid)):
        if room.startswith("sender:"):
            camera_id = room.split(":", 1)[1]
            sender_tracks.pop(camera_id, None)
            sender_sources.pop(camera_id, None) # 9.18 추가


async def cleanup_pc(pc: RTCPeerConnection):
    try:
        for t in pc_subs.pop(pc, []):
            try: t.stop()
            except: pass

        pcs.discard(pc)
        await pc.close()
    except Exception as e:
        print("[cleanup_pc] error:", e)


# --- 모니터링 엔드포인트 ---
async def metrics(request):
    body = {
        "pcs": len(pcs),
        "senders": len(sender_tracks),
        "cameras": list(sender_tracks.keys())
    }
    return web.json_response(body)


app.router.add_get("/metrics", metrics)

# BOUNDARY = "frame"

# async def mjpeg_receiver(request: web.Request):
#     """
#     GET /receiver?camera_id=cam2
#     → multipart/x-mixed-replace로 MJPEG 스트림 전송
#     """
#     camera_id = request.query.get("camera_id")
#     if not camera_id:
#         return web.Response(text="camera_id query required", status=400)

#     # 해당 카메라의 '원본' 비디오 트랙을 찾음
#     sources = sender_sources.get(camera_id) or []
#     vsrc = next((t for t in sources if getattr(t, "kind", "") == "video"), None)
#     if not vsrc:
#         return web.Response(text=f"no video track for camera_id={camera_id}", status=404)

#     # 각 클라이언트마다 새 릴레이 구독(track)을 만들어줌
#     local_track = relay.subscribe(vsrc)

#     resp = web.StreamResponse(
#         status=200,
#         headers={
#             "Cache-Control": "no-cache, no-store, must-revalidate",
#             "Pragma": "no-cache",
#             "Connection": "close",
#             "Content-Type": f"multipart/x-mixed-replace; boundary={BOUNDARY}",
#         },
#     )
#     await resp.prepare(request)

#     try:
#         while True:
#             frame = await local_track.recv()                     # aiortc VideoFrame
#             img = frame.to_ndarray(format="bgr24")               # → numpy BGR
#             ok, jpg = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
#             if not ok:
#                 continue
#             data = jpg.tobytes()

#             # multipart 파트 작성
#             await resp.write(b"--" + BOUNDARY.encode() + b"\r\n")
#             await resp.write(b"Content-Type: image/jpeg\r\n")
#             await resp.write(b"Content-Length: " + str(len(data)).encode() + b"\r\n\r\n")
#             await resp.write(data + b"\r\n")

#             # 너무 빡세게 돌지 않게 살짝 양보 (원하면 FPS 제한 로직으로 교체)
#             await asyncio.sleep(0.001)

#     except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
#         pass
#     finally:
#         try: local_track.stop()
#         except: pass
#         try:
#             await resp.write_eof()
#         except Exception:
#             pass
#     return resp
# 상단
import time
# import cv2

BOUNDARY = "frame"

async def mjpeg_receiver(request):
    camera_id = request.query.get("camera_id")
    if not camera_id:
        return web.Response(text="camera_id query required", status=400)

    kinds = sender_sources.get(camera_id) or {}
    vsrc = kinds.get("video")
    if not vsrc:
        return web.Response(text=f"no video track for camera_id={camera_id}", status=404)

    local_track = relay.subscribe(vsrc)

    resp = web.StreamResponse(
        status=200,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Connection": "close",
            "Content-Type": f"multipart/x-mixed-replace; boundary=%s" % BOUNDARY,
        },
    )
    await resp.prepare(request)

    target_fps = 15
    min_interval = 1.0 / target_fps
    next_t = time.perf_counter()

    try:
        while True:
            frame = await local_track.recv()  # aiortc VideoFrame

            now = time.perf_counter()
            if now < next_t:
                # 소비 속도가 느릴 때는 프레임 건너뜀 (메모리/CPU 보호)
                continue
            next_t = now + min_interval

            img = frame.to_ndarray(format="bgr24")
            ok, jpg = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if not ok:
                continue
            data = jpg.tobytes()

            await resp.write(b"--" + BOUNDARY.encode() + b"\r\n")
            await resp.write(b"Content-Type: image/jpeg\r\n")
            await resp.write(b"Content-Length: " + str(len(data)).encode() + b"\r\n\r\n")
            await resp.write(data + b"\r\n")
            # 🔽 소켓 쓰기 버퍼가 가득 차면 여기서 멈춰서 backpressure 적용
            await resp.drain()

            # 🔽 C-extension 할당 객체 레퍼런스 즉시 해제 (파편화 완화)
            del data, jpg, img, frame
    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        try:
            local_track.stop()   # ✅ 구독 트랙 종료 (중요)
        except Exception:
            pass
        try:
            await resp.write_eof()
        except Exception:
            pass
    return resp


# 라우터 등록
app.router.add_get("/receiver", mjpeg_receiver)

# --- 실행 ---
if __name__ == "__main__":
    # ssl_context = None
    # try:
    #   ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #   ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    # except Exception:
    #     print("⚠️ SSL 인증서 없음 → HTTP 모드로 실행")

    # web.run_app(app, host="0.0.0.0", port=3010, ssl_context=ssl_context)
    web.run_app(app, host="0.0.0.0", port=3010)
