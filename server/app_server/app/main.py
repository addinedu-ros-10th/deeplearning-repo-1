"""
통합된 FastAPI 메인 애플리케이션

모든 기능을 통합한 메인 애플리케이션:
- 스케줄러 기능
- SQLAdmin 관리자 패널
- 헥사고날 아키텍처 지원
- Docker Compose 환경 지원
"""

from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import unquote, urlparse

# 환경 변수 로딩
load_dotenv('secret/.env.local')

def create_app() -> FastAPI:
    """통합된 FastAPI 애플리케이션 팩토리 함수"""
    
    app = FastAPI(
        title="App Server API with Scheduler & Admin",
        description="IoT Care App Server with APScheduler, SQLAdmin, and Hexagonal Architecture",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 스케줄러 애플리케이션 임포트 및 설정
    from app.scheduler_app import router as scheduler_router, startup_event, shutdown_event
    
    # 스케줄러 애플리케이션의 라우터들을 메인 앱에 포함
    app.include_router(scheduler_router)
    
    # 스케줄러 이벤트 핸들러 포함
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    # SQLAdmin 관리자 패널 설정
    _setup_admin_panel(app)
    
    # 추가 API 엔드포인트 설정
    _setup_additional_endpoints(app)
    
    return app


def _setup_admin_panel(app: FastAPI) -> None:
    """SQLAdmin 관리자 패널 설정"""
    try:
        from app.admin.admin_app import admin_app
        admin_app.mount_to_app(app)
        print("✅ SQLAdmin 관리자 패널이 성공적으로 마운트되었습니다.")
    except Exception as e:
        print(f"⚠️ SQLAdmin 관리자 패널 마운트 실패: {e}")


def _setup_additional_endpoints(app: FastAPI) -> None:
    """추가 API 엔드포인트 설정"""
    
    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        return {
            "message": "App Server API with Scheduler & Admin",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "docs": "/docs",
            "admin": "/admin",
            "scheduler": "active",
            "features": [
                "APScheduler 스케줄러",
                "SQLAdmin 관리자 패널",
                "헥사고날 아키텍처 지원",
                "Docker Compose 환경 지원"
            ]
        }

    @app.get("/api/v1/tables")
    async def list_tables():
        """데이터베이스 테이블 목록 조회"""
        try:
            conn = await _get_db_connection()
            
            tables = await conn.fetch("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            await conn.close()
            
            return {
                "tables": [dict(table) for table in tables],
                "count": len(tables),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch tables: {str(e)}")

    @app.get("/api/v1/scheduled-jobs")
    async def get_scheduled_jobs():
        """스케줄 작업 목록 조회"""
        try:
            conn = await _get_db_connection()
            
            jobs = await conn.fetch("""
                SELECT id, name, func, cron, enabled, status, 
                       last_run_at, next_run_at, created_at
                FROM scheduled_jobs 
                WHERE is_deleted = false
                ORDER BY created_at DESC
            """)
            
            await conn.close()
            
            return {
                "jobs": [dict(job) for job in jobs],
                "count": len(jobs),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled jobs: {str(e)}")

    @app.get("/api/v1/database/info")
    async def get_database_info():
        """데이터베이스 정보 조회"""
        try:
            conn = await _get_db_connection()
            
            # 데이터베이스 버전
            version = await conn.fetchval("SELECT version()")
            
            # 테이블 개수
            table_count = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            # scheduled_jobs 테이블 통계
            job_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN enabled = true THEN 1 END) as enabled_jobs,
                    COUNT(CASE WHEN status = 'idle' THEN 1 END) as idle_jobs,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_jobs
                FROM scheduled_jobs 
                WHERE is_deleted = false
            """)
            
            await conn.close()
            
            return {
                "database_version": version,
                "table_count": table_count,
                "scheduled_jobs_stats": dict(job_stats),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch database info: {str(e)}")

    @app.get("/api/v1/admin/info")
    async def get_admin_info():
        """관리자 패널 정보 조회"""
        return {
            "admin_url": "/admin",
            "features": [
                "스케줄 작업 관리",
                "작업 생성/수정/삭제",
                "실시간 상태 모니터링",
                "Cron 표현식 검증"
            ],
            "available_models": [
                "ScheduledJob"
            ],
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/api/v1/architecture/info")
    async def get_architecture_info():
        """아키텍처 정보 조회"""
        return {
            "architecture": "hybrid",
            "patterns": [
                "Factory Pattern",
                "Dependency Injection",
                "Hexagonal Architecture (partial)",
                "Repository Pattern"
            ],
            "components": [
                "FastAPI",
                "APScheduler",
                "SQLAlchemy",
                "SQLAdmin",
                "AsyncPG"
            ],
            "layers": [
                "Presentation (FastAPI)",
                "Application (Use Cases)",
                "Domain (Entities)",
                "Infrastructure (Database)"
            ],
            "timestamp": datetime.now().isoformat()
        }


async def _get_db_connection():
    """데이터베이스 연결 생성"""
    # 환경변수에서 데이터베이스 연결 정보 파싱
    db_url = os.getenv("DB_APP_URL", "postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care")
    
    # URL 디코딩
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    # URL 파싱
    parsed = urlparse(f"postgresql://{db_url}")
    
    return await asyncpg.connect(
        host=parsed.hostname or "host.docker.internal",
        port=parsed.port or 15432,
        user=unquote(parsed.username) if parsed.username else "svc_dev",
        password=unquote(parsed.password) if parsed.password else "IOT_dev_123!@#",
        database=parsed.path[1:] if parsed.path else "iot_care"
    )


# Docker Compose에서 사용할 수 있도록 직접 실행 가능
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")