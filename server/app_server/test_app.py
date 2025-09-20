"""
ML 레지스트리 API 테스트용 간단한 앱
데이터베이스 연결 없이 기본 구조 테스트
"""

from fastapi import FastAPI
from app.adapters.http.dataset_router import router as dataset_router
from app.adapters.http.experiment_router import router as experiment_router

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
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_test_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

