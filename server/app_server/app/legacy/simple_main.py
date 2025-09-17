"""
간단한 FastAPI 애플리케이션 (테스트용)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime

# 환경 변수 로딩
load_dotenv('secret/.env.local')

app = FastAPI(
    title="App Server API",
    description="IoT Care App Server with Scheduled Jobs Management",
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

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "App Server API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "App Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/tables")
async def list_tables():
    """데이터베이스 테이블 목록 조회"""
    try:
        conn = await asyncpg.connect(
            host="0.0.0.0",
            port=15432,
            user="svc_dev",
            password="IOT_dev_123!@#",
            database="iot_care"
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

@app.get("/api/v1/scheduled-jobs")
async def get_scheduled_jobs():
    """스케줄 작업 목록 조회"""
    try:
        conn = await asyncpg.connect(
            host="0.0.0.0",
            port=15432,
            user="svc_dev",
            password="IOT_dev_123!@#",
            database="iot_care"
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

@app.get("/api/v1/database/info")
async def get_database_info():
    """데이터베이스 정보 조회"""
    try:
        conn = await asyncpg.connect(
            host="0.0.0.0",
            port=15432,
            user="svc_dev",
            password="IOT_dev_123!@#",
            database="iot_care"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
