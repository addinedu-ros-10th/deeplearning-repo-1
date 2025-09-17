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
    
    # 데이터베이스 매니저 초기화
    from app.infrastructure.db.session import db_manager
    import asyncio
    
    # 비동기 초기화를 동기적으로 실행
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 실행 중인 이벤트 루프가 있는 경우
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, db_manager.initialize())
                future.result()
        else:
            asyncio.run(db_manager.initialize())
        print("✅ 데이터베이스 매니저 초기화 완료")
    except Exception as e:
        print(f"⚠️ 데이터베이스 매니저 초기화 실패: {e}")
    
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
    
    # ML 레지스트리 라우터 포함
    from app.adapters.http.dataset_router import router as dataset_router
    from app.adapters.http.experiment_router import router as experiment_router
    from app.adapters.http.frame_prediction_router import router as frame_prediction_router
    from app.adapters.http.detection_event_router import router as detection_event_router
    
    app.include_router(dataset_router)
    app.include_router(experiment_router)
    app.include_router(frame_prediction_router)
    app.include_router(detection_event_router)
    
    # 스케줄러 이벤트 핸들러 포함
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    # SQLAdmin 관리자 패널 설정
    _setup_admin_panel(app)
    
    # 추가 API 엔드포인트 설정 (한 번만 실행)
    if not hasattr(app, '_endpoints_configured'):
        _setup_additional_endpoints(app)
        app._endpoints_configured = True
    
    return app


def _setup_admin_panel(app: FastAPI) -> None:
    """SQLAdmin 관리자 패널 설정 (동기 버전 - 호환성 유지)"""
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
            from app.infrastructure.db.session import get_app_session
            from sqlalchemy import text
            async with get_app_session() as session:
                result = await session.execute(text("""
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                tables = result.fetchall()
                
                return {
                    "tables": [{"table_name": row[0], "table_type": row[1]} for row in tables],
                    "count": len(tables),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch tables: {str(e)}")

    @app.get("/api/v1/scheduled-jobs")
    async def get_scheduled_jobs():
        """스케줄 작업 목록 조회"""
        try:
            from app.infrastructure.db.session import get_app_session
            from sqlalchemy import text
            async with get_app_session() as session:
                result = await session.execute(text("""
                    SELECT id, name, func, cron, enabled, status, 
                           last_run_at, next_run_at, created_at
                    FROM scheduled_jobs 
                    WHERE is_deleted = false
                    ORDER BY created_at DESC
                """))
                jobs = result.fetchall()
                
                return {
                    "jobs": [{"id": row[0], "name": row[1], "func": row[2], "cron": row[3], 
                             "enabled": row[4], "status": row[5], "last_run_at": row[6], 
                             "next_run_at": row[7], "created_at": row[8]} for row in jobs],
                    "count": len(jobs),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled jobs: {str(e)}")

    @app.get("/api/v1/database/info")
    async def get_database_info():
        """데이터베이스 정보 조회"""
        try:
            from app.infrastructure.db.session import get_app_session
            from sqlalchemy import text
            async with get_app_session() as session:
                # 데이터베이스 버전
                version_result = await session.execute(text("SELECT version()"))
                version = version_result.scalar()
                
                # 테이블 개수
                table_count_result = await session.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                table_count = table_count_result.scalar()
                
                # scheduled_jobs 테이블 통계
                job_stats_result = await session.execute(text("""
                    SELECT 
                        COUNT(*) as total_jobs,
                        COUNT(CASE WHEN enabled = true THEN 1 END) as enabled_jobs,
                        COUNT(CASE WHEN status = 'idle' THEN 1 END) as idle_jobs,
                        COUNT(CASE WHEN status = 'running' THEN 1 END) as running_jobs
                    FROM scheduled_jobs 
                    WHERE is_deleted = false
                """))
                job_stats_row = job_stats_result.fetchone()
                
                return {
                    "database_version": version,
                    "table_count": table_count,
                    "scheduled_jobs_stats": {
                        "total_jobs": job_stats_row[0],
                        "enabled_jobs": job_stats_row[1],
                        "idle_jobs": job_stats_row[2],
                        "running_jobs": job_stats_row[3]
                    },
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
    
    # URL 디코딩 - postgresql+asyncpg:// 형식도 처리
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "")
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    # URL 파싱
    parsed = urlparse(f"postgresql://{db_url}")
    
    # Docker 컨테이너에서 host.docker.internal 대신 직접 IP 사용
    host = parsed.hostname or "host.docker.internal"
    if host == "host.docker.internal":
        host = "172.17.0.1"  # Docker 호스트의 실제 IP
    
    return await asyncpg.connect(
        host=host,
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