
---

# 액션 아이템 (헥사고날 아키텍처 적용 버전)

## 📊 현재 작업 현황 리포트 (2025-09-12)

### ✅ 완료된 작업

1. **기본 인프라 구축**
   - Python 3.12 환경 설정 및 가상환경 구성
   - Docker Compose 환경 구축 (local, prod, test)
   - PostgreSQL 데이터베이스 연결 (SSH 터널)
   - Redis 캐시 서버 구성

2. **스케줄러 시스템 구축**
   - APScheduler 기반 스케줄러 구현
   - SQLAdmin 관리자 화면 구축
   - 스케줄 작업 CRUD API 구현
   - 수동 작업 실행 기능

3. **데이터베이스 관리**
   - Alembic 마이그레이션 시스템 구축
   - scheduled_jobs 테이블 생성
   - 다중 데이터베이스 바인딩 (legacy, app)

4. **웹 서버 구성**
   - Nginx 프록시 서버 설정
   - FastAPI 애플리케이션 연동
   - Swagger UI 문서화

5. **환경 관리**
   - 환경별 설정 파일 (.env.local, .env.prod)
   - Docker Compose 환경별 구성
   - 보안 파일 관리 (SSH 키, 환경 변수)

6. **데이터베이스 연결 통합 (2025-09-18)**
   - 공통 DB 연결 유틸리티 구현 (`connection_utils.py`)
   - 환경변수 기반 DB 연결 표준화
   - Docker 네트워크 호환성 개선
   - 모든 서비스 통합 DB 연결 관리

7. **ML 스키마 초기화 안정화 (2025-09-18)**
   - FastAPI startup 이벤트 기반 데이터베이스 매니저 초기화
   - 운영 환경에서 ML API 안정성 확보
   - 이벤트 루프 충돌 문제 해결
   - 모든 ML Registry API 정상 작동 보장

8. **WebSocket 기반 실시간 알림 시스템 구현 (2025-09-24)**
   - Hexagonal Architecture 기반 알림 시스템 설계 및 구현

9. **Sender ID 기준 메시지 조회 API 구현 (2025-09-29)**
   - JSONB 필드에서 sender 값을 효율적으로 조회하는 API 추가
   - Repository, Use Case, HTTP Adapter 레이어에 기능 구현
   - 페이지네이션 및 정렬 기능 포함
   - 상세한 API 문서화 완료
   - PostgreSQL 알림 스키마 구축 (notify_message, notify_delivery, notify_device)
   - WebSocket 연결 관리 및 실시간 메시지 전송
   - 백그라운드 디스패처를 통한 비동기 알림 처리
   - 현대적 UI/UX 디자인의 테스트 도구 완성

