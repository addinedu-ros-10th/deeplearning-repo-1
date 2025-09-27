import asyncio
from aiohttp import web
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

import ssl
import uuid
import time

import cv2

# --- 전역 상태 ---
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

pcs = set()  # 전체 PeerConnection 관리
pc_roles = {}  # pc 역할 관리 (sender/receiver)
pc_owners = {}  # pc 소유자(sid) 관리
relay = MediaRelay()

sender_tracks = {}
sender_sources = {}
pc_subs = {}
cameras = {}
receivers = {}

# --- 시그널링 이벤트 핸들러 ---
@sio.event
async def join(sid, data):
    role = data.get("role")

    if role == "sender":
        camera_id = data.get("camera_id")
        if not camera_id:
            await sio.emit("error", {"message": "camera_id required for sender"}, to=sid)
            return
        
        if camera_id in cameras:
            await teardown_camera(camera_id, reason="duplicate_sender")

        pc = RTCPeerConnection()
        cameras[camera_id] = {
            "sender_sid": sid,
            "sender_pc": pc,
            "orig_tracks": {"video":None, "audio":None},
            "subscribers": {}
        }

        @pc.on("iceconnectionstatechange")
        async def on_ice_state_change():
            st = pc.iceConnectionState
            print("[sender ice]", camera_id, st)
            if st in ("failed", "disconnected", "closed"):
                await teardown_camera(camera_id, reason=st)

        await sio.save_session(sid, {"role": "sender", "camera_id": camera_id})
        await sio.enter_room(sid, f"sender:{camera_id}")

        await sio.emit("joined", {"role": "sender", "camera_id": camera_id}, to=sid)

        @pc.on("track")
        def on_track(track):
            camera_id = camera_id_from_sid(sid)
            cam = cameras.get(camera_id)
            if not cam:
                return
            
            kind = track.kind
            print(f"[sender] {camera_id} new track kind={kind}")

            old = cam["orig_tracks"].get(kind)
            if old:
                try: old.stop()
                except: pass

            cam["orig_tracks"][kind] = track

            for rcv_sid, ent in cam["subscribers"].items():
                rcv_pc = ent["pc"]

                prev = ent["clones"].get(kind)
                if prev:
                    try: prev.stop()
                    except: pass

                clone = relay.subscribe(track)
                ent["clones"][kind] = clone
                rcv_pc.addTrack(clone)

            if kind == "video":
                asyncio.create_task(sio.emit("sender_added", {"camera_id": camera_id}, room="receivers"))

    elif role == "receiver":
        pc = RTCPeerConnection()
        receivers[sid] = {
            "pc": pc
        }
        
        @pc.on("iceconnectionstatechange")
        async def on_ice_state_change():
            st = pc.iceConnectionState
            print("[receiver ice]", sid, st)
            if st in ("failed", "disconnected", "closed"):
                await receiver_cleanup(sid)
        
        await sio.save_session(sid, {"role": "receiver"})
        await sio.enter_room(sid, "receivers")
        await sio.emit("joined", {"role": "receiver"}, to=sid)

@sio.event
async def start_receive(sid, data):
    info = receivers.get(sid)
    if not info:
        return
    rcv_pc = info["pc"]

    for camera_id, cam in cameras.items():
        sub = cam["subscribers"].setdefault(sid, {"pc": rcv_pc, "clones": {"video": None, "audio": None}})
        for kind in ("video", "audio"):
            orig = cam["orig_tracks"].get(kind)
            if orig:
                prev = sub["clones"].get(kind)
                if prev:
                    try: prev.stop()
                    except: pass
                clone = relay.subscribe(orig)
                sub["clones"][kind] = clone
                rcv_pc.addTrack(clone)
    
    await sio.emit("subscribed", {"ok": True}, to=sid)

