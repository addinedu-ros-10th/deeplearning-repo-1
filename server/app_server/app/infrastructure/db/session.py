"""
데이터베이스 세션 관리 모듈
멀티 엔진 지원 및 비삭제 정책 구현
"""

import os
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 매니저 - 멀티 엔진 지원"""
    
    def __init__(self):
        self.app_engine: Optional[Engine] = None
        self.legacy_engine: Optional[Engine] = None
        self.app_async_engine = None
        self.legacy_async_engine = None
        self.app_session_factory = None
        self.legacy_session_factory = None
        
    async def initialize(self):
        """데이터베이스 엔진 초기화"""
        try:
            # 신규 스키마용 엔진 (앱 전용)
            app_url = os.getenv('DB_APP_URL')
            if app_url:
                self.app_async_engine = create_async_engine(
                    app_url,
                    pool_size=int(os.getenv('DATABASE_POOL_SIZE', '20')),
                    max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '30')),
                    pool_pre_ping=True,
                    echo=os.getenv('DEBUG', 'false').lower() == 'true'
                )
                self.app_session_factory = async_sessionmaker(
                    self.app_async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                logger.info("신규 스키마 엔진 초기화 완료")
            
            # 레거시 스키마용 엔진 (읽기 전용)
            legacy_url = os.getenv('DB_LEGACY_URL')
            if legacy_url:
                self.legacy_async_engine = create_async_engine(
                    legacy_url,
                    pool_size=int(os.getenv('DATABASE_POOL_SIZE', '20')),
                    max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '30')),
                    pool_pre_ping=True,
                    echo=os.getenv('DEBUG', 'false').lower() == 'true'
                )
                self.legacy_session_factory = async_sessionmaker(
                    self.legacy_async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                logger.info("레거시 스키마 엔진 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 엔진 초기화 실패: {e}")
            raise
    
    async def close(self):
        """데이터베이스 연결 종료"""
        if self.app_async_engine:
            await self.app_async_engine.dispose()
        if self.legacy_async_engine:
            await self.legacy_async_engine.dispose()
        logger.info("데이터베이스 연결 종료 완료")
    
    def get_app_session(self) -> AsyncSession:
        """신규 스키마용 세션 반환 (쓰기 허용)"""
        if not self.app_session_factory:
            raise RuntimeError("신규 스키마 엔진이 초기화되지 않았습니다.")
        return self.app_session_factory()
    
    def get_legacy_session(self) -> AsyncSession:
        """레거시 스키마용 세션 반환 (읽기 전용)"""
        if not self.legacy_session_factory:
            raise RuntimeError("레거시 스키마 엔진이 초기화되지 않았습니다.")
        return self.legacy_session_factory()

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()

async def get_app_session() -> AsyncGenerator[AsyncSession, None]:
    """신규 스키마용 세션 의존성 주입"""
    session = db_manager.get_app_session()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"신규 스키마 세션 오류: {e}")
        raise
    finally:
        await session.close()

async def get_legacy_session() -> AsyncGenerator[AsyncSession, None]:
    """레거시 스키마용 세션 의존성 주입"""
    session = db_manager.get_legacy_session()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"레거시 스키마 세션 오류: {e}")
        raise
    finally:
        await session.close()

# 편의 함수들
async def get_app_engine():
    """신규 스키마 엔진 반환"""
    return db_manager.app_async_engine

async def get_legacy_engine():
    """레거시 스키마 엔진 반환"""
    return db_manager.legacy_async_engine

def get_sync_engine():
    """동기 엔진 반환 (SQLAdmin용)"""
    # 환경 변수에서 데이터베이스 URL 가져오기
    app_url = os.getenv('DB_APP_URL')
    if not app_url:
        raise ValueError("DB_APP_URL 환경 변수가 설정되지 않았습니다")
    
    # 동기 엔진 생성
    sync_engine = create_engine(
        app_url.replace('postgresql+asyncpg://', 'postgresql://'),
        pool_size=int(os.getenv('DATABASE_POOL_SIZE', '20')),
        max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '30')),
        pool_pre_ping=True,
        echo=os.getenv('DEBUG', 'false').lower() == 'true'
    )
    
    return sync_engine
