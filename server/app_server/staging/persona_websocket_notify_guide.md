# PersonA 팀 Deeplearning 노인공경 프로젝트
## WebSocket 기반 알림 시스템 가이드 (Nginx + FastAPI + Redis + PostgreSQL)

**작성일자**: 2025-09-18  
**작성자**: IT 총괄 정규호  
**버전**: v1.0  
**회사명**: ConAI  
**부서명**: IT  

---

## 1. 전체 구조
- 클라이언트(웹/웹앱 PWA) → `wss://notify.petple.ai/ws` 접속 (JWT 포함).
- FastAPI WebSocket 서버 → 인증 후 Redis Pub/Sub 구독 → 클라이언트로 fan-out.
- 백엔드 서비스는 “알림 생성 API” 호출 → PostgreSQL 기록 → Redis publish → WS 서버 전달 → 클라 `ack` 반영.

---

## 2. Nginx 설정

```nginx
upstream ws_backend {
    server app:8000;
    keepalive 64;
}

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    server_name notify.petple.ai;

    gzip on;
    gzip_types application/json text/event-stream application/javascript;

    location /ws {
        proxy_pass         http://ws_backend;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection $connection_upgrade;
        proxy_set_header   Host $host;
        proxy_read_timeout 75s;
        proxy_send_timeout 75s;
    }

    location /health {
        proxy_pass http://ws_backend/health;
    }
}
```

---

## 3. PostgreSQL 스키마

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE notification (
  notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         BIGINT NOT NULL,
  title           TEXT NOT NULL,
  body            TEXT NOT NULL,
  data_json       JSONB,
  priority        TEXT CHECK (priority IN ('HIGH','NORMAL','LOW')) NOT NULL DEFAULT 'NORMAL',
  topic           TEXT,
  created_at      timestamptz DEFAULT now(),
  status          TEXT DEFAULT 'QUEUED'
);

CREATE TABLE delivery_log (
  delivery_id     BIGSERIAL PRIMARY KEY,
  notification_id UUID REFERENCES notification(notification_id) ON DELETE CASCADE,
  user_id         BIGINT NOT NULL,
  channel         TEXT CHECK (channel IN ('websocket')) NOT NULL DEFAULT 'websocket',
  status          TEXT CHECK (status IN ('PUSHED','ACK','FAILED')) NOT NULL,
  attempts        INT DEFAULT 0,
  error_msg       TEXT,
  ts              timestamptz DEFAULT now()
);
```

---

## 4. FastAPI WebSocket 서버 예시

```python
import json, asyncio, aioredis
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
import jwt

app = FastAPI(title="PersonA Realtime Notify")

REDIS_URL = "redis://redis:6379/0"

class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        self.active.get(user_id, set()).discard(ws)

    async def send_user(self, user_id: int, payload: dict):
        for ws in list(self.active.get(user_id, set())):
            try:
                await ws.send_json(payload)
            except:
                self.disconnect(user_id, ws)

manager = ConnectionManager()

def verify_jwt(token: str) -> int:
    payload = jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
    return int(payload["sub"])

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    token = ws.query_params.get("token")
    user_id = verify_jwt(token)
    await manager.connect(user_id, ws)
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)
            if data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
            elif data.get("type") == "ack":
                pass
    except WebSocketDisconnect:
        manager.disconnect(user_id, ws)
```

---

## 5. 알림 생성 API

```python
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api")

class NotifyIn(BaseModel):
    user_id: int
    title: str
    body: str
    data_json: dict | None = None
    priority: str = "NORMAL"

@router.post("/notify")
async def create_notify(n: NotifyIn):
    payload = {
        "type": "notification",
        "user_id": n.user_id,
        "title": n.title,
        "body": n.body,
        "data": n.data_json,
        "ts": datetime.utcnow().isoformat() + "Z"
    }
    await app.state.redis.publish("notify.broadcast", json.dumps(payload))
    return {"ok": True}
```

---

## 6. 클라이언트 예시 (브라우저)

```javascript
const token = "<JWT>";
const ws = new WebSocket(`wss://notify.petple.ai/ws?token=${encodeURIComponent(token)}`);

ws.onopen = () => {
  setInterval(() => ws.send(JSON.stringify({type:"ping"})), 25000);
};

ws.onmessage = (evt) => {
  const msg = JSON.parse(evt.data);
  if (msg.type === "notification") {
    alert("알림: " + msg.title + " - " + msg.body);
    ws.send(JSON.stringify({type:"ack", notification_id: msg.notification_id}));
  }
};
```

---

## 7. 운영 체크리스트
- JWT 인증 → 핸드셰이크 시 검증.
- 리커넥트: 지수 백오프, 마지막 offset 복원.
- 메트릭: PUSHED/ACK 비율, 평균 지연.
- 보안: 민감정보 최소화.

---

## 8. 단계별 도입 로드맵
1. MVP: FastAPI WS + Redis Pub/Sub + Postgres 로그.
2. Outbox 패턴 → 안정적 전달 보장.
3. Redis Streams + Consumer Group → 확장.
4. Web Push(PWA) 추가 → 백그라운드 지원.
5. 토픽 브로드캐스트/역할별 알림 확장.

---

## 9. 예시 시나리오
- 낙상 감지 → WS 실시간 토스트 → 사용자 ACK → 로그 적재.
- 리포트 준비 완료 → WS 뱃지 갱신, 백그라운드 Web Push.
- 운영 경보 → 토픽 기반 브로드캐스트.

---

**결론**: 본 가이드라인은 PersonA 팀 Deeplearning 노인공경 프로젝트에서 앱/웹 공통 WebSocket 알림 체계를 구축하기 위한 기술적 기준을 제공합니다.
