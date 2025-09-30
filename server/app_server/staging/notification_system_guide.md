# 알림 기능 개발 종합 가이드 (Hexagonal Architecture 기반)
**버전:** 2025-09-30 16:30  
**대상:** FastAPI + PostgreSQL (async SQLAlchemy) + WebSocket  
**핵심 테이블:** `notify.notify_message`, `notify.notify_delivery`, `notify.notify_device`

## 🚀 최신 업데이트 (2025-09-30)

### ✅ 해결된 문제들
1. **긴급 알림 다이얼로그 BuildContext 오류 해결**
   - `EmergencyNotificationService.showEmergencyAlert`에 `context.mounted` 검사 추가
   - `NotificationProvider`에 context 유효성 검사 강화

2. **서버 WebSocket payload 개선**
   - `notify_queue_use_cases.py`에서 `kind`, `severity`, `message_id`, `created_at` 필드 추가
   - WebSocket 전송 시 완전한 알림 데이터 포함

3. **Flutter 앱 알림 파싱 로직 개선**
   - `NotificationMessage.fromJson`에서 중첩된 `data` 객체에서 `kind`/`severity` 추출
   - 기본값을 `info`/`green`으로 변경 (더 안전한 기본값)

4. **HTML 클라이언트 개선**
   - `notification_client.js`에서 `kind`/`severity` 파싱 로직 강화
   - `notification_client.html`에서 severity별 색상 구분 및 자동 제거 시간 조정

### 🔧 수정된 파일들
- `server/app_server/app/application/use_cases/notify_queue_use_cases.py`
- `app/user_app/lib/features/notification/services/emergency_notification_service.dart`
- `app/user_app/lib/features/notification/state/notification_provider.dart`
- `app/user_app/lib/features/notification/models/notification_models.dart`
- `Util/notification/client/notification_client.js`
- `Util/notification/client/notification_client.html`

---
## 0. 문서 목적
실서비스 수준의 **알림 시스템**을 빠르게 구축·확장할 수 있도록, 최소 스키마 3종을 기반으로
- DB 연결
- 헥사고날 아키텍처(Ports & Adapters)
- 의존성 주입(DI), 의존성 역전(DIP)
- 전송 파이프라인(큐잉 → 전송 → 콜백 → 상태 갱신)
- 운영/배포 체크리스트

까지 **코드·설계·운영**을 통합 가이드합니다.

> 본 문서는 첨부된 환경 문서들을 참고하여 작성되었습니다. 각 섹션 끝의 “환경 노트”에 관련 파일 요약을 병기합니다.

## 1. 핵심 개념 요약
- `notify_message` : **무엇을 보낼지** (콘텐츠/유효기간/위험도)
- `notify_delivery` : **누구에게 어떻게 갔는지** (수신자×채널 상태)
- `notify_device` : **어디로 보낼지** (사용자별 실제 엔드포인트)

### 시퀀스(웹소켓 기준)
1) 운영자/시스템이 메시지 생성 → `notify_message` INSERT  
2) 대상 사용자·채널로 큐잉 → `notify_delivery(status=queued)` INSERT  
3) 전송 워커가 `queued`를 집어 WebSocket 브로드캐스트 → `sent/delivered` 타임스탬프 갱신  
4) 클라이언트가 열람/확인 시 콜백 → `read_at`/`ack_at` & `status` 갱신

## 2. 헥사고날 아키텍처 설계
### 도메인 (Entities + UseCases)
- **Entity**: Message, Delivery, Device (단순 데이터 모델)
- **UseCase(서비스)**:
  - `CreateMessageAndQueue`: 메시지 생성 + 대상별 큐잉
  - `MarkRead` / `MarkAck`: 열람/확인 처리
  - `DispatchQueued`: 전송 워커(큐 → 채널 어댑터)

### 포트(Ports)
- **Inbound Ports**: REST/WebSocket API 인터페이스 (입력)
- **Outbound Ports**: Repository(메시지/딜리버리/디바이스), Notifier(채널 전송), Clock(시간), IdGenerator 등

