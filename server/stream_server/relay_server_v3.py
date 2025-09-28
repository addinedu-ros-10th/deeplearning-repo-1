import argparse
import asyncio
import time
import cv2
from aiohttp import web
import socketio

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

relay = MediaRelay()

cameras = {}      # camera_id -> {"sender_sid", "sender_pc", "orig_tracks": {video, audio}, "subscribers": {...}}
receivers = {}    # sid -> {"pc": RTCPeerConnection}

pcs = set()
pc_roles = {}
pc_owners = {}
pc_subs = {}  # pc -> dict[(camera_id, kind)] = relay.clone track

async def receiver_cleanup(sid: str):
    print(f"[cleanup] 수신자 정리 시작: {sid}")

    ent = receivers.pop(sid, None)

    # 모든 카메라에서 이 수신자의 구독 정리
    for cam in cameras.values():
        sub = cam["subscribers"].pop(sid, None)
        if sub:
            for tr in list(sub.get("clones", {}).values()):
                try:
                    if hasattr(tr, 'stop'):
                        tr.stop()
                except Exception as e:
                    print(f"[cleanup] 구독 트랙 정지 실패: {e}")
            sub["clones"].clear()

    # 이 수신자의 PeerConnection 찾기 및 정리
    pc = None
    for _pc, owner in list(pc_owners.items()):
        if owner == sid:
            pc = _pc
            break

    if pc:
        # pc_subs에서 관련 트랙들 정리
        subs = pc_subs.pop(pc, {})
        for tr in list(subs.values()):
            try:
                if hasattr(tr, 'stop'):
                    tr.stop()
            except Exception as e:
                print(f"[cleanup] PC 트랙 정지 실패: {e}")

        # PeerConnection 닫기
        try:
            if hasattr(pc, 'close') and pc.connectionState != 'closed':
                await pc.close()
        except Exception as e:
            print(f"[cleanup] PC 닫기 실패: {e}")

        # 관련 데이터 정리
        pcs.discard(pc)
        pc_roles.pop(pc, None)
        pc_owners.pop(pc, None)

    print(f"[cleanup] 수신자 정리 완료: {sid}")

async def delayed_teardown(camera_id: str, reason: str):
    """딜레이를 두고 카메라 정리 작업 수행"""
    await asyncio.sleep(0.5)  # 500ms 딜레이
    await teardown_camera(camera_id, reason)

async def delayed_receiver_cleanup(sid: str):
    """딜레이를 두고 수신자 정리 작업 수행"""
    await asyncio.sleep(0.5)  # 500ms 딜레이
    await receiver_cleanup(sid)

async def teardown_camera(camera_id: str, reason: str = "replaced"):
    cam = cameras.get(camera_id)
    if not cam:
        return

    print(f"[teardown] 카메라 정리 시작: {camera_id} (이유: {reason})")

    # 구독자들의 클론 트랙 정리
    for rcv_sid, ent in list(cam["subscribers"].items()):
        clones = ent.get("clones", {})
        for k, tr in list(clones.items()):
            try:
                if hasattr(tr, 'stop'):
                    tr.stop()
            except Exception as e:
                print(f"[teardown] 클론 트랙 정지 실패: {e}")
            clones.pop(k, None)
        cam["subscribers"].pop(rcv_sid, None)

    # 원본 트랙 정리
    for kind, tr in list(cam["orig_tracks"].items()):
        if tr:
            try:
                if hasattr(tr, 'stop'):
                    tr.stop()
            except Exception as e:
                print(f"[teardown] 원본 트랙 정지 실패: {e}")
        cam["orig_tracks"][kind] = None

    # PeerConnection 정리
    spc = cam.get("sender_pc")
    if spc:
        try:
            if hasattr(spc, 'close') and spc.connectionState != 'closed':
                await spc.close()
            pcs.discard(spc)
            pc_roles.pop(spc, None)
            pc_owners.pop(spc, None)
        except Exception as e:
            print(f"[teardown] PC 닫기 실패: {e}")

    cameras.pop(camera_id, None)

    try:
        await sio.emit("sender_removed", {"camera_id": camera_id, "reason": reason}, room="receivers")
    except Exception as e:
        print(f"[teardown] 이벤트 전송 실패: {e}")

    print(f"[teardown] 카메라 정리 완료: {camera_id}")

