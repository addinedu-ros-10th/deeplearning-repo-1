# 🔔 알림 시스템 개발 관리 문서

---

## 📊 프로젝트 개요

### 🎯 목표
- WebSocket 기반 실시간 알림 시스템 구현
- Hexagonal Architecture 적용으로 확장 가능한 시스템 설계
- 다중 채널 지원 (WebSocket, Email, SMS, Push 등)
- 높은 성능과 안정성을 가진 알림 전달 시스템

### 🏗️ 아키텍처
- **Design Pattern**: Hexagonal Architecture (Ports & Adapters)
- **Communication**: WebSocket + Redis Pub/Sub
- **Database**: PostgreSQL (notify 스키마)
- **Framework**: FastAPI + SQLAlchemy
- **Background Processing**: AsyncIO 기반 디스패처

---

## ✅ 개발 완료 현황 (2025-09-29)

### 🎯 Core Domain Layer
- [x] **Domain Models**
  - `NotifyMessage`: 알림 메시지 엔티티
  - `NotifyDelivery`: 전송 기록 엔티티  
  - `NotifyDevice`: 디바이스 정보 엔티티
- [x] **Value Objects**
  - Channel Enum (websocket, email, sms, push 등)
  - Delivery Status Enum (queued, sent, delivered, read, ack 등)
- [x] **Domain Events**
  - 알림 생성, 전송, 수신 이벤트 처리

### 🔌 Ports (Interfaces)
- [x] **Repository Ports**
  - `NotifyMessageRepository`: 메시지 CRUD 인터페이스 + Sender ID 조회
  - `NotifyDeliveryRepository`: 전송 기록 CRUD 인터페이스
  - `NotifyDeviceRepository`: 디바이스 CRUD 인터페이스
- [x] **Service Ports**
  - `NotificationChannel`: 다중 채널 지원 인터페이스
  - `ConnectionManager`: WebSocket 연결 관리 인터페이스

### 🔧 Adapters (Implementations)
- [x] **Database Adapters**
  - SQLAlchemy 기반 Repository 구현체들
  - PostgreSQL notify 스키마 연동
  - JSONB 쿼리 지원 (Sender ID 조회)
- [x] **WebSocket Adapter**
  - FastAPI WebSocket 연결 관리
  - 실시간 메시지 전송 구현
- [x] **HTTP Adapter**
  - REST API 엔드포인트 구현
  - 알림 큐잉 API (`/api/v1/notify/queue`)
  - Sender ID 기준 메시지 조회 API (`/api/v1/notify/messages/by-sender/{sender_id}`)

### 🏢 Application Layer
- [x] **Use Cases**
  - `NotifyQueueUseCase`: 알림 큐 등록
  - `NotifyDispatchUseCase`: 알림 전송 처리
  - `ListNotifyMessagesBySenderUseCase`: Sender ID 기준 메시지 조회
- [x] **DTOs**
  - `NotifyQueueRequest`: 알림 생성 요청 DTO
  - `NotifyQueueResponse`: 알림 생성 응답 DTO

### 🖥️ Infrastructure Layer
- [x] **Database Models**
  - SQLAlchemy ORM 모델 구현
  - PostgreSQL 스키마 정의
- [x] **Background Services**
  - 비동기 디스패처 구현
  - 큐 처리 및 전송 로직
- [x] **Connection Management**
  - WebSocket 연결 풀 관리
  - 사용자별 세션 추적

### 🌐 Frontend Integration
- [x] **클라이언트 라이브러리**
  - Python 클라이언트: WebSocket 연결 및 알림 전송
  - JavaScript 클라이언트: 브라우저 환경 지원
  - HTML 테스트 도구: 수동 테스트 인터페이스
- [x] **웹서버 호스팅**
  - Nginx 정적 파일 서빙: `/notification/` 경로
  - Docker Compose 통합: 볼륨 마운트 자동화
  - 브라우저 직접 접근: `http://localhost/notification/client/`
