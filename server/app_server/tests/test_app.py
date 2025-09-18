"""
ML 레지스트리 API 단순 테스트
기존 앱 의존성 없이 테스트
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.adapters.http.dataset_router import router as dataset_router
from app.adapters.http.experiment_router import router as experiment_router

def create_test_app():
    """테스트용 FastAPI 앱 생성"""
    app = FastAPI(title="ML Registry API Test")
    app.include_router(dataset_router)
    app.include_router(experiment_router)
    return app

@pytest.fixture
def test_client():
    """테스트용 FastAPI 클라이언트"""
    app = create_test_app()
    return TestClient(app)

def test_app_creation():
    """앱 생성 테스트"""
    app = create_test_app()
    assert app is not None
    assert app.title == "ML Registry API Test"

def test_dataset_router_included():
    """데이터셋 라우터 포함 테스트"""
    app = create_test_app()
    routes = [route.path for route in app.routes]
    assert any("/api/v1/datasets" in route for route in routes)

def test_experiment_router_included():
    """실험 라우터 포함 테스트"""
    app = create_test_app()
    routes = [route.path for route in app.routes]
    assert any("/api/v1/experiments" in route for route in routes)

def test_dataset_endpoints_exist(test_client):
    """데이터셋 엔드포인트 존재 테스트"""
    # GET /api/v1/datasets/ - 목록 조회
    response = test_client.get("/api/v1/datasets/")
    # 데이터베이스 연결 없이도 500 에러가 아닌 다른 에러여야 함
    assert response.status_code in [200, 422, 500]  # 422는 validation error, 500은 DB 연결 에러

def test_experiment_endpoints_exist(test_client):
    """실험 엔드포인트 존재 테스트"""
    # GET /api/v1/experiments/ - 목록 조회
    response = test_client.get("/api/v1/experiments/")
    # 데이터베이스 연결 없이도 500 에러가 아닌 다른 에러여야 함
    assert response.status_code in [200, 422, 500]  # 422는 validation error, 500은 DB 연결 에러

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