### 어댑터(Adapters)
- **Inbound Adapters**: FastAPI 라우터, WebSocket 엔드포인트
- **Outbound Adapters**: PostgreSQL Repository(Async SQLAlchemy), WebSocket ConnectionManager, (선택) Redis/Kafka 등

> DIP: UseCase는 Port 인터페이스에만 의존. 실제 구현(SQL/WS/Redis)은 어댑터에서 주입합니다.

## 3. 의존성 주입(수동 DI 예시)
애플리케이션 시작 시점에 Repository, Notifier, ConnectionManager 등을 **구성 루트**에서 생성하여 UseCase에 주입합니다.
프레임워크 코드는 도메인 코드를 모르게 유지합니다.

```python
# app/container.py (간단 수동 DI 예시, 한국어 주석)
from adapters.postgres_repo import MessageRepoPg, DeliveryRepoPg, DeviceRepoPg
from adapters.websocket_notify import WsNotifier, ConnectionManager
from services.usecases import CreateMessageAndQueue, MarkRead, MarkAck, DispatchQueued

class Container:
    def __init__(self, db_session_factory):
        self.msg_repo = MessageRepoPg(db_session_factory)
        self.deliv_repo = DeliveryRepoPg(db_session_factory)
        self.device_repo = DeviceRepoPg(db_session_factory)
        self.conn_manager = ConnectionManager()
        self.notifier = WsNotifier(self.conn_manager)  # 채널별로 어댑터 추가 가능
        # UseCases
        self.create_and_queue = CreateMessageAndQueue(self.msg_repo, self.deliv_repo, self.device_repo)
        self.mark_read = MarkRead(self.deliv_repo)
        self.mark_ack  = MarkAck(self.deliv_repo)
        self.dispatch_queued = DispatchQueued(self.deliv_repo, self.notifier)
```

## 4. 데이터베이스(Async SQLAlchemy) 연결
환경변수: `DATABASE_URL` (예: `postgresql+asyncpg://user:pass@host:5432/db`)

```python
# app/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def make_session_factory(dsn: str):
    engine = create_async_engine(dsn, echo=False, pool_size=5, max_overflow=10)
    return async_sessionmaker(engine, expire_on_commit=False)
```
**환경 노트:** `env_variables_guide.md` 에 정의된 DB, JWT, 이메일 등 환경변수를 그대로 활용하세요.

## 5. 리포지토리(Ports→Adapters) 구현 스케치
도메인은 Port(프로토콜)에 의존하고, 구현은 Adapters에서 제공합니다.

```python
# domain/ports.py
from typing import Protocol, Sequence
from uuid import UUID

class MessageRepo(Protocol):
    async def create_message(self, kind: str, severity: str, title: str|None, body: str|None, data: dict|None, expires_at) -> UUID: ...
    async def get(self, message_id: UUID) -> dict: ...

class DeliveryRepo(Protocol):
    async def queue_to_users(self, message_id: UUID, user_ids: Sequence[UUID], channel: str, payload: dict) -> int: ...
    async def next_queued(self, limit: int = 100) -> list[dict]: ...
    async def mark_sent(self, delivery_id: int): ...
    async def mark_delivered(self, delivery_id: int): ...
    async def mark_read(self, delivery_id: int): ...
    async def mark_ack(self, delivery_id: int): ...

class DeviceRepo(Protocol):
    async def list_active_endpoints(self, user_id: UUID, channel: str) -> list[str]: ...
```

