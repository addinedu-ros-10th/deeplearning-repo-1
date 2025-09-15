"""
데이터셋 리포지토리 구현
SQLAlchemy 기반 데이터셋 리포지토리
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from app.domain.entities.dataset import Dataset
from app.domain.ports.dataset_repository import DatasetRepository
from app.infrastructure.db.models.ml_models import DatasetModel

class DatasetRepositoryImpl(DatasetRepository):
    """데이터셋 리포지토리 구현체"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, dataset: Dataset) -> Dataset:
        """데이터셋 저장"""
        # SQLAlchemy 모델로 변환
        dataset_model = self._to_model(dataset)
        
        self.session.add(dataset_model)
        await self.session.commit()
        await self.session.refresh(dataset_model)
        
        return self._to_entity(dataset_model)
    
    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        """ID로 데이터셋 조회"""
        result = await self.session.execute(
            select(DatasetModel).where(DatasetModel.dataset_id == dataset_id)
        )
        dataset_model = result.scalar_one_or_none()
        
        if not dataset_model:
            return None
        
        return self._to_entity(dataset_model)
    
    async def get_by_name_and_version(self, name: str, version: str) -> Optional[Dataset]:
        """이름과 버전으로 데이터셋 조회"""
        result = await self.session.execute(
            select(DatasetModel).where(
                DatasetModel.name == name,
                DatasetModel.version == version
            )
        )
        dataset_model = result.scalar_one_or_none()
        
        if not dataset_model:
            return None
        
        return self._to_entity(dataset_model)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """모든 데이터셋 조회 (페이징)"""
        result = await self.session.execute(
            select(DatasetModel)
            .order_by(DatasetModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        dataset_models = result.scalars().all()
        
        return [self._to_entity(model) for model in dataset_models]
    
    async def get_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """이름으로 데이터셋 조회 (페이징)"""
        result = await self.session.execute(
            select(DatasetModel)
            .where(DatasetModel.name == name)
            .order_by(DatasetModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        dataset_models = result.scalars().all()
        
        return [self._to_entity(model) for model in dataset_models]
    
    async def get_by_tag(self, tag: str, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """태그로 데이터셋 조회 (페이징)"""
        result = await self.session.execute(
            select(DatasetModel)
            .where(DatasetModel.tags.contains([tag]))
            .order_by(DatasetModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        dataset_models = result.scalars().all()
        
        return [self._to_entity(model) for model in dataset_models]
    
    async def update(self, dataset: Dataset) -> Dataset:
        """데이터셋 업데이트"""
        # 기존 모델 조회
        result = await self.session.execute(
            select(DatasetModel).where(DatasetModel.dataset_id == dataset.dataset_id)
        )
        dataset_model = result.scalar_one_or_none()
        
        if not dataset_model:
            raise ValueError(f"Dataset with ID {dataset.dataset_id} not found")
        
        # 모델 업데이트
        self._update_model_from_entity(dataset_model, dataset)
        
        await self.session.commit()
        await self.session.refresh(dataset_model)
        
        return self._to_entity(dataset_model)
    
    async def delete(self, dataset_id: UUID) -> bool:
        """데이터셋 삭제"""
        result = await self.session.execute(
            delete(DatasetModel).where(DatasetModel.dataset_id == dataset_id)
        )
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def count(self) -> int:
        """전체 데이터셋 개수"""
        result = await self.session.execute(
            select(func.count(DatasetModel.dataset_id))
        )
        return result.scalar()
    
    async def count_by_name(self, name: str) -> int:
        """이름별 데이터셋 개수"""
        result = await self.session.execute(
            select(func.count(DatasetModel.dataset_id))
            .where(DatasetModel.name == name)
        )
        return result.scalar()
    
    async def count_by_tag(self, tag: str) -> int:
        """태그별 데이터셋 개수"""
        result = await self.session.execute(
            select(func.count(DatasetModel.dataset_id))
            .where(DatasetModel.tags.contains([tag]))
        )
        return result.scalar()
    
    def _to_model(self, dataset: Dataset) -> DatasetModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        return DatasetModel(
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
    
    def _to_entity(self, dataset_model: DatasetModel) -> Dataset:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return Dataset(
            dataset_id=dataset_model.dataset_id,
            name=dataset_model.name,
            version=dataset_model.version,
            storage_path=dataset_model.storage_path,
            description=dataset_model.description,
            creator_name=dataset_model.creator_name,
            creator_email=dataset_model.creator_email,
            source_url=dataset_model.source_url,
            license=dataset_model.license,
            class_schema=dataset_model.class_schema,
            tags=dataset_model.tags or [],
            created_at=dataset_model.created_at
        )
    
    def _update_model_from_entity(self, model: DatasetModel, entity: Dataset) -> None:
        """도메인 엔티티로부터 SQLAlchemy 모델 업데이트"""
        model.name = entity.name
        model.version = entity.version
        model.storage_path = entity.storage_path
        model.description = entity.description
        model.creator_name = entity.creator_name
        model.creator_email = entity.creator_email
        model.source_url = entity.source_url
        model.license = entity.license
        model.class_schema = entity.class_schema
        model.tags = entity.tags