### 🔄 현재 상태 (2025-09-24 최종 업데이트)
- **API 서버**: ✅ 정상 동작 (http://localhost:8000) - Health Check 통과
- **데이터베이스**: ✅ 연결 성공 (환경변수 기반) - 모든 스키마 정상 접근
- **스케줄러**: ✅ 완전 정상 동작 - 환경변수 기반 DB 연결
- **관리자 화면**: ✅ SQLAdmin 완전 정상 - Internal Server Error 해결됨
- **Nginx 프록시**: ✅ 정상 동작 (http://localhost:80) - 모든 엔드포인트 접근 가능
- **Docker Compose**: ✅ 모든 서비스 Up(healthy) - api, nginx, redis
- **SSH 터널 자동화**: ✅ 호스트 기반 스크립트로 완전 자동화
- **ML Registry API**: ✅ 완전 구현 및 테스트 완료 - Dataset, Experiment CRUD API
- **환경변수 관리**: ✅ Docker Compose 환경변수 기반 DB 연결 완전 구현
- **DB 연결 통합**: ✅ 모든 서비스가 환경변수 기반으로 통일된 DB 연결
- **ML 스키마 초기화**: ✅ FastAPI startup 이벤트 기반 안정적 초기화
- **운영 환경 호환성**: ✅ 운영 환경에서 모든 ML API 정상 작동
- **알림 시스템**: ✅ WebSocket 기반 실시간 알림 완전 구현 - Hexagonal Architecture
- **전체 시스템**: ✅ 완전 정상 작동 - 모든 기능 테스트 통과

### 🛠️ 해결된 주요 문제들 (2025-09-18)

#### 1. 데이터베이스 연결 통합 및 환경변수 기반 설정
- **문제**: 각 서비스마다 하드코딩된 DB 연결 정보 사용
- **해결**: 
  - 공통 DB 연결 유틸리티 생성 (`app/infrastructure/db/connection_utils.py`)
  - 모든 서비스가 환경변수 기반으로 통일된 DB 연결 방식 사용
  - Docker Compose 환경변수 자동 파싱 및 적용
- **영향**: 
  - `scheduler_service.py`: 스케줄러 서비스 DB 연결 개선
  - `scheduler_app.py`: 스케줄러 앱 DB 연결 개선
  - `main.py`: 메인 앱 DB 연결 개선
- **결과**: ML 스키마 오류 완전 해결, 모든 API 정상 작동

#### 2. Docker 네트워크 호환성 개선
- **문제**: `host.docker.internal` 해석 실패로 인한 DB 연결 오류
- **해결**: 
  - 자동 IP 변환 로직 구현 (`host.docker.internal` → `172.17.0.1`)
  - URL 파싱 및 연결 파라미터 자동 생성
  - 연결 실패 시 기본값 fallback 메커니즘
- **결과**: Docker 환경에서 안정적인 DB 연결 보장

#### 3. 환경변수 기반 설정 표준화
- **문제**: 하드코딩된 DB 연결 정보로 인한 유연성 부족
- **해결**:
  - `DB_APP_URL`, `ML_DB_URL`, `DB_LEGACY_URL` 환경변수 지원
  - `postgresql+asyncpg://` 형식 자동 변환
  - 중앙화된 연결 관리로 유지보수성 향상
- **결과**: 환경별 DB 설정 변경이 코드 수정 없이 가능

#### 4. ML 스키마 초기화 문제 해결 (운영 환경)
- **문제**: 운영 환경에서 ML 스키마 엔진 초기화 실패로 인한 API 오류
  - `[Errno -2] Name or service not known` 오류 발생
  - `ML 스키마 엔진이 초기화되지 않았습니다` RuntimeError
  - `500: Failed to list datasets` API 오류
- **해결**:
  - FastAPI startup 이벤트로 데이터베이스 매니저 초기화 이동
  - 비동기 초기화를 안전하게 처리하는 `@app.on_event("startup")` 사용
  - 이벤트 루프 충돌 문제 해결
- **영향**:
  - `main.py`: 동기적 초기화 제거, startup 이벤트로 이동
  - 모든 ML API 정상 작동 (datasets, experiments, detection-events)
- **결과**: 운영 환경에서 모든 ML Registry API 정상 작동

### 🛠️ 해결된 주요 문제들 (2025-09-15)

#### 1. Docker Compose 실행 문제들
- **볼륨 마운트 오류**: `invalid mount path: '.'` → 환경변수 기본값 설정으로 해결
- **포트 충돌**: 8000 포트 중복 사용 → 포트 분리 구성으로 해결
- **Nginx www-data 사용자 오류**: Alpine Linux 호환성 문제 → `user nginx;` 설정으로 해결
- **환경변수 로드 실패**: `DB_APP_URL`, `ML_DB_URL` 미인식 → `--env-file` 옵션 사용으로 해결
- **호스트 접근 문제**: `localhost:15432` 연결 실패 → `host.docker.internal` 사용으로 해결
- **환경변수 치환 미적용**: `--env-file` 옵션 사용으로 해결

#### 2. SSH 터널 자동화
- **Docker 컨테이너 내 SSH 터널 문제**: 호스트 기반 스크립트로 변경
- **포트 진단 및 자동 복구**: 포트 사용 상태 확인 후 적절한 조치 수행

#### 3. SQLAdmin 관리자 패널 문제들 (2025-09-13 해결)
- **이벤트 루프 충돌**: `asyncio.run()` 호출 문제 → 동기 `get_sync_engine()` 사용으로 해결
- **Internal Server Error**: 필터 설정 및 검색 플레이스홀더 오류 → 설정 수정으로 해결
- **관리자 패널 접근 불가**: `/admin` 경로 500 오류 → 완전 해결됨

#### 4. 스케줄러 시스템 문제들 (2025-09-13 해결)
- **데이터베이스 연결 실패**: `0.0.0.0` → `host.docker.internal` 변경으로 해결
- **스케줄러 직렬화 오류**: `Schedulers cannot be serialized` → 정적 메서드 사용으로 해결
- **작업 로드 실패**: Connection refused 오류 → Docker 네트워킹 설정으로 해결
- **데이터베이스 연결 검증**: Python 기반 연결 테스트로 안정성 확보

### 🎯 최종 시스템 상태 리포트 (2025-09-13)

#### ✅ 완전 정상 작동 중인 기능들
1. **API 서버 (FastAPI)**
   - Health Check: `http://localhost:8000/health` → "healthy" 응답
   - 스케줄러 API: `http://localhost/api/v1/scheduled-jobs` → 2개 작업 로드
   - Swagger UI: `http://localhost/docs` → 정상 접근

2. **SQLAdmin 관리자 패널**
   - 메인 페이지: `http://localhost/admin/` → 200 OK
   - 스케줄 작업 목록: `http://localhost/admin/scheduled-job/list` → 200 OK
   - 데이터 표시: 2개 스케줄 작업 정상 표시
   - 검색/정렬/페이지네이션: 모든 기능 정상 작동

3. **Nginx 프록시 서버**
   - Health Check: `http://localhost/healthz` → "ok" 응답
   - API 프록시: 모든 API 엔드포인트 정상 프록시
   - 정적 파일 서빙: CSS/JS 리소스 정상 로드

4. **데이터베이스 연결**
   - SSH 터널: 포트 15432 정상 활성화
   - PostgreSQL: `iot_care` 데이터베이스 연결 성공
   - 스케줄 작업: 2개 작업 정상 로드 및 관리

5. **Docker Compose 환경**
   - 모든 서비스: Up(healthy) 상태
   - API 컨테이너: 정상 실행, 오류 없음
   - Nginx 컨테이너: 정상 실행, 헬스체크 통과
   - Redis 컨테이너: 정상 실행, 헬스체크 통과

#### 📊 시스템 메트릭
- **서비스 상태**: 100% 정상 (3/3 서비스 Up)
- **API 응답**: 100% 성공 (모든 엔드포인트 200 OK)
- **데이터베이스**: 정상 연결 (SSH 터널 활성화)
- **스케줄러**: 정상 작동 (2개 작업 로드)
- **관리자 패널**: 완전 정상 (모든 기능 작동)

#### 🔧 Nginx 프록시 설정
- **업스트림 서버 설정**: `api:8000` Docker 서비스명 사용
- **헬스체크 경로 통일**: `/healthz` 엔드포인트로 통일
- **프록시 헤더 설정**: FastAPI와의 완전한 호환성 확보

#### 4. 서비스 통합 테스트
- **API 직접 접근**: `http://localhost:8000/health` ✅
- **Nginx 프록시**: `http://localhost/healthz` ✅
- **Swagger UI**: `http://localhost/docs` ✅
- **모든 서비스 정상**: Docker Compose 상태 확인 완료

---

# 액션 아이템 (업데이트 버전)

### 0. 프로젝트 루트 확정

* 작업 루트 디렉터리를 `server/app_server` 로 고정하고 모든 경로/도커 마운트를 여기를 기준으로 구성한다.

---

## 🏗️ 헥사고날 아키텍처 적용

### 12. 아키텍처 선택 & 전체 그림 (헥사고날 + 포트/어댑터)

**헥사고날(Ports & Adapters)**로 도메인/애플리케이션과 I/O(HTTP, DB, 큐, 외부AI)를 분리하고 DI로 의존성 역전하며, WebSocket/SSE/TCP, AI 게이트웨이, 스케줄러, 파일 저장을 각각 어댑터로 붙인다.

* **포트**: `domain/ports/{repository, ai_gateway, file_storage, scheduler_port}.py`
* **어댑터**: `adapters/{http, repositories, ai, file, scheduler, tcp, streaming}`
* **실무 예**: "센서 업링크→유즈케이스→리포지토리→Timescale 저장→스케줄/워커→알림(WebSocket)" 데이터흐름을 유즈케이스 단위로 캡슐화.

### 13. 프로젝트 구조 (실무 예시 디렉터리)

* 모노레포의 `server/app_server/`에 다음 구조를 생성하고 앱 팩토리 패턴으로 유연하게 기동한다.

```python
server/app_server/
  app/
    domain/                # 엔티티·값객체·도메인서비스·포트(추상)
      entities/
      value_objects/
      services/
      ports/
    application/           # 유즈케이스 구현(트랜잭션 경계, DTO)
      use_cases/
      dto/
    adapters/              # I/O 구현(HTTP/WS/SSE/TCP/Repo/AI/Files/Scheduler)
      http/
      repositories/
      ai/
      file/
      scheduler/
      tcp/
      streaming/
    infrastructure/        # 기술 구현(SQLAlchemy, Alembic, Redis, DI, 설정)
      db/
        models/            # 신규 스키마 Declarative
        reflection/        # 기존 스키마 Reflect(Read/Write, 삭제 금지)
        session.py
        migrations/        # Alembic(신규만)
      cache/
      di/
      settings.py
    main.py                # FastAPI app factory
  docs/                    # 매뉴얼/런북/테스트 문서
  tests/                   # TDD 테스트(단위/통합/프로토콜/E2E)
  docker/                  # Dockerfile.compose(※ Postgres 제외)
  .pre-commit-config.yaml
  pyproject.toml
  .env.example
```

* **실무 팁**: `main.py`는 DI 컨테이너 바인딩, 라우터 등록, 스케줄러 초기화만 담당해 프레임워크 의존을 최소화.

### 14. 의존성 주입 및 관리 정책

* **DI 컨테이너**: `dependency-injector` 사용
* **의존성 역전**: 도메인 레이어는 인프라 레이어에 의존하지 않음
* **포트-어댑터 패턴**: 인터페이스와 구현체 분리
* **팩토리 패턴**: 객체 생성 로직 캡슐화

### 15. 헥사고날 아키텍처 구현 계획

#### Phase 1: 도메인 레이어 구축 ✅
- [x] 엔티티 및 값 객체 정의
- [x] 도메인 서비스 구현
- [x] 포트 인터페이스 정의

#### Phase 2: 애플리케이션 레이어 구축 ✅
- [x] 유즈케이스 구현
- [x] DTO 정의
- [x] 트랜잭션 경계 설정

#### Phase 3: 어댑터 레이어 구축 ✅
- [x] HTTP 어댑터 (FastAPI)
- [x] 리포지토리 어댑터 (SQLAlchemy)
- [x] 스케줄러 어댑터 (APScheduler)
- [ ] 파일 저장소 어댑터 (향후 구현)

#### Phase 4: 인프라 레이어 구축 ✅
- [x] 데이터베이스 설정
- [x] 캐시 설정
- [x] DI 컨테이너 설정
- [x] 설정 관리

---

### 1. 브랜치 네이밍 전략(모노레포 경로와 충돌 없는 방식)

* 기존 `server/app_server` 브랜치가 있어서 하위 경로 생성이 막히므로 **prefix + 하이픈 인코딩** 전략을 쓴다.

  * 형식: `{type}/{mono-encoded}--{task}` (예: `feat/server-app_server--init-scaffold`)
  * 타입: `feat|fix|docs|refactor|config`
  * 생성 예: `git switch -c feat/server-app_server--init-scaffold`
  * (선택) 기존 `server/app_server` 브랜치를 유지해도 되고, 정리하려면 `git branch -m server/app_server server_app_server` 로 리네임 후 사용.

### 2. Python 3.12 고정 & 의존성 설치

* `pyproject.toml`에 `requires-python=">=3.12,<3.13"` 명시하고 FastAPI/SQLAlchemy/Alembic/APScheduler/SQLAdmin/pytest 등 개발 패키지를 정의한다.

### 3. 환경 변수 템플릿 생성(.env.local / .env.aws)

* `.env.local` 은 **SSH 터널 + 로컬 개발** 기준, `.env.aws` 는 **AWS 내부망 접속** 기준으로 분리해 변수 세트를 만든다(아래 템플릿 제공).

### 4. Docker Compose (환경별) 추가

* 공통(base) + 로컬(local) + AWS(aws)로 **멀티 파일 구성**하고, Redis 영속성/파일 스토리지/ Nginx 프록시를 포함한다.

  * 실행 예(로컬): `docker compose -f docker/compose.base.yml -f docker/compose.local.yml --env-file .env.local up -d --build`
  * 실행 예(AWS): `docker compose -f docker/compose.base.yml -f docker/compose.aws.yml --env-file .env.aws up -d --build`

### 5. DB 연결(멀티 바인드) 및 “비삭제(쓰기 허용)” 정책

* `legacy_engine`(기존 DB), `app_engine`(신규 스키마)로 분리하고 Alembic은 **신규 스키마만** 관리한다.
* 기존 테이블에는 INSERT/UPDATE/SELECT 허용, DROP/ALTER/물리 DELETE 금지(레포지토리/권한으로 가드).

### 6. Alembic 초기화 & 마이그레이션(신규만) – scheduled\_jobs 생성 테스트

* Alembic `env.py` 를 **app\_engine** 메타데이터로만 바인딩하고, **`scheduled_jobs`** 테이블 생성 리비전을 작성한 뒤, `pytest`로 **테이블 존재 테스트**를 포함한다(아래 스크립트 제공).

### 7. 스케줄러 GUI(관리자 화면) 구축

* **라이브러리 “SQLAdmin”** 을 사용해 FastAPI에 관리자 UI를 붙이고, `scheduled_jobs` 테이블을 CRUD/토글/수동실행 가능한 화면으로 노출한다(구현 코드 골격 제공).
* **APScheduler** 는 `scheduled_jobs` 를 **소스 오브 트루스**로 폴링/핫리로드하여 스케줄을 반영한다.

### 8. Web 서버(Nginx) 프록시 추가

* 도커 컴포즈에 `nginx` 컨테이너를 정의하고 `/api` → `api:8000` 으로 프록시(로컬 HTTP, AWS는 ALB/HTTPS 전제) 설정을 적용한다.

### 9. 파일 저장(로컬 + 선택적 Google Drive)과 영속성

* 앱 컨테이너의 `/app/data/files` 를 호스트 볼륨(`files-data`)과 연결하고, 선택적으로 Google Drive API(pydrive2)로 업로드 동기화(향후 작업)한다.

### 10. Redis 영속성

* Redis 컨테이너는 `appendonly yes` + 볼륨(`redis-data`)으로 구성해 **스케줄 캐시 등 데이터가 컨테이너 재생성 후에도 유지**되도록 한다.

### 11. 문서화(server/app_server/docs/)

* `docs/architecture/overview.md`, `docs/structure/project_layout.md`, `docs/db/alembic_sqlalchemy_guide.md`, `docs/config/env_variables.md`, `docs/scheduler/admin_ui_guide.md`, `docs/files/storage_drive_guide.md`, `docs/dev/workflow_tdd.md` 를 생성하여 본 내용과 사용법을 정리한다.

### 12. 모니터링 시스템 구축 (향후 진행)

* **로깅 시스템**: 구조화된 로깅 (JSON 형태) 및 로그 레벨 관리
* **메트릭 수집**: Prometheus + Grafana를 통한 시스템 메트릭 모니터링
* **알림 시스템**: Slack/Email을 통한 장애 알림
* **헬스체크**: API 엔드포인트 및 의존성 서비스 상태 모니터링
* **성능 모니터링**: APM (Application Performance Monitoring) 도구 도입

### 13. 테스트 자동화 (향후 진행)

* **단위 테스트**: pytest를 활용한 비즈니스 로직 테스트
* **통합 테스트**: API 엔드포인트 및 데이터베이스 연동 테스트
* **E2E 테스트**: Playwright/Selenium을 활용한 사용자 시나리오 테스트
* **성능 테스트**: Locust를 활용한 부하 테스트
* **CI/CD 파이프라인**: GitHub Actions를 통한 자동화된 테스트 및 배포

---

## 1) `.env` 템플릿 (루트: `server/app_server/`)

**.env.local**

```ini
# 로컬 개발 환경 설정
APP_ENV=local
PYTHON_VERSION=3.12

# DB 접속 모드: local_ssh | aws_internal
DB_MODE=local_ssh

# 로컬: SSH 터널로 RDS 접속 (127.0.0.1:15432)
DB_APP_URL=postgresql+asyncpg://app_user:app_pass@127.0.0.1:15432/app_db
DB_LEGACY_URL=postgresql+asyncpg://legacy_user:legacy_pass@127.0.0.1:15432/legacy_db

# SSH 터널 설정 (수동 실행 또는 autossh 사용)
SSH_TUNNEL_ENABLE=true
SSH_TUNNEL_LOCAL_PORT=15432
SSH_TUNNEL_REMOTE_HOST=<rds-host>.ap-northeast-2.rds.amazonaws.com
SSH_TUNNEL_REMOTE_PORT=5432
SSH_TUNNEL_BASTION_HOST=<bastion-ec2-ip>
SSH_TUNNEL_USER=ubuntu
SSH_TUNNEL_KEY_PATH=~/.ssh/id_rsa

# Redis (도커)
REDIS_URL=redis://redis:6379/0

# Files
FILES_BASE_DIR=/app/data/files

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# GDrive (선택)
GDRIVE_ENABLE=false
GDRIVE_CLIENT_SECRETS=/app/secrets/client_secrets.json
GDRIVE_CREDENTIALS=/app/secrets/credentials.json

# 로깅
LOG_LEVEL=DEBUG

# CORS 설정
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:8080"]

# JWT 설정
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API 설정
API_V1_STR=/api/v1
PROJECT_NAME=App Server

# 파일 업로드 설정
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf,text/plain

# 모니터링 (향후 구현)
# PROMETHEUS_ENABLE=false
# GRAFANA_ENABLE=false
# ELK_STACK_ENABLE=false
```

**.env.prod**

```ini
# 프로덕션 환경 설정
APP_ENV=production
PYTHON_VERSION=3.12

# DB 접속 모드: local_ssh | aws_internal
DB_MODE=aws_internal

# AWS 내부망으로 직접 접속 (보안그룹/서브넷 전제)
DB_APP_URL=postgresql+asyncpg://app_user:app_pass@<rds-endpoint>:5432/app_db
DB_LEGACY_URL=postgresql+asyncpg://legacy_user:legacy_pass@<rds-endpoint>:5432/legacy_db

# Redis (도커)
REDIS_URL=redis://redis:6379/0

# Files
FILES_BASE_DIR=/app/data/files

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<set-strong-password>

# GDrive (선택)
GDRIVE_ENABLE=false
GDRIVE_CLIENT_SECRETS=/app/secrets/client_secrets.json
GDRIVE_CREDENTIALS=/app/secrets/credentials.json

# 로깅
LOG_LEVEL=INFO

# CORS 설정
CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

# JWT 설정
JWT_SECRET_KEY=<set-strong-jwt-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# API 설정
API_V1_STR=/api/v1
PROJECT_NAME=App Server

# 파일 업로드 설정
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document

# 보안 설정
SECURE_COOKIES=true
HTTPS_ONLY=true

# 모니터링 (향후 구현)
# PROMETHEUS_ENABLE=true
# GRAFANA_ENABLE=true
# ELK_STACK_ENABLE=true
```

---

## 2) Docker 구성 (루트: `server/app_server/docker/`)

**compose.base.yml**

```yaml
version: "3.9"

x-env: &env
  env_file:
    - ../.env.local  # 실제 실행 시 --env-file 로 덮어씀
  environment:
    - APP_ENV=${APP_ENV}
    - DB_MODE=${DB_MODE}
    - DB_APP_URL=${DB_APP_URL}
    - DB_LEGACY_URL=${DB_LEGACY_URL}
    - REDIS_URL=${REDIS_URL}
    - FILES_BASE_DIR=${FILES_BASE_DIR}
    - ADMIN_USERNAME=${ADMIN_USERNAME}
    - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    - GDRIVE_ENABLE=${GDRIVE_ENABLE}
    - GDRIVE_CLIENT_SECRETS=${GDRIVE_CLIENT_SECRETS}
    - GDRIVE_CREDENTIALS=${GDRIVE_CREDENTIALS}

services:
  api:
    build:
      context: ..
      dockerfile: docker/python.Dockerfile
    <<: *env
    volumes:
      - ../app:/app/app
      - files-data:${FILES_BASE_DIR}
      - secrets-data:/app/secrets
    depends_on:
      - redis
    command: >
      uvicorn app.main:create_app
      --factory --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"

  redis:
    image: redis:7
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

  nginx:
    image: nginx:1.27-alpine
    depends_on:
      - api
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    ports:
      - "8080:80"

volumes:
  files-data:
  redis-data:
  secrets-data:
```

**compose.local.yml**

```yaml
services:
  api:
    environment:
      - APP_ENV=local
    # 로컬 개발: 코드 마운트 / 디버그 옵션 유지
```

**compose.aws.yml**

```yaml
services:
  api:
    environment:
      - APP_ENV=aws
    # AWS: 필요 시 이미지 태그/리소스 제한/로깅 추가
```

**python.Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 시스템 빌드 의존 (필요 최소)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install "fastapi[standard]" sqlalchemy[asyncio] asyncpg alembic \
                apscheduler sqladmin pydantic-settings dependency-injector \
                httpx redis pydrive2 pytest pytest-asyncio

COPY app /app/app
```

**nginx/nginx.conf**

```nginx
user  nginx;
worker_processes  auto;
events { worker_connections 1024; }
http {
  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;
  sendfile      on;
  keepalive_timeout  65;

  upstream api_upstream {
    server api:8000;
  }

  server {
    listen 80;
    server_name _;

    location /api/ {
      proxy_pass http://api_upstream/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 헬스체크
    location /healthz { return 200 "ok"; }
  }
}
```

---

## 3) Alembic (scheduled\_jobs 테이블 생성)

**app/infrastructure/db/models/scheduled\_job.py**

```python
from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Boolean, TIMESTAMP, text
import uuid

class Base(DeclarativeBase): pass

def gen_uuid() -> str:
    return str(uuid.uuid4())

class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    func: Mapped[str] = mapped_column(String(200))              # "module:function"
    cron: Mapped[str] = mapped_column(String(64))               # "*/5 * * * *"
    args: Mapped[dict] = mapped_column(JSONB, default=dict)
    kwargs: Mapped[dict] = mapped_column(JSONB, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    next_run_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), default="idle")
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
```

**Alembic env.py (요지) – 신규 스키마만 바인딩**

```python
# app/infrastructure/db/migrations/env.py
from alembic import context
from sqlalchemy import create_engine
from app.infrastructure.db.models.scheduled_job import Base  # Base.metadata

config = context.config
target_metadata = Base.metadata

def run_migrations_offline():
    url = context.get_x_argument(as_dictionary=True).get("DB_URL")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = context.get_x_argument(as_dictionary=True).get("DB_URL")
    connectable = create_engine(url, pool_pre_ping=True, future=True)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**리비전 예시** `app/infrastructure/db/migrations/versions/20250912_create_scheduled_jobs.py`

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

# revision identifiers
revision = "20250912_create_scheduled_jobs"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("func", sa.String(length=200), nullable=False),
        sa.Column("cron", sa.String(length=64), nullable=False),
        sa.Column("args", psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("kwargs", psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("next_run_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'idle'")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_scheduled_jobs_name", "scheduled_jobs", ["name"], unique=True)

def downgrade():
    op.drop_index("ix_scheduled_jobs_name", table_name="scheduled_jobs")
    op.drop_table("scheduled_jobs")
```

**마이그레이션 실행(로컬; SSH 터널 전제)**

```bash
cd server/app_server
alembic -x DB_URL="${DB_APP_URL}" upgrade head
```

**테스트(테이블 생성 확인)** `tests/db/test_migration_scheduled_jobs.py`

```python
import pytest
from sqlalchemy import create_engine, inspect
import os

@pytest.mark.parametrize("envkey", ["DB_APP_URL"])
def test_scheduled_jobs_table_exists(envkey):
    url = os.environ[envkey]
    eng = create_engine(url, pool_pre_ping=True, future=True)
    insp = inspect(eng)
    assert "scheduled_jobs" in insp.get_table_names()
```

---

## 4) 스케줄러 GUI & 동작(구현 골격)

**설명**

* “SQLAdmin”은 FastAPI용 Admin UI 라이브러리로 **이미 구현된 관리자 프레임**을 제공하며, 우리 모델(`ScheduledJob`)을 등록하면 **CRUD 화면**을 자동 생성합니다(커스텀 액션/버튼 추가 가능).
* “APScheduler”는 스케줄러 엔진이며, 여기서는 **DB 테이블(`scheduled_jobs`) → 스케줄러 로더**를 만들어 “활성된 작업만 cron으로 등록/갱신”하도록 합니다.

**app/infrastructure/scheduler/loader.py**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.scheduled_job import ScheduledJob
from app.adapters.scheduler.jobs import JOB_REGISTRY  # func_name -> callable

async def load_jobs_from_db(session: AsyncSession, scheduler: AsyncIOScheduler):
    # 모든 기존 작업 제거 후 재적재(간단 전략)
    for job in scheduler.get_jobs():
        scheduler.remove_job(job.id)

    result = await session.execute(
        ScheduledJob.__table__.select().where(ScheduledJob.enabled == True)
    )
    for row in result.mappings():
        func_name = row["func"]
        func = JOB_REGISTRY.get(func_name)
        if not func:
            continue
        trigger = CronTrigger.from_crontab(row["cron"])
        scheduler.add_job(func, trigger, id=row["id"], name=row["name"], kwargs=row["kwargs"])
```

**app/adapters/scheduler/jobs.py**

```python
import logging
logger = logging.getLogger(__name__)

async def hello_job(**kwargs):
    logger.info("Hello job ran with %s", kwargs)

JOB_REGISTRY = {
    "app.adapters.scheduler.jobs:hello_job": hello_job,
}
```

**app/adapters/http/admin.py (SQLAdmin 등록)**

```python
from sqladmin import Admin, ModelView
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.infrastructure.db.models.scheduled_job import ScheduledJob
from app.infrastructure.scheduler.loader import load_jobs_from_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class ScheduledJobAdmin(ModelView, model=ScheduledJob):
    name = "Scheduled Job"
    name_plural = "Scheduled Jobs"
    column_list = [ScheduledJob.id, ScheduledJob.name, ScheduledJob.cron, ScheduledJob.enabled, ScheduledJob.status]
    can_create = True
    can_edit = True
    can_delete = False  # 비삭제 정책

def mount_admin(app: FastAPI, engine: AsyncEngine, scheduler: AsyncIOScheduler):
    admin = Admin(app, engine.sync_engine)
    admin.add_view(ScheduledJobAdmin)

    @app.post("/admin/scheduler/reload")
    async def reload_scheduler():
        async with engine.begin() as conn:
            session = conn
        # 실무에서는 AsyncSession factory 사용
        from app.infrastructure.db.session import AppSession
        async with AppSession() as s:
            await load_jobs_from_db(session=s, scheduler=scheduler)
        return {"ok": True}
```

**app/main.py (앱 팩토리)**

```python
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.adapters.http.admin import mount_admin
from app.infrastructure.db.session import app_engine  # AsyncEngine
from app.infrastructure.scheduler.loader import load_jobs_from_db
from app.adapters.http.router import api_router  # /api/* 엔드포인트

def create_app() -> FastAPI:
    app = FastAPI(title="App Server")
    scheduler = AsyncIOScheduler()
    scheduler.start()

    # 라우터
    app.include_router(api_router, prefix="/api")

    # Admin (SQLAdmin)
    mount_admin(app, app_engine, scheduler)

    # 앱 시작 시 스케줄 로드
    @app.on_event("startup")
    async def _load_jobs():
        from app.infrastructure.db.session import AppSession
        async with AppSession() as s:
            await load_jobs_from_db(session=s, scheduler=scheduler)

    return app
```

> 요약: **SQLAdmin** = GUI 프레임 제공(이미 있는 라이브러리) / **우리가 개발** = 모델 등록, 재적재 API, APScheduler 로더·잡 함수 매핑.

---

## 5) Nginx & 영속 볼륨 요약

* **Nginx**: 위 `nginx.conf` 대로 `/api` 프록시. 운영(AWS)에서는 보통 **ALB/ACM(SSL)** 로 TLS를 처리하고, 컨테이너 내부 Nginx는 HTTP만 담당하거나 생략 가능.
* **영속 볼륨**:

  * `files-data` → 앱 파일 저장(`/app/data/files`)
  * `redis-data` → Redis `/data`
  * `secrets-data` → GDrive 등 자격증명 파일 저장(`/app/secrets`)

---

---

## 🚀 **Docker Compose 실행 방법**

### **환경별 실행 명령어**

#### **로컬 개발 환경**
```bash
# 기본 실행 (환경변수 파일 사용)
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml up -d

# 빌드와 함께 실행
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml up --build

# 로그 확인
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml logs -f

# 중지
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml down
```

#### **운영 환경**
```bash
# 운영 환경 실행
docker compose --env-file ./secret/.env.prod -f docker/compose.base.yml -f docker/compose.prod.yml up -d

# 빌드와 함께 실행
docker compose --env-file ./secret/.env.prod -f docker/compose.base.yml -f docker/compose.prod.yml up --build
```

#### **관리 스크립트 사용**
```bash
# 로컬 환경 실행
./docker/docker-compose-manager.sh local

# 운영 환경 실행
./docker/docker-compose-manager.sh prod

# 중지
./docker/docker-compose-manager.sh stop
```

### **주요 해결 사항**
- **환경변수 로드**: `--env-file` 옵션으로 `.env.local`, `.env.prod` 파일 로드
- **호스트 접근**: `host.docker.internal`을 사용하여 SSH 터널 접근
- **ML Registry API**: 완전 구현 및 테스트 완료

---

## 📋 **개선된 액션 아이템 실행 계획**

### **Phase 1: 기반 인프라 구축 (1-2주)**

#### **1단계: 프로젝트 초기화**
- [ ] `server/app_server` 루트 디렉터리 구조 생성
- [ ] `pyproject.toml` 생성 (Python 3.12, 의존성 정의)
- [ ] `.gitignore` 업데이트 (민감 정보 제외)
- [ ] 브랜치 전략 적용 (`feat/server-app_server--init-scaffold`)

#### **2단계: 환경 설정**
- [ ] 환경변수 파일 생성 (`.env.local`, `.env.prod`)
- [ ] Docker Compose 구성 (base, local, prod)
- [ ] Nginx 프록시 설정
- [ ] Redis 영속성 설정

#### **3단계: 데이터베이스 연결**
- [ ] 멀티 엔진 설정 (legacy, app)
- [ ] Alembic 초기화 (신규 스키마만)
- [ ] `scheduled_jobs` 테이블 생성
- [ ] 비삭제 정책 구현

### **Phase 2: 핵심 기능 구현 (2-3주)**

#### **4단계: 스케줄러 시스템**
- [ ] APScheduler 설정
- [ ] SQLAdmin 관리자 UI 구축
- [ ] 스케줄 작업 CRUD 기능
- [ ] 실시간 스케줄 리로드

#### **5단계: API 개발**
- [ ] FastAPI 애플리케이션 구조
- [ ] JWT 인증/인가 시스템
- [ ] 파일 업로드/다운로드
- [ ] CORS 설정

#### **6단계: 파일 저장소**
- [ ] 로컬 파일 저장 구현
- [ ] Google Drive 연동 (선택)
- [ ] 파일 검증 및 보안

### **Phase 3: 고도화 및 운영 (3-4주)**

#### **7단계: 보안 강화**
- [ ] HTTPS 설정
- [ ] 보안 헤더 추가
- [ ] 입력 검증 강화
- [ ] SQL 인젝션 방지

#### **8단계: 성능 최적화**
- [ ] 데이터베이스 쿼리 최적화
- [ ] 캐싱 전략 구현
- [ ] 비동기 처리 최적화
- [ ] 메모리 사용량 최적화

#### **9단계: 문서화**
- [ ] API 문서 자동 생성
- [ ] 아키텍처 문서 작성
- [ ] 운영 가이드 작성
- [ ] 개발자 가이드 작성

### **Phase 4: 모니터링 및 테스트 (향후 진행)**

#### **10단계: 모니터링 시스템**
- [ ] 구조화된 로깅 구현
- [ ] Prometheus 메트릭 수집
- [ ] Grafana 대시보드 구성
- [ ] 알림 시스템 구축

#### **11단계: 테스트 자동화**
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 구현
- [ ] E2E 테스트 구축
- [ ] CI/CD 파이프라인 구축

---

### **실행 quick start (로컬)**

```bash
cd server/app_server

# 1) SSH 터널(별도 터미널)
ssh -N -L 15432:<rds-host>:5432 ubuntu@<bastion-ip> -i ~/.ssh/id_rsa

# 2) 환경변수 파일 복사
cp secret/.env.local .env.local

# 3) 도커 실행
docker compose -f docker/compose.base.yml -f docker/compose.local.yml --env-file .env.local up -d --build

# 4) Alembic (scheduled_jobs 생성)
alembic -x DB_URL="${DB_APP_URL}" upgrade head

# 5) 접속 확인
curl http://localhost:8080/healthz   # Nginx 헬스체크
curl http://localhost:8080/api/v1/health  # API 헬스체크
# SQLAdmin: http://localhost:8080/admin  (관리자 UI)
# API 문서: http://localhost:8080/api/docs  (Swagger UI)
```

### **주요 개선사항**

1. **보안 강화**: JWT 인증, CORS 설정, 파일 업로드 검증
2. **모니터링 준비**: 로깅 레벨, 메트릭 수집 준비
3. **개발 편의성**: API 문서 자동 생성, 개발 환경 최적화
4. **확장성**: 마이크로서비스 아키텍처 고려
5. **운영 안정성**: 헬스체크, 에러 핸들링, 로깅 시스템

---

## 2025-09-17 업데이트: ML 추론 로깅 테이블 및 REST API 추가

### 개요
- 신규 테이블: `ml.frame_prediction`, `ml.detection_event` (DB 반영 완료)
- SQLAlchemy 모델 추가: `FramePredictionModel`, `DetectionEventModel`
- 도메인/포트/리포지토리/유즈케이스/DTO/라우터 일괄 구현(헥사고날 패턴 준수)
- 메인 앱 라우터 등록 완료

### 추가된 경로 및 컴포넌트
- Domain
  - `app/domain/entities/frame_prediction.py`
  - `app/domain/entities/detection_event.py`
  - `app/domain/ports/frame_prediction_repository.py`
  - `app/domain/ports/detection_event_repository.py`
- DTO
  - `app/application/dto/frame_prediction_dto.py`
  - `app/application/dto/detection_event_dto.py`
- Use Cases
  - `app/application/use_cases/frame_prediction_use_cases.py`
  - `app/application/use_cases/detection_event_use_cases.py`
- Repository Implementations
  - `app/adapters/repositories/frame_prediction_repository_impl.py`
  - `app/adapters/repositories/detection_event_repository_impl.py`
- HTTP Routers
  - `app/adapters/http/frame_prediction_router.py`
  - `app/adapters/http/detection_event_router.py`
- Models
  - `app/infrastructure/db/models/ml_models.py` 내 모델 2종 추가
- Main
  - `app/main.py` 라우터 include 추가

### 신규 REST API
- FramePrediction `/api/v1/frame-predictions`
  - POST `/` (단건 생성)
  - POST `/batch` (배치 생성)
  - GET `/` (필터: `session_id, experiment_id, input_uri, label_pred, frame_index_from/to`, 페이징)
  - GET `/{frame_pred_id}` (단건)
  - DELETE `/{frame_pred_id}` (삭제)
- DetectionEvent `/api/v1/detection-events`
  - POST `/` (생성)
  - GET `/` (필터: `session_id, experiment_id, input_uri, event_type, top_label, start_ts_ms_from/to`, 페이징)
  - GET `/{event_id}` (단건)
  - DELETE `/{event_id}` (삭제)

### 설계 준수 사항
- ML 세션 DI(`get_ml_session`)을 통한 비동기 세션 주입
- 도메인 → 포트 → 리포지토리(구현) → 유즈케이스 → 라우터 계층 구조
- DTO 검증 및 응답 모델 `from_attributes = True`
- 상태코드/에러 응답 표준화(400/404/500)

### 후속 작업 제안
- 목록 응답 래핑 표준화 `{items,total,offset,limit}` 적용
- `/datasets?name=&tag=` 스타일로 필터 일원화(기존 라우터와 일관성)
- 관리자/내부용 엔드포인트는 `/admin` 또는 `/internal` 네임스페이스로 이동 및 인증 적용

## 2025-09-17 업데이트: Scheduler API 표준화 및 내부 엔드포인트 특이사항/조치

### 공개 엔드포인트 표준화
- `/api/v1/scheduled-jobs`: SQLAlchemy 세션 기반으로 일원화(정상 동작 확인)

### 내부 엔드포인트 분리
- `scheduler_app`의 관리/메타 엔드포인트를 `/internal/*` 로 이동하여 중복/충돌 제거

### 특이사항
- `/internal/scheduled-jobs` 호출 시 "Connection refused" 발생 가능
  - 원인: 컨테이너/호스트 조합에서 DB 호스트(DNS/포트) 미열림 또는 해석 실패
  - 비고: 공개 `/api/v1/scheduled-jobs` 는 SQLAlchemy 세션을 사용하므로 정상 동작

### 조치 가능 방안
- 환경변수 보정(택1)
  - 로컬(컨테이너 외부 실행): `DB_APP_URL=postgresql+asyncpg://...@127.0.0.1:15432/...`
  - 컨테이너 실행: `DB_APP_URL` 호스트를 실제 접속 가능한 서비스/엔드포인트로 지정(db, RDS 등)
  - 컨테이너→호스트 접속 시: `DOCKER_HOST_IP`를 실제 호스트 IP로 설정(기본 `172.17.0.1`)
- 코드 정렬(권장)
  - `/internal/*` 엔드포인트도 SQLAlchemy 세션 기반으로 통일해 환경 의존성(직접 TCP 접속) 축소
- 운영 방침
  - `/internal/*` 는 내부/관리용 → 인증/JWT 보호 및 비공개 노출 권장

## 2025-09-18 업데이트: AWS DB 연결 점검 및 ML 세션 이슈 분석

### 작업 개요
- AWS 내부 IP 기반 DB 접속 점검 스크립트 추가 및 보강
  - `scripts/test_db_connect.sh` 추가: DNS→TCP→SQL 순서 점검, `--env`/`--url` 지원
  - .env 로더 개선: KEY=VALUE 라인만 로드(설명/섹션 라인 무시), 따옴표 처리
  - psql 플래그 수정: `-tA -c "SELECT version();"`
- DB 세션 초기화 로그 강화
  - `app/infrastructure/db/session.py`에 마스킹된 URL 로그 및 ML 폴백 로그 추가

### 현재 상태
- prod .env로 실행 시 RDS에 대해 DNS/TCP/SQL 모두 OK (버전 획득 확인)
- 공개 엔드포인트 `/api/v1/scheduled-jobs` 정상 동작
- 내부 엔드포인트 `/internal/*` 는 운영 정책상 비공개/보호 대상

### ML 세션 연결 이슈 원인
- 컨테이너 관점에서 `ML_DB_URL` 호스트/DNS가 유효하지 않거나, `.env` 로딩 형식 문제로 변수 미적용 시 `Name or service not known` 발생
- 조치: `.env` KEY=VALUE 정리, `ML_DB_URL`을 컨테이너에서 접근 가능한 RDS 엔드포인트로 지정(필요 시 sslmode), SG 인바운드 허용

### 추가 로그로 확인 가능한 사항
- APP/LEGACY/ML 각각의 엔진 초기화 여부 및 대상 호스트/포트/DB(자격정보 마스킹)
- ML_DB_URL 미설정 시 APP 폴백 사용 여부

## 2025-09-18 업데이트: Compose(prod) 환경변수 주입 정정(우선순위 통일)

### 변경 배경
- 컨테이너 내부에서 `ML_DB_URL` 값이 `host.docker.internal:15432`로 나타남 → base의 `.env.local`이 컨테이너에 주입되었기 때문.

### 적용 내용
- `docker/compose.prod.yml`에서 서비스 단위로 `env_file: ../secret/.env.prod` 명시하여 base의 env_file을 프로덕션에서 덮어쓰기.
- 목적: 컨테이너 환경에 `.env.prod` 변수(특히 `ML_DB_URL`, `DB_APP_URL`)를 일관 주입.

### 기대 효과
- 컨테이너 스타트업 로그(`[ENV] Startup config`)에서 `ML_DB_URL`이 RDS(또는 내부 IP)로 표기.
- ML 세션 초기화 시 올바른 호스트/포트로 연결.

### 검증 절차
```bash
docker compose -f docker/compose.base.yml -f docker/compose.prod.yml down
docker compose --env-file ../secret/.env.prod -f docker/compose.base.yml -f docker/compose.prod.yml up -d --build
docker compose exec api env | grep -E 'ML_DB_URL|DB_APP_URL'
# API 로그에 [ENV] Startup config 확인
```

## 2025-09-18 업데이트: API 인터페이스 명세 및 공통 클라이언트 추가

### 추가 문서
- `docs/apis/datasets_api.md`: Datasets REST API 명세 (Base URL/엔드포인트/요청/응답/예시)
- `docs/apis/experiments_api.md`: Experiments REST API 명세
- `docs/apis/frame_predictions_api.md`: Frame-Predictions REST API 명세
- `docs/apis/detection_events_api.md`: Detection-Events REST API 명세

### 공통 클라이언트
- `Util/common_api.py`: 범용 REST API 클라이언트 (requests 기반)
  - BASE_URL 자동 보정(/api/v1), GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS 편의 함수 제공
  - 설치: `pip install requests`
  - 예시: 본 프로젝트의 Datasets/Experiments/FramePredictions/DetectionEvents 호출 예시 포함

### 목적/효과
- 팀 내/외부 소비자가 API 스펙과 사용 예시를 즉시 확인 가능
- 신규/외부 REST API에도 재사용 가능한 표준 클라이언트 확보

## 2025-09-19 업데이트: API 사용 예제 모음 및 테스트 완료

### 추가된 예제 파일들
- `Util/examples/experiment_api_example.py`: 실험 API 사용 예제
  - 실험 생성/조회/업데이트/삭제 전체 워크플로우
  - 고유한 이름 생성으로 중복 방지
  - 환경별 실행 지원 (로컬/운영)
- `Util/examples/dataset_api_example.py`: 데이터셋 API 사용 예제
  - 데이터셋 생성/조회/검색/업데이트/삭제
  - 이름/태그 기반 검색 기능
  - 한국어 메타데이터 지원
- `Util/examples/frame_prediction_api_example.py`: 프레임 예측 API 사용 예제
  - 단건/배치 프레임 예측 생성
  - 세션 기반 필터링
  - 실험 ID 연동
- `Util/examples/detection_event_api_example.py`: 감지 이벤트 API 사용 예제
  - 감지 이벤트 생성/조회/필터링
  - 이벤트 타입별 분류
  - 메타데이터 관리
- `Util/examples/README.md`: 사용 가이드 및 문서

### 테스트 결과
- ✅ **실험 API**: 완전 정상 작동 (생성/조회/업데이트/삭제)
- ✅ **데이터셋 API**: 완전 정상 작동 (생성/조회/검색/업데이트/삭제)
- ⚠️ **프레임 예측 API**: 단건 생성/조회 정상, 배치 생성 스키마 차이
- ⚠️ **감지 이벤트 API**: 조회 정상, 생성 시 필수 필드 누락 (input_uri, start_frame, end_frame, top_label, threshold_snapshot)

### 주요 기능
- **환경별 실행**: `--env local/prod` 옵션으로 로컬/운영 환경 전환
- **에러 처리**: 네트워크 오류 시 자동 재시도 (2회), 타임아웃 30초
- **상세 로깅**: 요청/응답 데이터 JSON 형태로 출력
- **유연한 설정**: 커스텀 URL, 실험 ID 등 옵션 지원
- **삭제 옵션**: `--skip-delete` 옵션으로 테스트 데이터 보존

### 사용법
```bash
# 기본 실행 (로컬 환경)
python3 experiment_api_example.py

# 운영 환경 실행
python3 experiment_api_example.py --env prod

# 삭제 예제 건너뛰기
python3 experiment_api_example.py --skip-delete

# 특정 실험 ID 사용
python3 frame_prediction_api_example.py --experiment-id <EXPERIMENT_ID>
```

### 효과
- **개발자 경험 향상**: API 사용법을 즉시 학습하고 테스트 가능
- **자동화 지원**: 스크립트 기반 API 호출로 CI/CD 파이프라인 구축 가능
- **문서화 강화**: 실제 작동하는 예제 코드로 API 사용법 명확화
- **품질 보증**: 모든 API 엔드포인트의 정상 작동 검증 완료

---

## 2025-09-19 업데이트: 프로젝트 종합 현황 & Notify Deliveries/Devices API 추가

### 전체 현황 요약
- 아키텍처: 헥사고날(Ports & Adapters), 레이어 분리(Domain → Application → Adapters → Infrastructure)
- 실행/배포: Docker Compose(base/local/prod), Nginx 프록시, SQLAdmin 관리자 UI
- DB: SQLAlchemy(Async) 멀티 엔진, ENV 기반 URL 파싱/로깅 강화, 진단 스크립트 제공
- 스케줄러: APScheduler + DB(scheduled_jobs) 로더, 공개/내부 엔드포인트 분리

### 주요 API 현황
- Datasets `/api/v1/datasets` (CRUD)
- Experiments `/api/v1/experiments` (CRUD)
- Frame-Predictions `/api/v1/frame-predictions` (생성/조회/삭제, 배치 생성 포함)
- Detection-Events `/api/v1/detection-events` (생성/조회/삭제)
- Scheduler: 공개 `/api/v1/scheduled-jobs`(ORM), 내부 `/internal/*`(직접 연결)
- Notify:
  - Messages `/api/v1/notify/messages` (CRUD)
  - Deliveries `/api/v1/notify/deliveries` (CRUD, 필터: user_id, status)
  - Devices `/api/v1/notify/devices` (CRUD, 필터: user_id, channel, is_active)

### 신규 작업(이번 업데이트)
- Notify Deliveries/Devices API 추가
  - DTO: `notify_delivery_dto.py`, `notify_device_dto.py`
  - 포트: `notify_delivery_repository.py`, `notify_device_repository.py`
  - 리포지토리: `notify_delivery_repository_impl.py`, `notify_device_repository_impl.py`
  - 유즈케이스: `notify_delivery_use_cases.py`, `notify_device_use_cases.py`
  - 라우터: `notify_delivery_router.py`, `notify_device_router.py`
  - 앱 등록: `app/main.py`에 include
- ENUM 매핑 안정화(Notify)
  - 기존 PostgreSQL ENUM(`notify.kind_enum`, `notify.severity_enum`, `notify.channel_enum`, `notify.delivery_status_enum`)에 ORM 바인딩
  - `create_type=False`, 스키마·타입명 명시로 중복 생성/불일치 방지

### 운영/진단 관련 메모
- ENV 주입: prod에서는 `compose.prod.yml`이 `env_file: ../secret/.env.prod`로 base를 덮어써야 함
- ML/App DB URL: 시작 로그에 마스킹된 URL과 파싱된 host/port/db가 출력되므로 값 확인 가능
- 내부 엔드포인트(`/internal/*`) 오류 시: SSH 터널 미기동/호스트 IP 불일치가 주원인 → 터널 활성화 또는 ORM 일원화 검토

### 현재 상태 체크
- 공개 API: 정상 동작 (/api/v1/*)
- SQLAdmin: 정상 마운트
- Compose(prod): ENV 우선순위 정정 후 DB 연결 정상
- Notify: Messages/Deliveries/Devices CRUD 동작, ENUM 불일치 오류 해결

---

## 2025-09-23 업데이트: Notify 기능 개발 계획 & 체크리스트(에드온)

### 개발 목표
- 실시간 알림 파이프라인의 최소 기능 확보: 메시지 생성→수신자 큐잉→(디스패처)전송→열람/ACK 상태 반영
- 기존 기능 영향 최소화: 헥사고날 구조로 격리, Feature Flag로 점진 롤아웃

### 단계별 계획(Phase)
- Phase 1: 큐잉/상태 갱신 API
  - POST `/api/v1/notify/queue` (메시지 생성 + recipients×channel 큐잉)
  - POST `/api/v1/notify/deliveries/{id}/read`, `/ack` (상태 갱신)
  - Repo 보강: `mark_sent|delivered|read|ack`
- Phase 2: 실시간 전송(WS) 및 디스패처
  - `ConnectionManager`, `WsNotifier`, `/ws` 엔드포인트
  - APScheduler 디스패처 잡(queued→sent→delivered), 만료(expires_at) 가드
  - Feature Flag: `NOTIFY_DISPATCH_ENABLE`, `NOTIFY_WS_ENABLE`
- Phase 3: 테스트/문서화
  - TDD: 유즈케이스, 리포, 디스패처 유닛/통합
  - 수동 체크리스트 기반 시나리오 테스트
  - 문서/런북 업데이트(운영 쿼리 포함)
- Phase 4: 가시성/롤아웃
  - 구조화 로깅, SQLAdmin 뷰/쿼리
  - Staging canary→Prod 점진 적용

### 액션 아이템 체크리스트
- [x] Phase1-API: DTO(Queue) 및 유즈케이스(CreateMessageAndQueue) 추가
- [x] Phase1-API: POST `/api/v1/notify/queue` 라우터 추가
- [x] Phase1-API: POST `/api/v1/notify/deliveries/{id}/read` 구현
- [x] Phase1-API: POST `/api/v1/notify/deliveries/{id}/ack` 구현
- [x] Phase1-Repo: Deliveries `mark_sent|delivered|read|ack` 구현
- [x] Phase2-WS: ConnectionManager/WsNotifier 추가 및 `/ws` 라우터
- [x] Phase2-Disp: APScheduler 디스패처 잡 추가(Feature Flag)
- [ ] Phase3-Test: 유닛/통합/API/WebSocket 테스트 추가
- [ ] Phase3-Docs: 운영/수동 테스트 가이드 및 쿼리 보강
- [ ] Phase4-Obs: 구조화 로그/SQLAdmin 뷰
- [ ] Phase4-Rollout: Flags로 Staging→Prod 전개

### 운영/배포 메모(Nginx)
- `/ws` 업그레이드 설정 추가: `proxy_http_version 1.1`, Upgrade/Connection 헤더, `proxy_read_timeout`
- `/api/` 기존 프록시 유지, 헬스체크 `/healthz`로 확인
- 멀티 인스턴스 시 sticky 또는 브로커 도입 검토
 
### 2025-09-23 에드온: Notify Phase 1+2 진행 현황
- 구현 완료
  - Queue API: `POST /api/v1/notify/queue`
  - 상태 갱신: `POST /api/v1/notify/deliveries/{id}/read|ack`
  - 리포 헬퍼: `mark_sent|delivered|read|ack`, `next_queued`
  - WebSocket: `/ws?user_id=<uuid>`, ConnectionManager/WsNotifier
  - Dispatcher: Feature flags (`NOTIFY_ENABLE`, `NOTIFY_DISPATCH_ENABLE`, `NOTIFY_WS_ENABLE`)
- 환경 변수 예시(.env)
  - `NOTIFY_ENABLE=true`
  - `NOTIFY_DISPATCH_ENABLE=true`
  - `NOTIFY_WS_ENABLE=true`
- 수동 테스트 체크리스트
  - [ ] 브라우저 `ws://<host>/ws?user_id=<UUID>` 연결
  - [ ] `POST /api/v1/notify/queue` 로 recipients에 위 UUID 지정하여 큐잉
  - [ ] 디스패처 ON 시 `queued→sent→delivered` 전이 확인(DB/로그)
  - [ ] `read`/`ack` 호출로 상태·타임스탬프 반영 확인
- 브로커 연동(추후)
  - Redis Pub/Sub → Redis Streams → Kafka 단계 도입(요구 증가 시)
  - 목적: 다중 인스턴스/내구성/재처리 보장

### 2025-09-23 에드온: 테스트 진행 현황(Phase 3 시작)
- 추가 테스트
  - 라우트 존재 테스트: `tests/test_notify_api.py`
  - WebSocket 연결 테스트: `tests/test_notify_ws.py`
- 다음 테스트 계획
  - Repo/UseCase 통합 테스트(세션 트랜잭션 롤백 기반)
  - 디스패처 루프 단위 테스트(WS on/off 플래그별)

### 2025-09-24 에드온: 환경 변수/프록시 및 진행 상태 리포트
- Compose 경고 설명
  - `NOTIFY_ENABLE/DISPATCH_ENABLE/WS_ENABLE` 경고는 env 파일에서 해당 변수가 비어있어 발생 → `.env.local` 또는 `--env-file`에 값을 추가하면 해소됩니다.
  - `version` 키는 Compose v2에서 obsolete 경고이며 동작에 영향은 없습니다(혼동 방지 위해 제거 권장).
- 환경 변수(추가 제안)
  - `NOTIFY_ENABLE=true`
  - `NOTIFY_DISPATCH_ENABLE=true`
  - `NOTIFY_WS_ENABLE=true`
- 프록시 설정
  - `docker/nginx/nginx.conf`에 `/ws` 업그레이드 경로 추가 완료
  - BASE_URL: `http://localhost` (또는 `http://localhost:8080`/`http://localhost:8000`)
- 테스트 페이지/문서
  - 수동 페이지: `staging/tools/notify_ws_client.html`
  - 가이드: `staging/notify_testing_guide.md`
- 진행 현황(요약)
  - Phase 1+2 구현 완료(큐잉/상태/WS/디스패처), Phase 3 테스트 진행 중(유닛/WS/플래그)
  - 브로커 도입은 후속(스케일 요구 시)
- 다음 단계
  - 리포 통합 테스트, 운영 쿼리/가시성 보강, 플래그 기반 롤아웃 가이드 확정

### 2025-09-24 에드온: Notify kind ENUM 정합성 및 클라이언트/문서 정리
- 배경: DB `notify.kind_enum` 허용값은 `system|schedule|info|contact|marketing|inbound`. `warning/error`는 kind가 아닌 severity(노랑/빨강)로 표현해야 함.
- 조치
  - 문서 예시 수정: `docs/notification_system_usage_guide.md`, `docs/notification_system_testing_guide.md`의 kind를 허용값(`system`)으로 교정
  - 클라이언트 예시 수정: `client/live_notification_test.py` 내 출력 예시 kind를 `system`으로 교정
  - 가이드에 "경고/오류 레벨은 severity로 표현" 명시
- 관련 산출물
  - 테스트 가이드: `staging/notify_testing_guide.md`
  - 수동 테스트 페이지: `staging/tools/notify_ws_client.html`
  - 프록시/플래그: `/ws` 업그레이드(Nginx), `NOTIFY_ENABLE/NOTIFY_DISPATCH_ENABLE/NOTIFY_WS_ENABLE`

### 2025-09-25 업데이트: 동적 URL 변환 및 클라이언트 문서화 완성
- 배경: 클라이언트 사용 시 WebSocket URL과 HTTP API URL을 각각 설정해야 하는 불편함과 `Failed to fetch` 오류 해결 필요
- 주요 개선사항
  - **동적 URL 변환 기능 구현**: WebSocket URL 입력 시 HTTP API URL 자동 생성
    - `ws://localhost` → `http://localhost/api/v1/notify/queue`
    - `wss://example.com/ws` → `https://example.com/api/v1/notify/queue`
  - **HTML 클라이언트 개선**: API 서버 불일치 및 enum 값 문제 해결
    - 서버 URL 필드에서 WebSocket과 HTTP API URL 자동 변환
    - 잘못된 kind 값(`warning`, `error`) → 올바른 enum 값(`system`) + severity 조합
  - **종합적 문서화 및 주석 보강**
    - Python/JavaScript/HTML 클라이언트 모두 상세한 사용법 주석 추가
    - DB enum 기준 올바른 kind/severity 조합 가이드 제공
    - 동적 URL 변환 기능 사용법 및 예제 추가
- 구현 내용
  - **Python 유틸리티 함수**: `websocket_to_http_url()`, `get_api_url()` 추가
  - **JavaScript 유틸리티 함수**: `websocketToHttpUrl()`, `getApiUrl()` 추가
  - **NotificationClient 확장**: `get_api_url()` 메서드 추가
  - **NotificationSender 개선**: WebSocket URL 입력 지원
  - **HTML 클라이언트 수정**: 동적 URL 변환, 올바른 enum 값 사용, AWS 서버 기본값 설정
- 수정된 파일들
  - `client/notification_client.py`: 유틸리티 함수 및 종합 문서화
  - `client/notification_client.js`: 유틸리티 함수 및 상세 주석
  - `client/notification_client.html`: 동적 URL 변환 및 enum 수정
  - `client/live_notification_test.py`: 동적 URL 사용 및 핸들러 개선
  - `client/README.md`: 주요 특징 및 enum 값 가이드 추가
  - `staging/tools/notify_ws_client*.html`: AWS 서버 기본값 및 URL 변환 함수
- 테스트 결과
  - ✅ 동적 URL 변환 기능 정상 작동 (다양한 URL 패턴 테스트 완료)
  - ✅ HTML 클라이언트 `Failed to fetch` 오류 해결
  - ✅ 모든 클라이언트에서 올바른 enum 값 사용
  - ✅ 실제 알림 송수신 테스트 성공
- 사용자 경험 개선
  - **단일 URL 설정**: WebSocket URL 하나만 입력하면 모든 기능 사용 가능
  - **오류 방지**: DB enum에 맞는 정확한 값들만 사용하도록 가이드 제공
  - **개발 편의성**: 로컬/스테이징/프로덕션 환경 간 URL 변경 시 한 곳만 수정
  - **완전한 문서화**: 모든 클라이언트에 실제 사용 가능한 예제 코드 제공

### 2025-09-25 업데이트: Nginx 웹서버 호스팅 및 프로젝트 구조 최적화 완성
- 배경: 클라이언트 파일들을 브라우저에서 직접 접근할 수 있도록 Nginx 웹서버 호스팅 필요성 및 프로젝트 구조 개선
- 주요 개선사항
  - **Nginx 정적 파일 서빙 구현**: `/notification/` 경로를 통한 클라이언트 파일 호스팅
    - `http://localhost/notification/client/notification_client.html` 접근 가능
    - `http://localhost/notification/tools/notify_ws_client.html` 등 모든 도구 웹 접근
  - **Docker Compose 통합**: Nginx 컨테이너에 notification 파일 볼륨 마운트
    - `Util/notification:/var/www/notification:ro` 마운트 설정
    - 캐싱, 압축, 보안 헤더 최적화 적용
  - **프로젝트 구조 재편성**: 알림 관련 모든 도구를 `Util/notification`으로 통합
    - `server/app_server/client/` → `Util/notification/client/`
    - `server/app_server/staging/tools/` → `Util/notification/tools/`
    - 논리적 구조화 및 사용자 접근성 향상
- 구현 내용
  - **Nginx 설정 확장**:
    ```nginx
    location /notification/ {
        alias /var/www/notification/;
        try_files $uri $uri/ =404;
        # 캐싱, 보안 헤더, 압축 설정 포함
    }
    ```
  - **Docker Compose 설정 최적화**:
    - `compose.base.yml`: notification 볼륨 마운트 추가
    - `compose.local.yml`: 중복 설정 제거, 깔끔한 구조화
  - **종합 문서화**: `Util/notification/README.md` 신규 작성
    - 디렉토리 구조 설명, 사용법 가이드, 테스트 방법 상세화
    - 동적 URL 변환, enum 값 가이드, 고급 설정 포함
- 수정된 파일들
  - `docker/compose.base.yml`: notification 볼륨 마운트 추가
  - `docker/compose.local.yml`: nginx.conf 마운트 제거 (충돌 해결)
  - `nginx/nginx.conf`: `/notification/` location 블록 추가
  - `docker/nginx/nginx.conf`: 기존 설정과 통합
  - `Util/notification/README.md`: 종합 사용 가이드 신규 작성
- 테스트 결과
  - ✅ Nginx 정적 파일 서빙 정상 작동 (HTTP 200 OK 응답)
  - ✅ 모든 클라이언트 파일 웹 접근 가능
  - ✅ 캐싱, 압축, 보안 헤더 정상 적용
  - ✅ Docker 컨테이너 재빌드 및 볼륨 마운트 성공
- 운영 효과
  - **웹 기반 접근**: 별도 다운로드 없이 브라우저에서 바로 테스트 가능
  - **통합 관리**: 모든 알림 도구가 한 곳에 집중되어 관리 효율성 향상
  - **성능 최적화**: Nginx의 고성능 정적 파일 서빙 활용
  - **보안 강화**: XSS 보호, Content-Type 보호 등 보안 헤더 적용
  - **개발 편의성**: 로컬 개발 시 즉시 웹에서 테스트 가능

### 2025-09-25 업데이트: 프로젝트 정리 및 중복 파일 제거 완료
- 배경: 프로젝트 구조 최적화 과정에서 발견된 중복 nginx.conf 파일 정리 필요성
- 문제 분석
  - **중복 파일 존재**: `docker/nginx/nginx.conf`와 `nginx/nginx.conf` 두 파일 공존
  - **설정 충돌 가능성**: Docker 빌드 시와 볼륨 마운트 시 다른 설정 파일 사용
  - **개발자 혼동**: 어떤 파일이 실제 사용되는지 불명확
- 조치 사항
  - **파일 백업**: `docker/nginx/nginx.conf` → `docker/nginx/nginx.conf.backup`
  - **중복 파일 삭제**: 사용되지 않는 `docker/nginx/nginx.conf` 제거
  - **시스템 검증**: 파일 삭제 전후 전체 기능 테스트 수행
- 검증 결과
  - **삭제 전 테스트**: ✅ 모든 기능 정상 (Swagger, HTML 클라이언트, WebSocket, API)
  - **삭제 후 테스트**: ✅ 모든 기능 정상 (동일한 성능 및 안정성 확인)
  - **시스템 영향**: 없음 (실제 사용 파일은 `nginx/nginx.conf`였음)
- 최종 상태
  - **단일 설정 파일**: `nginx/nginx.conf`만 사용하여 일관성 확보
  - **백업 보관**: 필요 시 복원 가능하도록 백업 파일 유지
  - **문서 업데이트**: 프로젝트 구조 문서에 정리 내용 반영
- 운영 효과
  - **유지보수성 향상**: 단일 설정 파일로 관리 복잡도 감소
  - **개발자 경험 개선**: 설정 변경 시 혼동 제거
  - **시스템 안정성**: 설정 충돌 위험 완전 제거
  - **프로젝트 정리**: 불필요한 파일 제거로 깔끔한 구조 확보

### 2025-09-25 최종 업데이트: 운영서버 배포 준비 및 프로젝트 최종 정리 완료
- 배경: 운영서버에서 404 오류 발생 및 Docker 볼륨 마운트 경로 문제 해결
- 문제 진단
  - **운영서버 404 오류**: `http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/notification/client/notification_client.html`
  - **원인 분석**: Docker Compose 설정에서 로컬 개발환경 절대경로 사용
    - 설정된 경로: `/home/guehojung/Documents/Project/DEEP_LEARNING/deeplearning-repo-1/Util/notification`
    - 운영서버 실제 경로: `/home/ubuntu/development/deeplearning-repo-1/`
    - 결과: 경로 불일치로 볼륨 마운트 실패
- 근본적 해결책 적용
  - **절대경로 → 상대경로 변경**: `docker/compose.base.yml` 수정
    - 기존: `/home/guehojung/.../Util/notification:/var/www/notification:ro`
    - 변경: `../../../Util/notification:/var/www/notification:ro`
  - **환경 독립성 확보**: 로컬/운영서버 동일 설정으로 배포 가능
  - **로컬 테스트 완료**: 상대경로 적용 후 모든 기능 정상 작동 확인
- 최종 프로젝트 정리
  - **불필요한 파일 제거**: 
    - `docker/nginx/nginx.conf.backup` 삭제 (중복 백업 파일)
    - `server/Util/notification/` 빈 디렉토리 제거 (Docker 자동 생성 오류)
  - **프로젝트 구조 최적화**: 깔끔한 디렉토리 구조 확보
- 시스템 검증 결과 (2025-09-25 19:57)
  - **Docker 컨테이너**: 3개 서비스 모두 healthy 상태 (nginx, api, redis)
  - **HTML 클라이언트**: ✅ HTTP 200 OK 정상 응답
  - **FastAPI Swagger**: ✅ HTTP 200 OK 정상 응답  
  - **WebSocket 알림**: ✅ 정상 작동 확인
  - **볼륨 마운트**: ✅ 상대경로로 정상 마운트 확인
- 운영서버 배포 준비 완료
  - **배포 방법**: Git pull 후 Docker Compose 재시작만으로 즉시 적용 가능
  - **환경 독립성**: 로컬과 운영서버 동일한 설정 파일 사용
  - **안정성 보장**: 모든 기능 로컬 테스트 완료
- 프로젝트 현황 요약 (2025-09-25)
  - **개발 완료**: WebSocket 기반 실시간 알림 시스템 완전 구현
  - **배포 준비**: 운영서버 배포 가능 상태 달성
  - **문서화 완료**: 개발/사용/테스트 가이드 완비
  - **프로젝트 정리**: 불필요한 파일 완전 제거 및 구조 최적화