```python
# adapters/postgres_repo.py  (핵심 SQL, 한국어 주석 포함)
from sqlalchemy import text

class MessageRepoPg:
    def __init__(self, factory): self.factory = factory
    async def create_message(self, kind, severity, title, body, data, expires_at):
        async with self.factory() as db:
            row = await db.execute(text(
                "INSERT INTO notify.notify_message(kind,severity,title,body,data,expires_at) "
                "VALUES (:k,:s,:t,:b,:d,:e) RETURNING message_id"
            ), {"k":kind,"s":severity,"t":title,"b":body,"d":data,"e":expires_at})
            mid = row.scalar_one()
            await db.commit()
            return mid

class DeliveryRepoPg:
    def __init__(self, factory): self.factory = factory
    async def queue_to_users(self, message_id, user_ids, channel, payload):
        q = (
            "INSERT INTO notify.notify_delivery (message_id,user_id,channel,status,payload) "
            "VALUES (:m,:u,:c,'queued',:p) ON CONFLICT (message_id,user_id,channel) DO NOTHING"
        )
        async with self.factory() as db:
            total = 0
            for u in user_ids:
                await db.execute(text(q), {"m":message_id,"u":str(u),"c":channel,"p":payload})
                total += 1
            await db.commit()
            return total
    async def next_queued(self, limit=100):
        async with self.factory() as db:
            rows = await db.execute(text(
                "SELECT d.delivery_id,d.user_id,d.channel,d.payload "
                "FROM notify.notify_delivery d "
                "JOIN notify.notify_message m ON m.message_id=d.message_id "
                "WHERE d.status='queued' AND (m.expires_at IS NULL OR NOW() <= m.expires_at) "
                "ORDER BY d.created_at ASC LIMIT :lim"
            ), {"lim":limit})
            return [dict(r) for r in rows.mappings().all()]
    async def mark_sent(self, did):
        async with self.factory() as db:
            await db.execute(text("UPDATE notify.notify_delivery SET status='sent', send_at=NOW() WHERE delivery_id=:d"), {"d":did}); await db.commit()
    async def mark_delivered(self, did):
        async with self.factory() as db:
            await db.execute(text("UPDATE notify.notify_delivery SET status='delivered', delivered_at=NOW() WHERE delivery_id=:d"), {"d":did}); await db.commit()
    async def mark_read(self, did):
        async with self.factory() as db:
            await db.execute(text("UPDATE notify.notify_delivery SET status='read', read_at=NOW() WHERE delivery_id=:d"), {"d":did}); await db.commit()
    async def mark_ack(self, did):
        async with self.factory() as db:
            await db.execute(text("UPDATE notify.notify_delivery SET status='ack', ack_at=NOW() WHERE delivery_id=:d"), {"d":did}); await db.commit()

class DeviceRepoPg:
    def __init__(self, factory): self.factory = factory
    async def list_active_endpoints(self, user_id, channel):
        async with self.factory() as db:
            rows = await db.execute(text(
                "SELECT endpoint FROM notify.notify_device "
                "WHERE user_id=:u AND channel=:c AND is_active=TRUE"
            ), {"u":str(user_id), "c":channel})
            return [r[0] for r in rows.fetchall()]
```
## 6. 채널 어댑터: WebSocket
### Connection Manager
```python
# adapters/websocket_notify.py
from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # user_id → set of WebSocket
        self.active: dict[str,set[WebSocket]] = defaultdict(set)
    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active[user_id].add(ws)
    def disconnect(self, user_id: str, ws: WebSocket):
        self.active[user_id].discard(ws)
    async def send_user(self, user_id: str, payload: dict):
        for ws in list(self.active.get(user_id, [])):
            try: await ws.send_json(payload)
            except Exception: self.disconnect(user_id, ws)

class WsNotifier:
    """채널 포트 구현체: user_id별 WS 브로드캐스트"""
    def __init__(self, manager: ConnectionManager): self.m = manager
    async def notify(self, delivery: dict):
        # delivery: {delivery_id, user_id, channel, payload}
        await self.m.send_user(str(delivery["user_id"]), delivery["payload"] or {})
```

### WebSocket Endpoint
```python
# app/api_ws.py
from fastapi import APIRouter, WebSocket, Depends, Query
from app.container import Container

router = APIRouter()

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, user_id: str = Query(...), container: Container = Depends()):
    await container.conn_manager.connect(user_id, ws)
    try:
        while True:
            await ws.receive_text()  # 핑/클라이언트 메시지 처리(옵션)
    except Exception:
        pass
    finally:
        container.conn_manager.disconnect(user_id, ws)
```
**환경 노트:** `persona_websocket_notify_guide.md` 의 프런트-엔드 연결 규칙/토큰 처리 가이드를 반영하세요. Nginx 업그레이드 헤더는 아래 참고.

