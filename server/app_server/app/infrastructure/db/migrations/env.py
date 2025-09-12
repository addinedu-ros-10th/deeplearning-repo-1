import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from urllib.parse import quote_plus

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# 환경 변수 로딩
from dotenv import load_dotenv
load_dotenv()

# 모델 임포트 (신규 스키마만)
from app.infrastructure.db.models import Base

# Alembic 설정 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 신규 스키마 메타데이터만 사용 (비삭제 정책)
target_metadata = Base.metadata


def get_database_url():
    """데이터베이스 URL을 올바르게 구성"""
    db_url = os.getenv('DB_APP_URL')
    if not db_url:
        raise ValueError("DB_APP_URL 환경 변수가 설정되지 않았습니다.")
    
    # asyncpg를 psycopg2로 변경 (Alembic 호환성)
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    # URL 파싱하여 비밀번호 인코딩
    if '://' in db_url:
        scheme, rest = db_url.split('://', 1)
        if '@' in rest:
            user_pass, host_db = rest.split('@', 1)
            if ':' in user_pass:
                user, password = user_pass.split(':', 1)
                # 비밀번호 URL 인코딩
                password = quote_plus(password)
                user_pass = f"{user}:{password}"
            rest = f"{user_pass}@{host_db}"
        db_url = f"{scheme}://{rest}"
    
    return db_url


def run_migrations_offline() -> None:
    """오프라인 모드로 마이그레이션 실행"""
    context.configure(
        url="postgresql://svc_dev:IOT_dev_123%21%40%23@0.0.0.0:15432/iot_care",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 비삭제 정책을 위한 설정
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드로 마이그레이션 실행"""
    # 직접 연결 파라미터 사용
    connectable = engine_from_config(
        {
            "sqlalchemy.url": "postgresql://svc_dev:IOT_dev_123%21%40%23@0.0.0.0:15432/iot_care",
            "sqlalchemy.poolclass": "NullPool"
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # 비삭제 정책을 위한 설정
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    비삭제 정책을 위한 객체 필터링
    레거시 테이블은 제외하고 신규 스키마만 관리
    """
    # 테이블인 경우
    if type_ == "table":
        # 레거시 테이블 제외 (legacy_ 접두사)
        if name.startswith("legacy_"):
            return False
        # 시스템 테이블 제외
        if name in ["alembic_version"]:
            return True
        # 신규 스키마 테이블만 포함
        return True
    
    # 인덱스인 경우
    if type_ == "index":
        # 레거시 테이블의 인덱스 제외
        if name.startswith("ix_legacy_"):
            return False
        return True
    
    # 기타 객체는 포함
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
