import asyncio
import ssl
import uuid

from aiohttp import web
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

# --- 전역 변수 재구성 ---
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# 각 sid에 연결된 RTCPeerConnection 객체를 저장
pcs = set()
# 발신자(sender)들의 비디오/오디오 트랙을 저장
# 이 구조는 어떤 트랙이 어떤 발신자로부터 왔는지 명확히 합니다.
sender_tracks = {} # { "video": [track1, track2], "audio": [track1, ...] }

# --- 이벤트 핸들러 ---

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    # 연결이 끊긴 pc를 찾아서 정리
    pc_to_remove = None
    for pc in pcs:
        if pc._sid == sid:
            # 해당 pc가 sender였다면, 저장된 트랙들을 제거
            if hasattr(pc, '_is_sender') and pc._is_sender:
                print(f"Sender {sid} disconnected. Removing its tracks.")
                # kind별로 해당 pc의 트랙을 찾아서 제거
                for kind in sender_tracks:
                    sender_tracks[kind] = [t for t in sender_tracks[kind] if t._pc_id != pc._id]

            await pc.close()
            pc_to_remove = pc
            break
    if pc_to_remove:
        pcs.discard(pc_to_remove)

@sio.event
async def offer(sid, data):
    role = data.get("role", "receiver")
    offer_sdp = RTCSessionDescription(sdp=data["sdp"], type=data["type"])

    # --- RTCPeerConnection 설정 ---
    pc = RTCPeerConnection(
        configuration=RTCConfiguration(
            iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
        )
    )
    # pc 객체에 커스텀 속성을 추가하여 sid와 id를 저장
    pc._sid = sid
    pc._id = uuid.uuid4() # pc 객체를 구분하기 위한 고유 ID

    # 서버 -> 클라이언트 trickle ICE
    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            await sio.emit("candidate", candidate.to_dict(), to=sid)

    # --- 역할(role)에 따른 로직 분기 ---

    if role == "sender":
        print(f"Sender connected: {sid} (pc_id: {pc._id})")
        pc._is_sender = True

        @pc.on("track")
        async def on_track(track):
            print(f"Track {track.kind} (id: {track.id}) received from sender {sid}")
            # 트랙 객체에도 pc_id를 저장해두어 나중에 추적할 수 있게 함
            track._pc_id = pc._id
            # sender_tracks에 종류(kind)별로 트랙 추가
            if track.kind not in sender_tracks:
                sender_tracks[track.kind] = []
            sender_tracks[track.kind].append(track)

            # 중요: 새로운 트랙이 들어왔음을 모든 수신자(receiver)에게 알리고 트랙을 추가
            for receiver_pc in pcs:
                if hasattr(receiver_pc, '_is_receiver') and receiver_pc._is_receiver:
                    print(f"Adding new track {track.kind} from {sid} to receiver {receiver_pc._sid}")
                    receiver_pc.addTrack(track)

    else: # role == "receiver"
        print(f"Receiver connected: {sid}")
        pc._is_receiver = True
        # 현재까지 들어온 모든 sender의 트랙들을 이 수신자에게 추가
        for kind in sender_tracks:
            for track in sender_tracks[kind]:
                print(f"Adding existing track {track.kind} (from pc_id: {track._pc_id}) to new receiver {sid}")
                pc.addTrack(track)

    # 공통 로직: offer를 받고 answer를 생성하여 전송
    await pc.setRemoteDescription(offer_sdp)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await sio.emit("answer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}, to=sid)
    pcs.add(pc) # 처리 완료 후 전역 set에 추가
    print(f"Sent answer to {sid}. Total PCs: {len(pcs)}")


@sio.event
async def candidate(sid, data):
    # sid에 해당하는 pc를 찾아서 ICE candidate 추가
    for pc in pcs:
        if pc._sid == sid and data:
            try:
                cand = RTCSessionDescription(
                    sdp="a=" + data["candidate"],
                    type="candidate"
                ).sdp.splitlines()[0]
                
                # aiortc旧版本可能需要RTCIceCandidate对象
                from aiortc.sdp import candidate_from_sdp
                ice_cand = candidate_from_sdp(data["candidate"])
                ice_cand.sdpMid = data["sdpMid"]
                ice_cand.sdpMLineIndex = data["sdpMLineIndex"]

                await pc.addIceCandidate(ice_cand)
            except Exception as e:
                print(f"Error adding ICE candidate for {sid}: {e}")
            break

# --- HTML 서빙 ---

async def sender_page(request):
    with open("index-sender.html") as f:
        return web.Response(text=f.read(), content_type="text/html")

async def receiver_page(request):
    with open("index-receiver.html") as f:
        return web.Response(text=f.read(), content_type="text/html")

async def root(request):
    return web.Response(text="<a href='/sender'>sender</a> | <a href='/receiver'>receiver</a>", content_type="text/html")

app.router.add_get("/", root)
app.router.add_get("/sender", sender_page)
app.router.add_get("/receiver", receiver_page)

if __name__ == "__main__":
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    web.run_app(app, host="0.0.0.0", port=3000, ssl_context=ssl_context) # host를 0.0.0.0으로 변경하면 외부 접속이 용이합니다.