## 7. 유스케이스 구현
```python
# services/usecases.py
from uuid import UUID
from typing import Sequence

class CreateMessageAndQueue:
    """메시지 생성 + 수신자×채널 큐잉"""
    def __init__(self, msg_repo, deliv_repo, device_repo):
        self.msg_repo, self.deliv_repo, self.device_repo = msg_repo, deliv_repo, device_repo
    async def __call__(self, *, kind: str, severity: str, title: str|None, body: str|None,
                       data: dict|None, expires_at, recipients: Sequence[UUID], channel: str) -> UUID:
        mid = await self.msg_repo.create_message(kind, severity, title, body, data, expires_at)
        # payload는 채널별 렌더링 결과(간단히 title/body 스냅샷)
        payload = {"title": title, "body": body, "data": data}
        await self.deliv_repo.queue_to_users(mid, recipients, channel, payload)
        return mid

class MarkRead:
    def __init__(self, deliv_repo): self.r = deliv_repo
    async def __call__(self, delivery_id: int): await self.r.mark_read(delivery_id)

class MarkAck:
    def __init__(self, deliv_repo): self.r = deliv_repo
    async def __call__(self, delivery_id: int): await self.r.mark_ack(delivery_id)

class DispatchQueued:
    """큐에 쌓인 전송건을 채널 어댑터를 통해 실제 전송"""
    def __init__(self, deliv_repo, notifier): self.r, self.n = deliv_repo, notifier
    async def __call__(self, *, batch: int = 100):
        items = await self.r.next_queued(limit=batch)
        for d in items:
            await self.r.mark_sent(d["delivery_id"])
            await self.n.notify(d)
            await self.r.mark_delivered(d["delivery_id"])
```
## 8. API 라우터 (생성/열람/ACK)
```python
# app/api_http.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta
from app.container import Container

router = APIRouter()

class CreateNotifyIn(BaseModel):
    kind: str; severity: str
    title: str|None = None; body: str|None = None; data: dict|None = None
    recipients: list[UUID]; channel: str = "websocket"
    expires_minutes: int|None = 120

@router.post("/notify")
async def create_notify(payload: CreateNotifyIn, c: Container = Depends()):
    exp = None
    if payload.expires_minutes:
        exp = datetime.utcnow() + timedelta(minutes=payload.expires_minutes)
    mid = await c.create_and_queue(kind=payload.kind, severity=payload.severity, title=payload.title,
                                   body=payload.body, data=payload.data, expires_at=exp,
                                   recipients=payload.recipients, channel=payload.channel)
    return {"message_id": str(mid)}

@router.post("/deliveries/{delivery_id}/read")
async def mark_read(delivery_id: int, c: Container = Depends()):
    await c.mark_read(delivery_id); return {"delivery_id": delivery_id, "status": "read"}

@router.post("/deliveries/{delivery_id}/ack")
async def mark_ack(delivery_id: int, c: Container = Depends()):
    await c.mark_ack(delivery_id); return {"delivery_id": delivery_id, "status": "ack"}
```
## 9. 백그라운드 전송 파이프라인
FastAPI 스타트업 이벤트나 별도 워커에서 `DispatchQueued`를 주기 실행합니다.

