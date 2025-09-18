# ML 레지스트리 API 개발 계획서

## 📋 프로젝트 개요

**프로젝트명**: ML 레지스트리 RESTful API 개발  
**목표**: PostgreSQL ML 스키마 기반의 데이터셋 및 실험 관리 API 구축  
**기간**: 10-15일 (예상)  
**아키텍처**: 헥사고날 아키텍처 + 의존성 주입  

## ✅ 개발 진행 현황 체크리스트

### Phase 1: 모델 및 인프라 구축 (1-2일)
- [ ] 1.1 SQLAlchemy 모델 정의
  - [ ] Dataset 모델 생성
  - [ ] Experiment 모델 생성
  - [ ] PostgreSQL 전용 타입 매핑
  - [ ] 관계 설정 및 제약조건 정의
- [ ] 1.2 데이터베이스 연결 설정
  - [ ] ML 스키마용 별도 엔진 생성
  - [ ] Alembic 마이그레이션 파일 생성
  - [ ] 연결 테스트 및 검증

### Phase 2: 도메인 레이어 구축 (2-3일)
- [ ] 2.1 엔티티 정의
  - [ ] Dataset 엔티티 생성
  - [ ] Experiment 엔티티 생성
  - [ ] 비즈니스 로직 및 검증 규칙 포함
- [ ] 2.2 값 객체 정의
  - [ ] DatasetId, ExperimentId 값 객체
  - [ ] DatasetVersion, ModelPath 등 도메인 특화 값 객체
- [ ] 2.3 도메인 서비스
  - [ ] 데이터셋 버전 관리 로직
  - [ ] 실험 생성 및 업데이트 로직
  - [ ] 도메인 규칙 검증 서비스

### Phase 3: 애플리케이션 레이어 구축 (3-4일)
- [ ] 3.1 DTO 정의
  - [ ] DatasetCreateRequest, DatasetUpdateRequest, DatasetResponse
  - [ ] ExperimentCreateRequest, ExperimentUpdateRequest, ExperimentResponse
  - [ ] 요청/응답 데이터 변환 로직
- [ ] 3.2 유즈케이스 구현
  - [ ] CreateDatasetUseCase
  - [ ] GetDatasetUseCase, ListDatasetsUseCase
  - [ ] UpdateDatasetUseCase, DeleteDatasetUseCase
  - [ ] CreateExperimentUseCase
  - [ ] GetExperimentUseCase, ListExperimentsUseCase
  - [ ] UpdateExperimentUseCase, DeleteExperimentUseCase

### Phase 4: 어댑터 레이어 구축 (2-3일)
- [ ] 4.1 리포지토리 어댑터
  - [ ] DatasetRepository 인터페이스 구현
  - [ ] ExperimentRepository 인터페이스 구현
  - [ ] SQLAlchemy 기반 구현체
- [ ] 4.2 HTTP 어댑터 (FastAPI)
  - [ ] RESTful API 엔드포인트 구현
  - [ ] 요청/응답 검증 및 변환
  - [ ] 에러 핸들링 및 HTTP 상태 코드

### Phase 5: 인프라 레이어 구축 (1-2일)
- [ ] 5.1 의존성 주입 설정
  - [ ] DI 컨테이너에 서비스 등록
  - [ ] 리포지토리 및 유즈케이스 바인딩
- [ ] 5.2 설정 관리
  - [ ] ML 스키마용 데이터베이스 설정
  - [ ] 환경별 설정 분리

### Phase 6: 통합 및 테스트 (2-3일)
- [ ] 6.1 API 통합 테스트
  - [ ] 모든 엔드포인트 테스트
  - [ ] 데이터베이스 연동 테스트
  - [ ] 에러 시나리오 테스트
- [ ] 6.2 문서화
  - [ ] Swagger/OpenAPI 문서 자동 생성
  - [ ] API 사용 가이드 작성

## 🏗️ 아키텍처 구조