- [x] **프로젝트 구조 최적화**
  - 알림 도구 통합: `Util/notification/` 디렉토리
  - 클라이언트/도구 분리: `client/`, `tools/` 서브 디렉토리
  - 종합 문서화: 사용법, 테스트, 고급 설정 가이드
- [x] **동적 URL 변환 시스템**
  - WebSocket URL → HTTP API URL 자동 생성
  - 단일 URL 설정으로 모든 기능 사용
  - 환경별 URL 변경 시 한 곳만 수정

---

## 🗄️ 데이터베이스 스키마

### 📋 notify.notify_message
```sql
message_id      UUID PRIMARY KEY
kind           TEXT NOT NULL              -- 알림 종류 (info, warning, error)
severity       TEXT NOT NULL              -- 심각도 (green, yellow, red)
title          TEXT                       -- 제목
body           TEXT                       -- 본문
data           JSONB                      -- 추가 데이터
scheduled_at   TIMESTAMP WITH TIME ZONE   -- 예약 시간
expires_at     TIMESTAMP WITH TIME ZONE   -- 만료 시간
created_by     UUID                       -- 생성자
created_ip     TEXT                       -- 생성 IP
created_at     TIMESTAMP WITH TIME ZONE   -- 생성 시간
updated_at     TIMESTAMP WITH TIME ZONE   -- 수정 시간
```

### 📋 notify.notify_delivery
```sql
delivery_id     BIGSERIAL PRIMARY KEY
message_id      UUID NOT NULL              -- 메시지 참조
user_id         UUID NOT NULL              -- 수신자
channel         channel_enum NOT NULL      -- 전송 채널
endpoint        TEXT                       -- 엔드포인트
status          delivery_status_enum       -- 전송 상태
send_at         TIMESTAMP WITH TIME ZONE   -- 전송 시간
delivered_at    TIMESTAMP WITH TIME ZONE   -- 도착 시간
read_at         TIMESTAMP WITH TIME ZONE   -- 읽음 시간
ack_at          TIMESTAMP WITH TIME ZONE   -- 확인 시간
error_text      TEXT                       -- 오류 메시지
payload         JSONB                      -- 페이로드
client_meta     JSONB                      -- 클라이언트 메타데이터
created_at      TIMESTAMP WITH TIME ZONE   -- 생성 시간
updated_at      TIMESTAMP WITH TIME ZONE   -- 수정 시간
```

### 📋 notify.notify_device
```sql
device_id       UUID PRIMARY KEY
user_id         UUID NOT NULL              -- 사용자 참조
channel         channel_enum NOT NULL      -- 채널 타입
endpoint        TEXT NOT NULL              -- 엔드포인트 주소
is_active       BOOLEAN DEFAULT TRUE       -- 활성 상태
client_meta     JSONB                      -- 클라이언트 정보
created_at      TIMESTAMP WITH TIME ZONE   -- 생성 시간
updated_at      TIMESTAMP WITH TIME ZONE   -- 수정 시간
```

---

## 🔄 알림 처리 플로우

### 1️⃣ 알림 생성 단계
```
Client → POST /api/v1/notify/queue
       → NotifyQueueUseCase
       → NotifyMessage 생성
       → NotifyDelivery 큐 등록
       → Response (message_id, queued_count)
```

### 2️⃣ 백그라운드 처리 단계
```
Dispatcher Loop → 큐에서 pending 알림 조회
                → WebSocket 연결 확인
                → 메시지 전송
                → 상태 업데이트 (sent → delivered)
```

### 3️⃣ 클라이언트 수신 단계
```
WebSocket Client → 연결 유지
                 → 메시지 수신
                 → 화면 표시
                 → (선택적) 읽음/확인 처리
```

---

## 🛠️ 개발 환경 설정

### 🔧 환경 변수
```bash
# 알림 시스템 활성화
NOTIFY_ENABLE=true
NOTIFY_DISPATCH_ENABLE=true
NOTIFY_WS_ENABLE=true

# 데이터베이스 연결
DB_APP_URL=postgresql+asyncpg://user:pass@host:port/db
```