```python
# app/main.py
from fastapi import FastAPI
from app.db import make_session_factory
from app.container import Container
from app.api_http import router as http_router
from app.api_ws import router as ws_router
import asyncio, os

app = FastAPI(title="Notify Minimal")
session_factory = make_session_factory(os.environ["DATABASE_URL"])
container = Container(session_factory)

app.include_router(http_router)
app.include_router(ws_router)

@app.on_event("startup")
async def start_workers():
    async def loop():
        while True:
            await container.dispatch_queued(batch=200)
            await asyncio.sleep(0.5)  # 폴링 간격(부하·지연에 맞게 조정)
    asyncio.create_task(loop())
```
## 10. 프런트엔드(WebSocket) 예시
```html
<!-- index.html -->
<script>
const userId = "11111111-1111-1111-1111-111111111111";
const ws = new WebSocket(`wss://your.domain/ws?user_id=${userId}`);
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  // TODO: UI 표시 후 읽음 콜백 전송
  console.log("notify:", msg);
};
</script>
```
## 11. 운영/배포 체크리스트
### Nginx (WebSocket 업그레이드)
```
location /ws {
    proxy_pass http://app:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 60s;
}
```
**환경 노트:** `nginx_setup_log.md` 를 참고해 실제 업스트림/SSL 설정을 반영하세요.

### SQLAdmin / 모니터링
- `sqladmin_setup_log.md` 의 접근 경로/계정으로 테이블 가시화
- 대시보드용 쿼리 예
```sql
-- 응급(RED) 미-ACK
SELECT d.* FROM notify.notify_delivery d
JOIN notify.notify_message m ON m.message_id=d.message_id
WHERE m.severity='red' AND d.ack_at IS NULL AND d.status IN ('sent','delivered','read');
```

### SSH 터널
- 원격 DB 접속은 `ssh_tunnel_guide.md` 의 로컬 포트포워딩 예시를 사용

### 패키지/버전
- `package_verification.md` 에 기록된 FastAPI/SQLAlchemy/asyncpg 버전을 기준으로 requirements를 고정

## 12. 테스트 전략(파이프라인 기준)
- 유닛: UseCase → Fake Repo/Notifier 주입으로 순수 테스트
- 통합: Postgres 테스트 DB + WS 연결 e2e
- 스케줄/재시도: `schedule_test_results.md` 를 참고, 만료 처리/재전송 경계값 검증

샘플 단언:
```python
# pytest 예시
async def test_dispatch_sends_and_marks_delivered(container):
    # given queued deliveries
    await container.dispatch_queued(batch=10)
    # then status should be delivered
```

## 13. 확장 포인트
- 채널 추가(Email/SMS): Notifier 포트에 어댑터 추가
- 에스컬레이션: RED 미-ACK → SMS/Voice 단계 상승 (크론/워크큐)
- Outbox/CDC: 강한 정합성이 필요하면 Outbox 테이블 + 브로커(예: Redis Streams)

## 14. 보안/준법
- PII 최소화, 토큰/전화번호 암호화 고려
- 마케팅 채널은 동의(옵트인) 저장 및 철회(옵트아웃) 준수
- 감사 로그: created_by/ip, payload 스냅샷

## A. 첨부 환경 문서 요약(발췌)
> 실제 문서 전문은 레포에 보관하세요. 아래는 상위 40라인 요약입니다.

### env_variables_guide.md (요약)
```
# 환경 변수 가이드

## 📋 환경 변수 목록

### 🔧 기본 애플리케이션 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `APP_ENV` | 애플리케이션 환경 | `local` | `production` |
| `PYTHON_VERSION` | Python 버전 | `3.12` | `3.12` |
| `PROJECT_NAME` | 프로젝트 이름 | `App Server` | `App Server` |
| `API_V1_STR` | API 버전 경로 | `/api/v1` | `/api/v1` |
| `DEBUG` | 디버그 모드 | `true` | `false` |

### 🗄️ 데이터베이스 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `DB_MODE` | DB 접속 모드 | `local_ssh` | `aws_internal` |
| `DB_APP_URL` | 신규 DB URL | SSH 터널 | AWS 내부망 |
| `DB_LEGACY_URL` | 레거시 DB URL | SSH 터널 | AWS 내부망 |

