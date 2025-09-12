
---

# 액션 아이템 (업데이트 버전)

### 0. 프로젝트 루트 확정

* 작업 루트 디렉터리를 `server/app_server` 로 고정하고 모든 경로/도커 마운트를 여기를 기준으로 구성한다.

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
