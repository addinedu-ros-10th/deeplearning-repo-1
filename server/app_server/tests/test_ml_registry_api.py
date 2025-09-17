"""
ML 레지스트리 API 통합 테스트
TDD 기반 테스트 구현
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import json

from app.main import create_app
from app.infrastructure.db.session import db_manager
from app.infrastructure.db.models.ml_models import Base

# 테스트용 데이터베이스 URL
TEST_DB_URL = "postgresql+asyncpg://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care"

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 생성"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """테스트용 데이터베이스 엔진"""
    engine = create_async_engine(TEST_DB_URL, echo=True)
    
    # 테스트용 스키마 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 테스트 후 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """테스트용 데이터베이스 세션"""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_client():
    """테스트용 FastAPI 클라이언트"""
    app = create_app()
    return TestClient(app)

@pytest.fixture
async def test_data():
    """테스트용 데이터"""
    return {
        "dataset": {
            "name": "test_fall_detection_dataset",
            "version": "v1.0",
            "storage_path": "/data/fall_detection/v1.0",
            "description": "낙상 감지를 위한 테스트 데이터셋",
            "creator_name": "테스트 개발자",
            "creator_email": "test@example.com",
            "source_url": "https://example.com/dataset",
            "license": "MIT",
            "class_schema": {
                "labels": ["normal", "warning", "fall"]
            },
            "tags": ["fall", "pose", "mediapipe", "lstm"]
        },
        "experiment": {
            "name": "lstm_fall_detection_v1",
            "dataset_id": None,  # 테스트 중에 설정
            "model_path": "/models/lstm_fall_detection_v1.pt",
            "framework": "PyTorch",
            "code_version": "abc123",
            "params": {
                "seq_len": 60,
                "hidden_size": 128,
                "num_layers": 2,
                "dropout": 0.2,
                "learning_rate": 0.001,
                "epochs": 100
            },
            "metrics": {
                "val_accuracy": 0.92,
                "val_f1_score": 0.88,
                "val_precision": 0.90,
                "val_recall": 0.86
            }
        }
    }

class TestDatasetAPI:
    """데이터셋 API 테스트"""
    
    def test_create_dataset(self, test_client, test_data):
        """데이터셋 생성 테스트"""
        response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # 응답 데이터 검증
        assert data["name"] == test_data["dataset"]["name"]
        assert data["version"] == test_data["dataset"]["version"]
        assert data["storage_path"] == test_data["dataset"]["storage_path"]
        assert data["description"] == test_data["dataset"]["description"]
        assert data["creator_name"] == test_data["dataset"]["creator_name"]
        assert data["creator_email"] == test_data["dataset"]["creator_email"]
        assert data["source_url"] == test_data["dataset"]["source_url"]
        assert data["license"] == test_data["dataset"]["license"]
        assert data["class_schema"] == test_data["dataset"]["class_schema"]
        assert data["tags"] == test_data["dataset"]["tags"]
        assert "dataset_id" in data
        assert "created_at" in data
        
        return data["dataset_id"]
    
    def test_get_dataset(self, test_client, test_data):
        """데이터셋 조회 테스트"""
        # 먼저 데이터셋 생성
        create_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        assert create_response.status_code == 201
        dataset_id = create_response.json()["dataset_id"]
        
        # 데이터셋 조회
        response = test_client.get(f"/api/v1/datasets/{dataset_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["dataset_id"] == dataset_id
        assert data["name"] == test_data["dataset"]["name"]
        assert data["version"] == test_data["dataset"]["version"]
    
    def test_get_dataset_not_found(self, test_client):
        """존재하지 않는 데이터셋 조회 테스트"""
        fake_id = str(uuid4())
        response = test_client.get(f"/api/v1/datasets/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_datasets(self, test_client, test_data):
        """데이터셋 목록 조회 테스트"""
        # 테스트 데이터 생성
        for i in range(3):
            dataset_data = test_data["dataset"].copy()
            dataset_data["name"] = f"test_dataset_{i}"
            dataset_data["version"] = f"v{i+1}.0"
            
            response = test_client.post("/api/v1/datasets/", json=dataset_data)
            assert response.status_code == 201
        
        # 목록 조회
        response = test_client.get("/api/v1/datasets/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "datasets" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["datasets"]) >= 3
    
    def test_update_dataset(self, test_client, test_data):
        """데이터셋 수정 테스트"""
        # 먼저 데이터셋 생성
        create_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        assert create_response.status_code == 201
        dataset_id = create_response.json()["dataset_id"]
        
        # 데이터셋 수정
        update_data = {
            "description": "수정된 설명",
            "tags": ["fall", "pose", "updated"]
        }
        
        response = test_client.put(
            f"/api/v1/datasets/{dataset_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["description"] == update_data["description"]
        assert data["tags"] == update_data["tags"]
    
    def test_delete_dataset(self, test_client, test_data):
        """데이터셋 삭제 테스트"""
        # 먼저 데이터셋 생성
        create_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        assert create_response.status_code == 201
        dataset_id = create_response.json()["dataset_id"]
        
        # 데이터셋 삭제
        response = test_client.delete(f"/api/v1/datasets/{dataset_id}")
        
        assert response.status_code == 204
        
        # 삭제 확인
        get_response = test_client.get(f"/api/v1/datasets/{dataset_id}")
        assert get_response.status_code == 404

class TestExperimentAPI:
    """실험 API 테스트"""
    
    def test_create_experiment(self, test_client, test_data):
        """실험 생성 테스트"""
        # 먼저 데이터셋 생성
        dataset_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        assert dataset_response.status_code == 201
        dataset_id = dataset_response.json()["dataset_id"]
        
        # 실험 데이터에 데이터셋 ID 설정
        experiment_data = test_data["experiment"].copy()
        experiment_data["dataset_id"] = dataset_id
        
        # 실험 생성
        response = test_client.post(
            "/api/v1/experiments/",
            json=experiment_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # 응답 데이터 검증
        assert data["name"] == experiment_data["name"]
        assert data["dataset_id"] == dataset_id
        assert data["model_path"] == experiment_data["model_path"]
        assert data["framework"] == experiment_data["framework"]
        assert data["code_version"] == experiment_data["code_version"]
        assert data["params"] == experiment_data["params"]
        assert data["metrics"] == experiment_data["metrics"]
        assert "experiment_id" in data
        assert "created_at" in data
        
        return data["experiment_id"]
    
    def test_get_experiment(self, test_client, test_data):
        """실험 조회 테스트"""
        # 먼저 데이터셋과 실험 생성
        dataset_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        dataset_id = dataset_response.json()["dataset_id"]
        
        experiment_data = test_data["experiment"].copy()
        experiment_data["dataset_id"] = dataset_id
        
        create_response = test_client.post(
            "/api/v1/experiments/",
            json=experiment_data
        )
        experiment_id = create_response.json()["experiment_id"]
        
        # 실험 조회
        response = test_client.get(f"/api/v1/experiments/{experiment_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["experiment_id"] == experiment_id
        assert data["name"] == experiment_data["name"]
        assert data["dataset_id"] == dataset_id
    
    def test_list_experiments(self, test_client, test_data):
        """실험 목록 조회 테스트"""
        # 먼저 데이터셋 생성
        dataset_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        dataset_id = dataset_response.json()["dataset_id"]
        
        # 여러 실험 생성
        for i in range(3):
            experiment_data = test_data["experiment"].copy()
            experiment_data["name"] = f"test_experiment_{i}"
            experiment_data["dataset_id"] = dataset_id
            
            response = test_client.post("/api/v1/experiments/", json=experiment_data)
            assert response.status_code == 201
        
        # 목록 조회
        response = test_client.get("/api/v1/experiments/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "experiments" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["experiments"]) >= 3
    
    def test_list_experiments_by_dataset(self, test_client, test_data):
        """데이터셋별 실험 목록 조회 테스트"""
        # 먼저 데이터셋 생성
        dataset_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        dataset_id = dataset_response.json()["dataset_id"]
        
        # 여러 실험 생성
        for i in range(2):
            experiment_data = test_data["experiment"].copy()
            experiment_data["name"] = f"test_experiment_{i}"
            experiment_data["dataset_id"] = dataset_id
            
            response = test_client.post("/api/v1/experiments/", json=experiment_data)
            assert response.status_code == 201
        
        # 데이터셋별 실험 목록 조회
        response = test_client.get(f"/api/v1/experiments/dataset/{dataset_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["dataset_id"] == dataset_id
        assert "experiments" in data
        assert "total" in data
        assert len(data["experiments"]) >= 2
    
    def test_update_experiment(self, test_client, test_data):
        """실험 수정 테스트"""
        # 먼저 데이터셋과 실험 생성
        dataset_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        dataset_id = dataset_response.json()["dataset_id"]
        
        experiment_data = test_data["experiment"].copy()
        experiment_data["dataset_id"] = dataset_id
        
        create_response = test_client.post(
            "/api/v1/experiments/",
            json=experiment_data
        )
        experiment_id = create_response.json()["experiment_id"]
        
        # 실험 수정
        update_data = {
            "framework": "TensorFlow",
            "params": {
                "seq_len": 120,
                "hidden_size": 256,
                "learning_rate": 0.0001
            }
        }
        
        response = test_client.put(
            f"/api/v1/experiments/{experiment_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["framework"] == update_data["framework"]
        assert data["params"]["seq_len"] == update_data["params"]["seq_len"]
        assert data["params"]["hidden_size"] == update_data["params"]["hidden_size"]
    
    def test_delete_experiment(self, test_client, test_data):
        """실험 삭제 테스트"""
        # 먼저 데이터셋과 실험 생성
        dataset_response = test_client.post(
            "/api/v1/datasets/",
            json=test_data["dataset"]
        )
        dataset_id = dataset_response.json()["dataset_id"]
        
        experiment_data = test_data["experiment"].copy()
        experiment_data["dataset_id"] = dataset_id
        
        create_response = test_client.post(
            "/api/v1/experiments/",
            json=experiment_data
        )
        experiment_id = create_response.json()["experiment_id"]
        
        # 실험 삭제
        response = test_client.delete(f"/api/v1/experiments/{experiment_id}")
        
        assert response.status_code == 204
        
        # 삭제 확인
        get_response = test_client.get(f"/api/v1/experiments/{experiment_id}")
        assert get_response.status_code == 404

class TestValidation:
    """유효성 검사 테스트"""
    
    def test_dataset_validation(self, test_client):
        """데이터셋 유효성 검사 테스트"""
        # 필수 필드 누락
        response = test_client.post("/api/v1/datasets/", json={})
        assert response.status_code == 422
        
        # 잘못된 데이터 타입
        invalid_data = {
            "name": "",
            "version": "v1",
            "storage_path": "/path"
        }
        response = test_client.post("/api/v1/datasets/", json=invalid_data)
        assert response.status_code == 422
    
    def test_experiment_validation(self, test_client):
        """실험 유효성 검사 테스트"""
        # 필수 필드 누락
        response = test_client.post("/api/v1/experiments/", json={})
        assert response.status_code == 422
        
        # 잘못된 프레임워크
        invalid_data = {
            "name": "test",
            "dataset_id": str(uuid4()),
            "model_path": "/path",
            "framework": "InvalidFramework"
        }
        response = test_client.post("/api/v1/experiments/", json=invalid_data)
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