### 🔐 SSH 터널 설정 (로컬만)
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SSH_TUNNEL_ENABLE` | SSH 터널 활성화 | `true` |
| `SSH_TUNNEL_LOCAL_PORT` | 로컬 포트 | `15432` |
| `SSH_TUNNEL_REMOTE_HOST` | RDS 호스트 | `<rds-host>` |
| `SSH_TUNNEL_REMOTE_PORT` | RDS 포트 | `5432` |
| `SSH_TUNNEL_BASTION_HOST` | Bastion 호스트 | `<bastion-ip>` |
| `SSH_TUNNEL_USER` | SSH 사용자 | `ubuntu` |
| `SSH_TUNNEL_KEY_PATH` | SSH 키 경로 | `~/.ssh/id_rsa` |

### 🗃️ Redis 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` | `redis://redis:6379/0` |
| `REDIS_PASSWORD` | Redis 비밀번호 | `` | `<set-redis-password>` |
| `REDIS_DB` | Redis DB 번호 | `0` | `0` |

### 📁 파일 저장소 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
```

### nginx_setup_log.md (요약)
```
# Nginx 프록시 서버 구축 로그

## 📅 작업 일시: 2025-09-12 19:30-19:40

## 🎯 작업 목표
- Nginx를 프록시 서버로 구성하여 FastAPI 애플리케이션 프록시
- 로드 밸런싱 및 보안 헤더 설정
- Docker Compose 통합

## ✅ 완료된 작업

### 1. Nginx 설정 파일 생성
- **파일**: `nginx/nginx.conf`
- **주요 기능**:
  - FastAPI 백엔드 프록시 설정
  - Gzip 압축 활성화
  - 보안 헤더 추가
  - 로드 밸런싱 준비
  - 정적 파일 서빙 설정

### 2. Docker Compose 통합
- **파일**: `docker/compose.base.yml`
- **Nginx 서비스 추가**:
  - 포트: 80 (HTTP), 443 (HTTPS)
  - FastAPI 의존성 설정
  - 헬스체크 구성
  - 정적 파일 볼륨 마운트

### 3. Nginx Dockerfile 생성
- **파일**: `docker/nginx.Dockerfile`
- **기능**:
  - Nginx 1.27-alpine 기반
  - curl, wget 설치
  - 설정 파일 복사
  - 권한 설정

### 4. 로컬 테스트 환경 구축
- **Nginx 설치**: Ubuntu 패키지 매니저 사용
- **설정 적용**: `/etc/nginx/nginx.conf` 복사
- **서비스 시작**: systemctl을 통한 관리
```

### package_verification.md (요약)
```
# 패키지 설치 검증 보고서

## 📦 설치된 패키지 목록

### ✅ 핵심 웹 프레임워크
- **fastapi**: 0.116.1 - 웹 API 프레임워크
- **uvicorn**: 0.35.0 - ASGI 서버
- **pydantic**: 2.11.7 - 데이터 검증
- **pydantic-settings**: 2.10.1 - 설정 관리
- **starlette**: 0.47.3 - ASGI 프레임워크

### ✅ 데이터베이스 관련
- **sqlalchemy**: 2.0.43 - ORM
- **asyncpg**: 0.30.0 - PostgreSQL 비동기 드라이버
- **alembic**: 1.16.5 - 데이터베이스 마이그레이션

### ✅ 스케줄러 및 캐시
- **apscheduler**: 3.11.0 - 작업 스케줄러
- **redis**: 6.4.0 - 캐시 및 세션 저장소

### ✅ 관리자 UI
- **sqladmin**: 0.21.0 - FastAPI용 관리자 UI

### ✅ 인증 및 보안
- **python-jose**: 3.5.0 - JWT 토큰 처리
- **passlib**: 1.7.4 - 패스워드 해싱
- **bcrypt**: 4.3.0 - 패스워드 암호화
- **python-multipart**: 0.0.20 - 파일 업로드

### ✅ HTTP 클라이언트
- **httpx**: 0.28.1 - 비동기 HTTP 클라이언트
- **requests**: 2.32.5 - 동기 HTTP 클라이언트

### ✅ 파일 저장소
- **pydrive2**: 1.21.3 - Google Drive API
- **google-api-python-client**: 2.181.0 - Google API 클라이언트

### ✅ 의존성 주입
- **dependency-injector**: 4.48.1 - 의존성 주입 컨테이너

```

### persona_websocket_notify_guide.md (요약)
```
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
```

### schedule_test_results.md (요약)
```
# 스케줄 작업 테스트 결과 보고서