```
app/
├── domain/
│   ├── entities/
│   │   ├── dataset.py          # Dataset 엔티티
│   │   └── experiment.py       # Experiment 엔티티
│   ├── value_objects/
│   │   ├── dataset_id.py       # DatasetId 값 객체
│   │   ├── experiment_id.py    # ExperimentId 값 객체
│   │   └── model_path.py       # ModelPath 값 객체
│   ├── services/
│   │   ├── dataset_service.py  # 데이터셋 도메인 서비스
│   │   └── experiment_service.py # 실험 도메인 서비스
│   └── ports/
│       ├── dataset_repository.py    # 데이터셋 리포지토리 인터페이스
│       └── experiment_repository.py # 실험 리포지토리 인터페이스
├── application/
│   ├── dto/
│   │   ├── dataset_dto.py      # 데이터셋 DTO
│   │   └── experiment_dto.py   # 실험 DTO
│   └── use_cases/
│       ├── dataset_use_cases.py    # 데이터셋 유즈케이스
│       └── experiment_use_cases.py # 실험 유즈케이스
├── adapters/
│   ├── repositories/
│   │   ├── dataset_repository_impl.py    # 데이터셋 리포지토리 구현
│   │   └── experiment_repository_impl.py # 실험 리포지토리 구현
│   └── http/
│       ├── dataset_router.py    # 데이터셋 API 라우터
│       └── experiment_router.py # 실험 API 라우터
└── infrastructure/
    ├── db/
    │   └── models/
    │       ├── dataset_model.py    # SQLAlchemy 모델
    │       └── experiment_model.py # SQLAlchemy 모델
    └── di/
        └── ml_container.py         # ML 서비스 DI 컨테이너
```

## 🚀 RESTful API 설계

### Dataset API
```
GET    /api/v1/datasets           # 데이터셋 목록 조회
POST   /api/v1/datasets           # 데이터셋 생성
GET    /api/v1/datasets/{id}      # 특정 데이터셋 조회
PUT    /api/v1/datasets/{id}      # 데이터셋 수정
DELETE /api/v1/datasets/{id}      # 데이터셋 삭제
```

### Experiment API
```
GET    /api/v1/experiments                    # 실험 목록 조회
POST   /api/v1/experiments                    # 실험 생성
GET    /api/v1/experiments/{id}               # 특정 실험 조회
PUT    /api/v1/experiments/{id}               # 실험 수정
DELETE /api/v1/experiments/{id}               # 실험 삭제
GET    /api/v1/datasets/{id}/experiments      # 특정 데이터셋의 실험 목록
```

## 📊 데이터 모델

### Dataset 모델
```python
class Dataset:
    dataset_id: UUID
    name: str
    version: str
    storage_path: str
    description: Optional[str]
    creator_name: Optional[str]
    creator_email: Optional[str]
    source_url: Optional[str]
    license: Optional[str]
    class_schema: Dict[str, List[str]]  # JSONB
    tags: List[str]  # TEXT[]
    created_at: datetime
```

### Experiment 모델
```python
class Experiment:
    experiment_id: UUID
    name: str
    dataset_id: UUID
    model_path: str
    framework: Optional[str]
    code_version: Optional[str]
    params: Optional[Dict]  # JSONB
    metrics: Optional[Dict]  # JSONB
    created_at: datetime
```

## 🔧 기술 스택

### Backend
- **FastAPI**: 비동기 웹 프레임워크
- **SQLAlchemy**: ORM
- **PostgreSQL**: 데이터베이스
- **Alembic**: 데이터베이스 마이그레이션
- **Pydantic**: 데이터 검증
- **Dependency Injector**: 의존성 주입

### Development
- **pytest**: 테스트 프레임워크
- **httpx**: HTTP 클라이언트 테스트
- **black**: 코드 포맷팅
- **mypy**: 타입 체킹

## 📝 상세 액션 아이템

### Phase 1: 모델 및 인프라 구축