async def attach_current_cameras_to_receiver(receiver_sid: str):
    info = receivers.get(receiver_sid)
    if not info:
        return
    rcv_pc = info["pc"]

    # PeerConnection 상태 확인
    if rcv_pc.connectionState in ('closed', 'failed'):
        print(f"[attach] 수신자 PC 상태가 불량함: {receiver_sid} -> {rcv_pc.connectionState}")
        return

    subs = pc_subs.setdefault(rcv_pc, {})

    for camera_id, cam in cameras.items():
        try:
            for kind in ("video", "audio"):
                orig = cam["orig_tracks"].get(kind)
                if not orig:
                    continue
                key = (camera_id, kind)
                if key in subs:
                    continue

                # 릴레이 구독 시 예외 처리
                try:
                    sub_track = relay.subscribe(orig)
                    subs[key] = sub_track

                    # 트랙 추가 시 트랜시버 찾기
                    available_transceiver = None
                    for transceiver in rcv_pc.getTransceivers():
                        if (transceiver.receiver.track is None and
                            transceiver.direction == "recvonly" and
                            transceiver.mid is None):
                            available_transceiver = transceiver
                            break

                    if available_transceiver:
                        # 기존 트랜시버 재사용
                        available_transceiver.sender.replaceTrack(sub_track)
                    else:
                        # 새 트랜시버 생성
                        rcv_pc.addTrack(sub_track)

                except Exception as e:
                    print(f"[attach] 트랙 구독 실패 {camera_id}.{kind}: {e}")
                    continue

            cam["subscribers"].setdefault(receiver_sid, {"pc": rcv_pc, "clones": {}})
            cam["subscribers"][receiver_sid]["clones"] = {
                k: v for k, v in pc_subs[rcv_pc].items() if k[0] == camera_id
            }
        except Exception as e:
            print(f"[attach] 카메라 연결 실패 {camera_id}: {e}")
            continue

@sio.event
async def connect(sid, environ):
    await sio.emit("connected", {"sid": sid}, to=sid)

@sio.event
async def join(sid, data):
    role = (data or {}).get("role")

    if role == "sender":
        camera_id = (data or {}).get("camera_id")
        if not camera_id:
            await sio.emit("error", {"msg": "camera_id required"}, to=sid)
            return

        if camera_id in cameras:
            await teardown_camera(camera_id, reason="duplicate_sender")

        pc = RTCPeerConnection()
        pcs.add(pc)
        pc_roles[pc] = "sender"
        pc_owners[pc] = sid

        cameras[camera_id] = {
            "sender_sid": sid,
            "sender_pc": pc,
            "orig_tracks": {"video": None, "audio": None},
            "subscribers": {}
        }

        @pc.on("iceconnectionstatechange")
        async def on_ice_state_change():
            st = pc.iceConnectionState
            print(f"[sender ice] {camera_id} -> {st}")
            if st in ("failed", "disconnected", "closed"):
                # 약간의 딜레이를 두고 정리 작업 수행
                asyncio.create_task(delayed_teardown(camera_id, st))

        @pc.on("track")
        def on_track(track: MediaStreamTrack):
            kind = track.kind
            print(f"[sender {camera_id}] new track kind={kind}")
            cam = cameras.get(camera_id)
            if not cam:
                return

            old = cam["orig_tracks"].get(kind)
            if old:
                try: old.stop()
                except: pass
            cam["orig_tracks"][kind] = track

            for rcv_sid, ent in cam["subscribers"].items():
                rcv_pc = ent.get("pc")
                if not rcv_pc:
                    continue
                prev_key = (camera_id, kind)
                prev = pc_subs.setdefault(rcv_pc, {}).pop(prev_key, None)
                if prev:
                    try: prev.stop()
                    except: pass
                clone = relay.subscribe(track)
                pc_subs[rcv_pc][prev_key] = clone
                rcv_pc.addTrack(clone)

            if kind == "video":
                asyncio.create_task(sio.emit("need_offer", {"camera_id": camera_id}, room="receivers"))

        await sio.save_session(sid, {"role": "sender", "camera_id": camera_id})
        await sio.enter_room(sid, f"sender:{camera_id}")
        await sio.emit("joined", {"role": "sender", "camera_id": camera_id}, to=sid)

    elif role == "receiver":
        pc = RTCPeerConnection()
        pcs.add(pc)
        pc_roles[pc] = "receiver"
        pc_owners[pc] = sid
        receivers[sid] = {"pc": pc}

        # 트랜시버 미리 생성 (다중 스트림 수신용)
        for i in range(8):
            video_transceiver = pc.addTransceiver("video", direction="recvonly")
            audio_transceiver = pc.addTransceiver("audio", direction="recvonly")
            # 방향 명시적 설정
            video_transceiver._offerDirection = "recvonly"
            audio_transceiver._offerDirection = "recvonly"

        @pc.on("iceconnectionstatechange")
        async def on_ice_state_change():
            st = pc.iceConnectionState
            print(f"[receiver ice] {sid} -> {st}")
            if st in ("failed", "disconnected", "closed"):
                # 약간의 딜레이를 두고 정리 작업 수행
                asyncio.create_task(delayed_receiver_cleanup(sid))

        await sio.save_session(sid, {"role": "receiver"})
        await sio.enter_room(sid, "receivers")
        await sio.emit("joined", {"role": "receiver"}, to=sid)
        await sio.emit("active_cameras", {"cameras": list(cameras.keys())}, to=sid)
        await attach_current_cameras_to_receiver(sid)

    else:
        await sio.emit("error", {"msg": "unknown role"}, to=sid)