## 📅 테스트 일시: 2025-09-12 19:58-19:59

## 🎯 테스트 목표
- 관리자 화면에서 1분 후 실행되는 스케줄 작업 등록
- 작업 실행 결과 확인 및 검증
- SQLAdmin 관리자 화면의 CRUD 기능 테스트

## ✅ 테스트 수행 과정

### 1. 테스트 작업 생성
- **작업 ID**: fc145d47-f2d9-4329-9e38-c38557fb7c9e
- **작업명**: test_1min_schedule
- **함수**: test_module.test_1min_function
- **Cron 표현식**: 59 10 12 9 * (2025-09-12 10:59 UTC 실행)
- **상태**: enabled=true, status=idle
- **생성 시간**: 2025-09-12 10:58:05 UTC

### 2. 관리자 화면 확인
- **URL**: http://localhost:8000/admin/scheduled-job/list
- **결과**: ✅ 새 작업이 목록에 정상 표시됨
- **표시 정보**: ID, 작업명, 함수, Cron, 활성화 상태, 생성일

### 3. API를 통한 데이터 확인
- **엔드포인트**: GET /api/v1/scheduled-jobs
- **결과**: ✅ 2개 작업 조회 성공
  - 기존 작업: test_job (5분마다)
  - 새 작업: test_1min_schedule (1분 후 실행)

### 4. 작업 실행 시뮬레이션
- **실행 시간**: 2025-09-12 10:59:34 UTC
- **상태 변경**: idle → completed
- **마지막 실행**: 2025-09-12 10:59:34 UTC
- **다음 실행**: 2025-09-12 11:59:34 UTC (1시간 후)

## 📊 테스트 결과

### ✅ 성공한 기능
1. **스케줄 작업 생성**
```

### sqladmin_setup_log.md (요약)
```
# SQLAdmin 관리자 화면 구축 로그

## 📅 작업 일시: 2025-09-12 19:40-19:50

## 🎯 작업 목표
- SQLAdmin을 사용하여 스케줄러 관리자 화면 구축
- ScheduledJob 모델을 위한 CRUD 인터페이스 제공
- FastAPI 애플리케이션과 통합

## ✅ 완료된 작업

### 1. SQLAdmin 설정 파일 생성
- **파일**: `app/admin/scheduled_job_admin.py`
- **주요 기능**:
  - ScheduledJob 모델을 위한 관리자 뷰
  - 컬럼 표시 설정 (id, name, func, cron, enabled, status, created_at)
  - 검색 및 정렬 기능
  - 논리 삭제 정책 적용

### 2. SQLAdmin 메인 설정
- **파일**: `app/admin/admin_app.py`
- **기능**:
  - 데이터베이스 엔진 설정
  - 관리자 뷰 등록
  - FastAPI 앱 마운트

### 3. 간단한 SQLAdmin 애플리케이션
- **파일**: `app/simple_admin_app.py`
- **기능**:
  - 동기 엔진 사용
  - URL 인코딩 처리
  - 기본 CRUD 기능

### 4. FastAPI 통합
- **SQLAdmin 마운트**: `/admin` 경로
- **관리자 뷰**: ScheduledJob 모델
- **기본 기능**: 생성, 조회, 수정, 삭제

## 🧪 테스트 결과

```

### ssh_tunnel_guide.md (요약)
```
# SSH 터널 설정 가이드

## 🔧 SSH 터널 설정 개요

### 기본 명령어
```bash
ssh -i "iot_db_key_pair.pem" -L 0.0.0.0:15432:localhost:5432 ubuntu@ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com
```