#### 1.1 SQLAlchemy 모델 정의
**파일**: `app/infrastructure/db/models/ml_models.py`

```python
# Dataset 모델
class DatasetModel(Base):
    __tablename__ = "dataset"
    __table_args__ = {'schema': 'ml'}
    
    dataset_id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    name = Column(Text, nullable=False)
    version = Column(Text, nullable=False, server_default='v1')
    storage_path = Column(Text, nullable=False)
    description = Column(Text)
    creator_name = Column(Text)
    creator_email = Column(Text)
    source_url = Column(Text)
    license = Column(Text)
    class_schema = Column(postgresql.JSONB, nullable=False)
    tags = Column(postgresql.ARRAY(Text))
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    
    # 관계 설정
    experiments = relationship("ExperimentModel", back_populates="dataset")

# Experiment 모델
class ExperimentModel(Base):
    __tablename__ = "experiment"
    __table_args__ = {'schema': 'ml'}
    
    experiment_id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    name = Column(Text, nullable=False)
    dataset_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('ml.dataset.dataset_id'))
    model_path = Column(Text, nullable=False)
    framework = Column(Text)
    code_version = Column(Text)
    params = Column(postgresql.JSONB)
    metrics = Column(postgresql.JSONB)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    
    # 관계 설정
    dataset = relationship("DatasetModel", back_populates="experiments")
```

#### 1.2 데이터베이스 연결 설정
**파일**: `app/infrastructure/db/ml_session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# ML 스키마용 별도 엔진
ML_DB_URL = os.getenv('ML_DB_URL', 'postgresql+asyncpg://user:pass@localhost:15432/dbname')

ml_engine = create_async_engine(ML_DB_URL, echo=True)
MLSessionLocal = sessionmaker(ml_engine, class_=AsyncSession, expire_on_commit=False)

async def get_ml_session():
    async with MLSessionLocal() as session:
        yield session
```

### Phase 2: 도메인 레이어 구축

#### 2.1 엔티티 정의
**파일**: `app/domain/entities/dataset.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

@dataclass
class Dataset:
    dataset_id: UUID
    name: str
    version: str
    storage_path: str
    description: Optional[str] = None
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None
    source_url: Optional[str] = None
    license: Optional[str] = None
    class_schema: Dict[str, List[str]] = None
    tags: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.class_schema is None:
            self.class_schema = {"labels": ["normal", "warning", "fall"]}
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """태그 추가"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """태그 제거"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def update_class_schema(self, labels: List[str]) -> None:
        """클래스 스키마 업데이트"""
        self.class_schema = {"labels": labels}
```

#### 2.2 값 객체 정의
**파일**: `app/domain/value_objects/dataset_id.py`

```python
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class DatasetId:
    value: UUID
    
    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError("DatasetId must be a valid UUID")
    
    def __str__(self) -> str:
        return str(self.value)
    
    @classmethod
    def generate(cls) -> 'DatasetId':
        """새로운 DatasetId 생성"""
        return cls(UUID.uuid4())
```

### Phase 3: 애플리케이션 레이어 구축

#### 3.1 DTO 정의
**파일**: `app/application/dto/dataset_dto.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class DatasetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(default="v1", min_length=1, max_length=50)
    storage_path: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=1000)
    creator_name: Optional[str] = Field(None, max_length=100)
    creator_email: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    license: Optional[str] = Field(None, max_length=500)
    class_schema: Dict[str, List[str]] = Field(default={"labels": ["normal", "warning", "fall"]})
    tags: List[str] = Field(default_factory=list)

class DatasetUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    storage_path: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=1000)
    creator_name: Optional[str] = Field(None, max_length=100)
    creator_email: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    license: Optional[str] = Field(None, max_length=500)
    class_schema: Optional[Dict[str, List[str]]] = None
    tags: Optional[List[str]] = None

class DatasetResponse(BaseModel):
    dataset_id: UUID
    name: str
    version: str
    storage_path: str
    description: Optional[str]
    creator_name: Optional[str]
    creator_email: Optional[str]
    source_url: Optional[str]
    license: Optional[str]
    class_schema: Dict[str, List[str]]
    tags: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 3.2 유즈케이스 구현
**파일**: `app/application/use_cases/dataset_use_cases.py`

```python
from typing import List, Optional
from uuid import UUID
from app.domain.entities.dataset import Dataset
from app.domain.ports.dataset_repository import DatasetRepository
from app.application.dto.dataset_dto import DatasetCreateRequest, DatasetUpdateRequest

