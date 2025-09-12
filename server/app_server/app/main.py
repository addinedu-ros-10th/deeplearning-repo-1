"""
FastAPI 애플리케이션 팩토리
Docker Compose 환경에서 사용
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv('secret/.env.local')

def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리 함수"""
    
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

    # 스케줄러 애플리케이션 임포트 및 설정
    from app.scheduler_app import router as scheduler_router, startup_event, shutdown_event
    
    # 스케줄러 애플리케이션의 라우터들을 메인 앱에 포함
    app.include_router(scheduler_router)
    
    # 스케줄러 이벤트 핸들러 포함
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
    
    return app

# Docker Compose에서 사용할 수 있도록 직접 실행 가능
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")