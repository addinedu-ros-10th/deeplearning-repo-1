"""
ML 레지스트리 API 테스트용 앱 (데이터베이스 초기화 포함)
"""

import asyncio
from fastapi import FastAPI
from app.adapters.http.dataset_router import router as dataset_router
from app.adapters.http.experiment_router import router as experiment_router
from app.infrastructure.db.session import db_manager

def create_test_app():
    """테스트용 FastAPI 앱 생성"""
    app = FastAPI(
        title="ML Registry API Test",
        description="ML 레지스트리 API 테스트용 앱",
        version="1.0.0"
    )
    
    # 라우터 포함
    app.include_router(dataset_router)
    app.include_router(experiment_router)
    
    @app.on_event("startup")
    async def startup_event():
        """앱 시작 시 데이터베이스 초기화"""
        print("🚀 데이터베이스 초기화 시작...")
        await db_manager.initialize()
        print("✅ 데이터베이스 초기화 완료!")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """앱 종료 시 데이터베이스 연결 정리"""
        print("🔄 데이터베이스 연결 정리...")
        await db_manager.close()
        print("✅ 데이터베이스 연결 정리 완료!")
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_test_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