class CreateDatasetUseCase:
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, request: DatasetCreateRequest) -> Dataset:
        # 도메인 엔티티 생성
        dataset = Dataset(
            dataset_id=UUID.uuid4(),
            name=request.name,
            version=request.version,
            storage_path=request.storage_path,
            description=request.description,
            creator_name=request.creator_name,
            creator_email=request.creator_email,
            source_url=request.source_url,
            license=request.license,
            class_schema=request.class_schema,
            tags=request.tags
        )
        
        # 저장
        return await self.dataset_repository.save(dataset)

class GetDatasetUseCase:
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, dataset_id: UUID) -> Optional[Dataset]:
        return await self.dataset_repository.get_by_id(dataset_id)

class ListDatasetsUseCase:
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Dataset]:
        return await self.dataset_repository.get_all(skip=skip, limit=limit)
```

### Phase 4: 어댑터 레이어 구축

#### 4.1 리포지토리 어댑터
**파일**: `app/adapters/repositories/dataset_repository_impl.py`

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities.dataset import Dataset
from app.domain.ports.dataset_repository import DatasetRepository
from app.infrastructure.db.models.ml_models import DatasetModel

class DatasetRepositoryImpl(DatasetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, dataset: Dataset) -> Dataset:
        # SQLAlchemy 모델로 변환
        dataset_model = DatasetModel(
            dataset_id=dataset.dataset_id,
            name=dataset.name,
            version=dataset.version,
            storage_path=dataset.storage_path,
            description=dataset.description,
            creator_name=dataset.creator_name,
            creator_email=dataset.creator_email,
            source_url=dataset.source_url,
            license=dataset.license,
            class_schema=dataset.class_schema,
            tags=dataset.tags,
            created_at=dataset.created_at
        )
        
        self.session.add(dataset_model)
        await self.session.commit()
        await self.session.refresh(dataset_model)
        
        return dataset
    
    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        result = await self.session.execute(
            select(DatasetModel).where(DatasetModel.dataset_id == dataset_id)
        )
        dataset_model = result.scalar_one_or_none()
        
        if not dataset_model:
            return None
        
        return self._to_domain_entity(dataset_model)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dataset]:
        result = await self.session.execute(
            select(DatasetModel).offset(skip).limit(limit)
        )
        dataset_models = result.scalars().all()
        
        return [self._to_domain_entity(model) for model in dataset_models]
    
    def _to_domain_entity(self, model: DatasetModel) -> Dataset:
        return Dataset(
            dataset_id=model.dataset_id,
            name=model.name,
            version=model.version,
            storage_path=model.storage_path,
            description=model.description,
            creator_name=model.creator_name,
            creator_email=model.creator_email,
            source_url=model.source_url,
            license=model.license,
            class_schema=model.class_schema,
            tags=model.tags,
            created_at=model.created_at
        )
```

