"""
데이터셋 유즈케이스
데이터셋 관련 비즈니스 로직 구현
"""

from typing import List, Optional
from uuid import UUID
from app.domain.entities.dataset import Dataset
from app.domain.ports.dataset_repository import DatasetRepository
from app.domain.services.dataset_service import DatasetService
from app.application.dto.dataset_dto import DatasetCreateRequest, DatasetUpdateRequest, DatasetResponse

class CreateDatasetUseCase:
    """데이터셋 생성 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository, dataset_service: DatasetService):
        self.dataset_repository = dataset_repository
        self.dataset_service = dataset_service
    
    async def execute(self, request: DatasetCreateRequest) -> DatasetResponse:
        """데이터셋 생성 실행"""
        # 도메인 엔티티 생성
        dataset = Dataset(
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
        
        # 도메인 서비스로 검증
        self.dataset_service.validate_dataset_creation(dataset)
        
        # 리포지토리에 저장
        created_dataset = await self.dataset_repository.save(dataset)
        
        # 응답 DTO로 변환
        return DatasetResponse.model_validate(created_dataset)

class GetDatasetUseCase:
    """데이터셋 조회 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, dataset_id: UUID) -> Optional[DatasetResponse]:
        """데이터셋 조회 실행"""
        dataset = await self.dataset_repository.get_by_id(dataset_id)
        if dataset:
            return DatasetResponse.model_validate(dataset)
        return None

class UpdateDatasetUseCase:
    """데이터셋 업데이트 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository, dataset_service: DatasetService):
        self.dataset_repository = dataset_repository
        self.dataset_service = dataset_service
    
    async def execute(self, dataset_id: UUID, request: DatasetUpdateRequest) -> Optional[DatasetResponse]:
        """데이터셋 업데이트 실행"""
        # 기존 데이터셋 조회
        existing_dataset = await self.dataset_repository.get_by_id(dataset_id)
        if not existing_dataset:
            return None
        
        # 업데이트할 필드만 적용
        update_data = request.dict(exclude_unset=True)
        updated_dataset = self.dataset_service.update_dataset_metadata(existing_dataset, update_data)
        
        # 리포지토리에 저장
        saved_dataset = await self.dataset_repository.update(updated_dataset)
        
        # 응답 DTO로 변환
        return DatasetResponse.model_validate(saved_dataset)

class DeleteDatasetUseCase:
    """데이터셋 삭제 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, dataset_id: UUID) -> bool:
        """데이터셋 삭제 실행"""
        return await self.dataset_repository.delete(dataset_id)

class ListDatasetsUseCase:
    """데이터셋 목록 조회 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[DatasetResponse]:
        """데이터셋 목록 조회 실행"""
        datasets = await self.dataset_repository.get_all(skip=skip, limit=limit)
        return [DatasetResponse.model_validate(dataset) for dataset in datasets]

class ListDatasetsByNameUseCase:
    """이름으로 데이터셋 목록 조회 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, name: str, skip: int = 0, limit: int = 100) -> List[DatasetResponse]:
        """데이터셋 목록 조회 실행"""
        datasets = await self.dataset_repository.get_by_name(name, skip=skip, limit=limit)
        return [DatasetResponse.model_validate(dataset) for dataset in datasets]

class ListDatasetsByTagUseCase:
    """태그로 데이터셋 목록 조회 유즈케이스"""
    
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository
    
    async def execute(self, tag: str, skip: int = 0, limit: int = 100) -> List[DatasetResponse]:
        """데이터셋 목록 조회 실행"""
        datasets = await self.dataset_repository.get_by_tag(tag, skip=skip, limit=limit)
        return [DatasetResponse.model_validate(dataset) for dataset in datasets]