@sio.event
async def offer(sid, data):
    role = data.get("role")
    sdp = data.get("sdp")
    type_ = data.get("type")

    pc = RTCPeerConnection()
    pcs.add(pc)
    pc_roles[pc] = role
    pc_owners[pc] = sid

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
                        sender_tracks.setdefault(camera_id, [])
                        sender_tracks[camera_id].append(relay.subscribe(track))
                        print(f"sender_tracks keys til now: {list(sender_tracks.keys())}")
                        d = sender_sources.setdefault(camera_id, {})
                        # print(f"track type : {type(track)}")
                        # print(f"track info: \n\t track vars : {vars(track)}\n\t track dir : {dir(track)}")
                        # print(f"relay.subscribe(track) type : {type(relay.subscribe(track))}")
                        # print(f"relay subscribe(track) id: {relay.subscribe(track).id}")
                        # print(f"sender sources id: {track.id}")
                        old = d.get(track.kind)
                        if old and hasattr(old, "stop"):
                            try: old.stop()
                            except: pass
                        d[track.kind] = track
                        print(f"sender_sources keys til now: {list(sender_sources.keys())}")
                        # print(f"sender_sources camera state : []")

                        for pc in list(pcs):
                            if pc_roles.get(pc) == "receiver":
                                owner_sid = pc_owners.get(pc)
                                if owner_sid:
                                    asyncio.create_task(sio.emit("need_offer", {"camera_id": camera_id}, room=owner_sid))
    # --- SDP 교환 ---
    offer = RTCSessionDescription(sdp=sdp, type=type_)
    await pc.setRemoteDescription(offer)

    if role == "receiver":
        # receiver → 모든 sender_tracks를 붙여줌
        for camera_id, tracks in sender_tracks.items():
            for track in tracks:
                    pc.addTrack(track)
                # print(f"track id in offer event: {track.id}")
        
        subs = []
        # for camera_id, kinds in sender_sources.items():
        #     for kind, orig in kinds.items():
        #         sub = relay.subscribe(orig)
        #         # pc.addTrack(sub)
        #         subs.append(sub)

        pc_subs[pc] = subs

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await sio.emit("answer", {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }, room=sid)

@sio.event
async def sender_left(sid, data):
    camera_id = data.get("camera_id")
    await teardown_camera(camera_id, reason="sender_left")

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
            # print(f"[disconnected sender] sender_tracks length: {len(sender_tracks.get(camera_id))}")
            # print(f"camera_id : {camera_id} and tracks : {sender_tracks.get(camera_id)[0].id}")
            # print(f"html_tag_check : {sender_sources.get(camera_id).get("video").id}")
            html_tag_id = sender_sources.get(camera_id).get("video").id
            for i in sender_tracks.pop(camera_id, []):
                try:
                    i.stop()
                except Exception:
                    pass
            # sender_tracks.pop(camera_id, None)
            sender_sources.pop(camera_id, None) # 9.18 추가
            await sio.emit("sender_removed", {"camera_id": html_tag_id}, room="receivers")
    
    to_cleanup = [pc for pc, owner in pc_owners.items() if owner == sid]
    for pc in to_cleanup:
        await cleanup_pc(pc)

async def cleanup_pc(pc: RTCPeerConnection):
    try:
        for t in pc_subs.pop(pc, []):
            try: t.stop()
            except: pass

        pcs.discard(pc)
        pc_roles.pop(pc, None)
        pc_owners.pop(pc, None)
        await pc.close()
    except Exception as e:
        print("[cleanup_pc] error:", e)

async def receiver_cleanup(sid: str):
    ent = receivers.pop(sid, None)
    if not ent:
        return
    pc = ent.get("pc")
    if pc:
        try: await pc.close()
        except: pass

    # 모든 camera의 subscribers에서 제거 + 해당 리시버에게 붙였던 클론 stop
    for cam in cameras.values():
        sub = cam["subscribers"].pop(sid, None)
        if sub:
            for k, tr in list(sub["clones"].items()):
                if tr:
                    try: tr.stop()
                    except: pass
            sub["clones"].clear()

async def teardown_camera(camera_id: str, reason: str = "replaced"):
    cam = cameras.get(camera_id)
    if not cam:
        return
    for rcv_sid, ent in list(cam["subscribers"].items()):
        clones = ent.get("clones", {})
        for k in list(clones.keys()):
            tr = clones[k]
            if tr:
                try:
                    tr.stop()
                except Exception:
                    pass
        ent["clones"].clear()

    for k in list(cam["orig_tracks"].keys()):
        tr = cam["orig_tracks"][k]
        if tr:
            try:
                tr.stop()
            except Exception:
                pass
        cam["orig_tracks"][k] = None

    spc = cam.get("pc")
    if spc:
        try:
            await spc.close()
        except Exception:
            pass
        cam["sender_pc"] = None

    await sio.emit("sender_removed", {"camera_id": camera_id, "reason": reason})

    cameras.pop(camera_id, None)

# --- 모니터링 엔드포인트 ---
async def metrics(request):
    body = {
        "pcs": len(pcs),
        "senders": len(sender_tracks),
        "cameras": list(sender_tracks.keys())
    }
    return web.json_response(body)

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
app.router.add_get("/metrics", metrics)
app.router.add_get("/receiver", mjpeg_receiver)

# --- 실행 ---
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=3010)
