"""
APScheduler가 통합된 FastAPI 애플리케이션
"""

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime
from app.services.scheduler_service import scheduler_service
from app.admin.simple_admin import create_admin_app

# 환경 변수 로딩
load_dotenv('secret/.env.local')

# 라우터 생성
router = APIRouter()

@router.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "App Server API with APScheduler",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "admin": "/admin",
        "scheduler": "active"
    }

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    scheduler_status = "active" if scheduler_service.is_running else "inactive"
    return {
        "status": "healthy",
        "service": "App Server with Scheduler",
        "version": "1.0.0",
        "scheduler_status": scheduler_status,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/api/v1/scheduled-jobs")
async def get_scheduled_jobs():
    """스케줄 작업 목록 조회"""
    try:
        # 환경변수에서 데이터베이스 연결 정보 파싱
        db_url = os.getenv("DB_APP_URL", "postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care")
        
        # URL 디코딩
        from urllib.parse import unquote
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # URL 파싱
        from urllib.parse import urlparse
        parsed = urlparse(f"postgresql://{db_url}")
        
        conn = await asyncpg.connect(
            host=parsed.hostname or "host.docker.internal",
            port=parsed.port or 15432,
            user=unquote(parsed.username) if parsed.username else "svc_dev",
            password=unquote(parsed.password) if parsed.password else "IOT_dev_123!@#",
            database=parsed.path[1:] if parsed.path else "iot_care"
        )
        
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

@router.get("/api/v1/scheduler/status")
async def get_scheduler_status():
    """스케줄러 상태 조회"""
    try:
        jobs = scheduler_service.get_jobs()
        return {
            "scheduler_running": scheduler_service.is_running,
            "active_jobs": len(jobs),
            "jobs": jobs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")

@router.post("/api/v1/scheduler/reload")
async def reload_scheduler():
    """스케줄러 재로드"""
    try:
        await scheduler_service.reload_jobs()
        return {
            "status": "success",
            "message": "스케줄러 재로드 완료",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload scheduler: {str(e)}")

@router.post("/api/v1/scheduled-jobs/{job_id}/execute")
async def execute_job_manually(job_id: str):
    """작업 수동 실행"""
    try:
        # 환경변수에서 데이터베이스 연결 정보 파싱
        db_url = os.getenv("DB_APP_URL", "postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care")
        
        # URL 디코딩
        from urllib.parse import unquote
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # URL 파싱
        from urllib.parse import urlparse
        parsed = urlparse(f"postgresql://{db_url}")
        
        conn = await asyncpg.connect(
            host=parsed.hostname or "host.docker.internal",
            port=parsed.port or 15432,
            user=unquote(parsed.username) if parsed.username else "svc_dev",
            password=unquote(parsed.password) if parsed.password else "IOT_dev_123!@#",
            database=parsed.path[1:] if parsed.path else "iot_care"
        )
        
        # 작업 정보 조회
        job = await conn.fetchrow("""
            SELECT id, name, func, args, kwargs, enabled
            FROM scheduled_jobs 
            WHERE id = $1 AND is_deleted = false
        """, job_id)
        
        if not job:
            await conn.close()
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job['enabled']:
            await conn.close()
            raise HTTPException(status_code=400, detail="Job is disabled")
        
        await conn.close()
        
        # 작업 실행
        await scheduler_service._execute_job(
            job_id, 
            job['func'], 
            job['args'] or {}, 
            job['kwargs'] or {}
        )
        
        return {
            "status": "success",
            "message": f"작업 {job['name']} 수동 실행 완료",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute job: {str(e)}")

@router.get("/api/v1/tables")
async def list_tables():
    """데이터베이스 테이블 목록 조회"""
    try:
        # 환경변수에서 데이터베이스 연결 정보 파싱
        db_url = os.getenv("DB_APP_URL", "postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care")
        
        # URL 디코딩
        from urllib.parse import unquote
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # URL 파싱
        from urllib.parse import urlparse
        parsed = urlparse(f"postgresql://{db_url}")
        
        conn = await asyncpg.connect(
            host=parsed.hostname or "host.docker.internal",
            port=parsed.port or 15432,
            user=unquote(parsed.username) if parsed.username else "svc_dev",
            password=unquote(parsed.password) if parsed.password else "IOT_dev_123!@#",
            database=parsed.path[1:] if parsed.path else "iot_care"
        )
        
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

@router.get("/api/v1/database/info")
async def get_database_info():
    """데이터베이스 정보 조회"""
    try:
        # 환경변수에서 데이터베이스 연결 정보 파싱
        db_url = os.getenv("DB_APP_URL", "postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care")
        
        # URL 디코딩
        from urllib.parse import unquote
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # URL 파싱
        from urllib.parse import urlparse
        parsed = urlparse(f"postgresql://{db_url}")
        
        conn = await asyncpg.connect(
            host=parsed.hostname or "host.docker.internal",
            port=parsed.port or 15432,
            user=unquote(parsed.username) if parsed.username else "svc_dev",
            password=unquote(parsed.password) if parsed.password else "IOT_dev_123!@#",
            database=parsed.path[1:] if parsed.path else "iot_care"
        )
        
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
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_jobs,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs
            FROM scheduled_jobs 
            WHERE is_deleted = false
        """)
        
        await conn.close()
        
        return {
            "database_version": version,
            "table_count": table_count,
            "scheduled_jobs_stats": dict(job_stats),
            "scheduler_status": "active" if scheduler_service.is_running else "inactive",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch database info: {str(e)}")

# 이벤트 핸들러 함수들
async def startup_event():
    """애플리케이션 시작 시 스케줄러 시작"""
    try:
        await scheduler_service.start()
        print("✅ 스케줄러 서비스 시작 완료")
    except Exception as e:
        print(f"❌ 스케줄러 서비스 시작 실패: {e}")

async def shutdown_event():
    """애플리케이션 종료 시 스케줄러 중지"""
    try:
        await scheduler_service.stop()
        print("✅ 스케줄러 서비스 중지 완료")
    except Exception as e:
        print(f"❌ 스케줄러 서비스 중지 실패: {e}")

# 독립 실행을 위한 FastAPI 앱 (개발/테스트용)
app = FastAPI(
    title="App Server API with Scheduler",
    description="IoT Care App Server with APScheduler Integration",
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

# 라우터 포함
app.include_router(router)

# 이벤트 핸들러 등록
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

# SQLAdmin 설정
admin = create_admin_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")