@sio.event
async def offer(sid, data):
    try:
        sdp = data.get("sdp")
        type_ = data.get("type")
        if not sdp or not type_:
            await sio.emit("error", {"msg": "invalid offer"}, to=sid)
            return

        session = await sio.get_session(sid)
        role = session.get("role")
        pc = None
        for _pc, owner in pc_owners.items():
            if owner == sid:
                pc = _pc
                break
        if not pc:
            await sio.emit("error", {"msg": "pc not found for sid"}, to=sid)
            return

        # PeerConnection 상태 확인
        if pc.connectionState == 'closed':
            print(f"[offer] PC가 이미 닫힌 상태: {sid}")
            return

        await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=type_))
        if role == "receiver":
            await attach_current_cameras_to_receiver(sid)

        # 트랜시버 방향 검증 및 수정
        for transceiver in pc.getTransceivers():
            if transceiver._offerDirection is None:
                transceiver._offerDirection = transceiver.direction or "recvonly"
                print(f"[offer] 트랜시버 방향 수정: {transceiver._offerDirection}")

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        await sio.emit("answer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}, to=sid)

    except Exception as e:
        print(f"[offer] 오퍼 처리 중 오류: {e}")
        await sio.emit("error", {"msg": f"offer processing failed: {str(e)}"}, to=sid)

@sio.event
async def disconnect(sid):
    session = None
    try:
        session = await sio.get_session(sid)
    except Exception:
        pass
    role = (session or {}).get("role")
    if role == "sender":
        camera_id = (session or {}).get("camera_id")
        if camera_id:
            await teardown_camera(camera_id, reason="sender_disconnect")
    elif role == "receiver":
        await receiver_cleanup(sid)

# -------------------------------
# Monitoring & MJPEG receiver
# -------------------------------
BOUNDARY = "frame"
BOUNDARY_LINE = f"--{BOUNDARY}\r\n".encode()

async def metrics(request):
    body = {
        "pcs": len(pcs),
        "receivers": len(receivers),
        "cameras": list(cameras.keys()),
        "senders": len(cameras),
    }
    return web.json_response(body)

async def mjpeg_receiver(request):
    camera_id = request.query.get("camera_id")
    if not camera_id:
        return web.Response(text="camera_id query required", status=400)

    cam = cameras.get(camera_id)
    if not cam:
        return web.Response(text=f"unknown camera_id={camera_id}", status=404)

    vsrc = cam["orig_tracks"].get("video")
    if not vsrc:
        return web.Response(text=f"no video track for camera_id={camera_id}", status=404)

    local_track = relay.subscribe(vsrc)

    resp = web.StreamResponse(
        status=200,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Connection": "close",
            # ✅ FFmpeg가 좋아하는 형태: boundary=frame (따옴표 없이)
            "Content-Type": f"multipart/x-mixed-replace; boundary={BOUNDARY}",
        },
    )
    await resp.prepare(request)

    # ✅ 프리엠블 없이 바로 첫 boundary 라인부터 시작
    await resp.write(BOUNDARY_LINE)

    target_fps = 15
    min_interval = 1.0 / target_fps
    next_t = time.perf_counter()

    try:
        while True:
            frame = await local_track.recv()
            now = time.perf_counter()
            if now < next_t:
                continue
            next_t = now + min_interval

            img = frame.to_ndarray(format="bgr24")
            ok, jpg = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if not ok:
                continue
            data = jpg.tobytes()

            # 파트 헤더(끝에 \r\n으로 닫음)
            await resp.write(b"Content-Type: image/jpeg\r\n")
            await resp.write(b"Content-Length: " + str(len(data)).encode() + b"\r\n\r\n")
            await resp.write(data + b"\r\n")

            # 다음 파트를 위한 경계 (앞에 \r\n 없이 바로)
            await resp.write(BOUNDARY_LINE)

            await resp.drain()

            del data, jpg, img, frame

    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        try:
            local_track.stop()
        except Exception:
            pass
        # ✅ 종료 경계 (선택적이지만 깔끔)
        try:
            await resp.write(f"--{BOUNDARY}--\r\n".encode())
        except Exception:
            pass
        # write_eof()는 생략(FFmpeg 일부에서 경계 해석 꼬임 방지)
    return resp


# Routes
async def health(request):
    return web.json_response({"ok": True, "cameras": list(cameras.keys()), "receivers": len(receivers)})

app.router.add_get("/health", health)
app.router.add_get("/metrics", metrics)
app.router.add_get("/receiver", mjpeg_receiver)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=3010)
    args = parser.parse_args()
    web.run_app(app, host=args.host, port=args.port)