### 🐳 Docker Compose
```yaml
services:
  api:
    environment:
      - NOTIFY_ENABLE=true
      - NOTIFY_DISPATCH_ENABLE=true
      - NOTIFY_WS_ENABLE=true
```

### 🌐 Nginx 설정
```nginx
location /ws {
    proxy_pass http://api:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

---

## 📊 성능 및 모니터링

### 📈 핵심 메트릭
- **연결 수**: 동시 WebSocket 연결 수
- **메시지 처리량**: 초당 처리되는 알림 수
- **전송 성공률**: 성공적으로 전달된 알림 비율
- **응답 시간**: 알림 생성부터 전달까지 소요 시간

### 🔍 로그 모니터링
- 디스패처 처리 로그
- WebSocket 연결/해제 로그
- 오류 발생 로그
- 성능 관련 로그

---

## 🚀 향후 개발 계획

### Phase 1: 기본 기능 확장
- [x] Sender ID 기준 메시지 조회 API 구현 ✅ (2025-09-29)
- [ ] 알림 읽음/확인 API 구현
- [ ] 알림 히스토리 조회 API
- [ ] 사용자별 알림 설정 관리

### Phase 2: 다중 채널 지원
- [ ] Email 채널 구현
- [ ] SMS 채널 구현  
- [ ] Push 알림 채널 구현
- [ ] 카카오톡 채널 구현

### Phase 3: 고급 기능
- [ ] 알림 템플릿 시스템
- [ ] 배치 전송 최적화
- [ ] 실패 재시도 메커니즘
- [ ] 통계 및 분석 대시보드

### Phase 4: 확장성 개선
- [ ] Redis Pub/Sub 통합
- [ ] 마이크로서비스 분리
- [ ] 로드 밸런싱 최적화
- [ ] 캐싱 전략 구현

---

## 🔧 기술적 고려사항

### 🏗️ 아키텍처 장점
- **확장성**: 새로운 채널 추가가 용이
- **유지보수성**: 계층 분리로 코드 관리 효율적
- **테스트 용이성**: 의존성 주입으로 단위 테스트 가능
- **성능**: 비동기 처리로 높은 처리량 달성

### ⚠️ 주의사항
- WebSocket 연결 수 제한 고려
- 데이터베이스 연결 풀 관리
- 메모리 누수 방지
- 예외 상황 처리 강화

---

## 📞 문의 및 지원

### 🐛 이슈 리포팅
- 버그 발견 시 GitHub Issues 활용
- 로그 파일과 함께 상세한 재현 단계 제공

### 💡 기능 요청
- 새로운 채널 지원 요청
- 성능 개선 제안
- UI/UX 개선 아이디어

---

*Last Updated: 2025-09-29*
*Version: 1.1.0*
*Status: ✅ Production Ready*

---

## 📋 최근 업데이트 (2025-09-29)

### 🆕 새로운 기능
- **Sender ID 기준 메시지 조회 API**: `GET /api/v1/notify/messages/by-sender/{sender_id}`
  - 특정 발신자로 전송된 메시지들을 조회
  - JSONB 필드에서 sender 값을 효율적으로 검색
  - 페이지네이션 지원 (skip, limit)
  - 생성 시간 기준 내림차순 정렬

### 🔧 기술적 개선
- **Repository Layer**: `list_by_sender()` 메서드 추가
- **Use Case Layer**: `ListNotifyMessagesBySenderUseCase` 구현
- **HTTP Adapter**: 새로운 엔드포인트 추가
- **API 문서화**: 상세한 사용법과 예시 포함

### 📁 변경된 파일
- `app/domain/ports/notify_message_repository.py`
- `app/adapters/repositories/notify_message_repository_impl.py`
- `app/application/use_cases/notify_message_use_cases.py`
- `app/adapters/http/notify_message_router.py`
- `docs/apis/sender_messages_api.md` (신규)