### 환경 변수 설정
| 변수명 | 값 | 설명 |
|--------|----|----|
| `SSH_TUNNEL_ENABLE` | `true` | SSH 터널 활성화 |
| `SSH_TUNNEL_LOCAL_PORT` | `15432` | 로컬 포트 |
| `SSH_TUNNEL_REMOTE_HOST` | `localhost` | 원격 호스트 (EC2 내부) |
| `SSH_TUNNEL_REMOTE_PORT` | `5432` | 원격 포트 (PostgreSQL) |
| `SSH_TUNNEL_BASTION_HOST` | `ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com` | Bastion 호스트 |
| `SSH_TUNNEL_USER` | `ubuntu` | SSH 사용자 |
| `SSH_TUNNEL_KEY_PATH` | `/app/secret/iot_db_key_pair.pem` | SSH 키 파일 경로 |

## 🚀 자동 실행 방법

### 1. Docker Compose로 실행
```bash
# 로컬 개발 환경
docker compose -f docker/compose.base.yml -f docker/compose.local.yml --env-file secret/.env.local up -d

# 프로덕션 환경
docker compose -f docker/compose.base.yml -f docker/compose.prod.yml --env-file secret/.env.prod up -d
```

### 2. 수동 실행
```bash
# SSH 터널만 실행
python scripts/ssh_tunnel.py

# 연결 테스트
python scripts/test_ssh_tunnel.py
```

```

### work_log.md (요약)
```
# 서버 구축 작업 이력

## 📊 전체 진행률: 30% (6/20 단계 완료)

### Phase 1: 기반 인프라 구축 (1-2주) - 진행률: 100% (4/4 단계 완료)

#### ✅ 1단계: 프로젝트 초기화 (완료)
- [x] `server/app_server` 루트 디렉터리 구조 생성
- [x] 환경변수 파일 생성 (`.env.local`, `.env.prod`)
- [x] `.gitignore` 업데이트 (민감 정보 제외)
- [x] 파일 업로드 제한 설정 주석처리 (향후 결정)
- [x] `pyproject.toml` 생성 (Python 3.12, 의존성 정의)
- [x] Python 3.12 가상환경 생성 및 의존성 설치
- [ ] 브랜치 전략 적용 (`feat/server-app_server--init-scaffold`) - **진행 예정**

#### ✅ 2단계: 환경 설정 (완료)
- [x] Docker Compose 구성 (base, local, prod)
- [x] Nginx 프록시 설정
- [x] Redis 영속성 설정
- [x] Python 3.12 Dockerfile 생성

#### ✅ 3단계: 패키지 설치 및 검증 (완료)
- [x] Python 3.12 가상환경 생성
- [x] 모든 핵심 패키지 설치 확인
- [x] 개발 도구 패키지 설치 (pytest, black, ruff, mypy 등)
- [x] 패키지 의존성 검증

#### ✅ 4단계: 환경 변수 템플릿 완성 (완료)
- [x] `.env.local` 템플릿 완성 (로컬 개발용)
- [x] `.env.prod` 템플릿 완성 (프로덕션용)
- [x] 모든 환경 변수 Docker Compose에 반영
- [x] 보안 강화 및 민감 정보 보호

#### ✅ 5단계: 데이터베이스 연결 및 SSH 터널 (완료)
- [x] 멀티 엔진 설정 (legacy, app)
- [x] Alembic 초기화 (신규 스키마만)
- [x] `scheduled_jobs` 테이블 모델 생성
- [x] 비삭제 정책 구현
- [x] SSH 터널 자동 생성 설정
- [x] 실제 DB 정보로 환경 변수 업데이트
```

## B. 마이그레이션/롤백 팁
- ENUM 추가: `ALTER TYPE ... ADD VALUE IF NOT EXISTS 'new'`
- TEXT → ENUM: `ALTER TABLE ... USING column::type`
- 롤백: 트랜잭션 단위로 DDL 묶기 어렵다면 단계적 스크립트로 안전하게

## C. 업무용 체크리스트 (요약)
- [ ] DB 접속 확인(SSH 터널/보안그룹/pg_hba)
- [ ] 3테이블 존재, COMMENT 메타 확인
- [ ] WebSocket 업그레이드/Nginx 헬스체크
- [ ] /notify POST → /ws 수신 엔드투엔드
- [ ] /deliveries/* 콜백 동작(읽음/ACK)
- [ ] RED 미ACK 모니터링 쿼리 배치

---

문서 끝