#### 4.2 HTTP 어댑터 (FastAPI)
**파일**: `app/adapters/http/dataset_router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.application.dto.dataset_dto import DatasetCreateRequest, DatasetUpdateRequest, DatasetResponse
from app.application.use_cases.dataset_use_cases import (
    CreateDatasetUseCase,
    GetDatasetUseCase,
    ListDatasetsUseCase,
    UpdateDatasetUseCase,
    DeleteDatasetUseCase
)
from app.infrastructure.db.ml_session import get_ml_session
from app.adapters.repositories.dataset_repository_impl import DatasetRepositoryImpl

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])

@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    request: DatasetCreateRequest,
    session = Depends(get_ml_session)
):
    """데이터셋 생성"""
    repository = DatasetRepositoryImpl(session)
    use_case = CreateDatasetUseCase(repository)
    
    try:
        dataset = await use_case.execute(request)
        return DatasetResponse.from_orm(dataset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create dataset: {str(e)}"
        )

@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    session = Depends(get_ml_session)
):
    """데이터셋 목록 조회"""
    repository = DatasetRepositoryImpl(session)
    use_case = ListDatasetsUseCase(repository)
    
    datasets = await use_case.execute(skip=skip, limit=limit)
    return [DatasetResponse.from_orm(dataset) for dataset in datasets]

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: UUID,
    session = Depends(get_ml_session)
):
    """특정 데이터셋 조회"""
    repository = DatasetRepositoryImpl(session)
    use_case = GetDatasetUseCase(repository)
    
    dataset = await use_case.execute(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return DatasetResponse.from_orm(dataset)

@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: UUID,
    request: DatasetUpdateRequest,
    session = Depends(get_ml_session)
):
    """데이터셋 수정"""
    repository = DatasetRepositoryImpl(session)
    use_case = UpdateDatasetUseCase(repository)
    
    try:
        dataset = await use_case.execute(dataset_id, request)
        return DatasetResponse.from_orm(dataset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update dataset: {str(e)}"
        )

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: UUID,
    session = Depends(get_ml_session)
):
    """데이터셋 삭제"""
    repository = DatasetRepositoryImpl(session)
    use_case = DeleteDatasetUseCase(repository)
    
    try:
        await use_case.execute(dataset_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete dataset: {str(e)}"
        )
```

## 🧪 테스트 계획

### 단위 테스트
- [ ] 도메인 엔티티 테스트
- [ ] 유즈케이스 테스트
- [ ] 리포지토리 테스트
- [ ] DTO 검증 테스트

### 통합 테스트
- [ ] API 엔드포인트 테스트
- [ ] 데이터베이스 연동 테스트
- [ ] 에러 핸들링 테스트

### E2E 테스트
- [ ] 전체 워크플로우 테스트
- [ ] 성능 테스트
- [ ] 보안 테스트

## 📚 문서화 계획

### API 문서
- [ ] Swagger/OpenAPI 자동 생성
- [ ] 엔드포인트별 상세 설명
- [ ] 요청/응답 예시
- [ ] 에러 코드 및 메시지

### 개발 문서
- [ ] 아키텍처 가이드
- [ ] 개발 환경 설정
- [ ] 배포 가이드
- [ ] 트러블슈팅 가이드

## 🚀 배포 계획

### 개발 환경
- [ ] 로컬 개발 환경 설정
- [ ] Docker Compose 구성
- [ ] 데이터베이스 마이그레이션

### 스테이징 환경
- [ ] 스테이징 서버 배포
- [ ] 통합 테스트 실행
- [ ] 성능 테스트

### 프로덕션 환경
- [ ] 프로덕션 서버 배포
- [ ] 모니터링 설정
- [ ] 로그 수집 설정

## 📊 성공 지표

### 기능적 지표
- [ ] 모든 CRUD 작업 정상 동작
- [ ] 데이터 검증 및 에러 핸들링
- [ ] API 응답 시간 < 200ms
- [ ] 99.9% 가용성

### 비기능적 지표
- [ ] 코드 커버리지 > 80%
- [ ] API 문서 완성도 100%
- [ ] 보안 취약점 0개
- [ ] 성능 요구사항 충족

---

**문서 생성일**: 2025-09-13  
**최종 업데이트**: 2025-09-13  
**작성자**: 개발팀  
**검토자**: -  
**승인자**: -  

