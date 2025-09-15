"""
실험 리포지토리 구현
SQLAlchemy 기반 실험 리포지토리
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from app.domain.entities.experiment import Experiment
from app.domain.ports.experiment_repository import ExperimentRepository
from app.infrastructure.db.models.ml_models import ExperimentModel

class ExperimentRepositoryImpl(ExperimentRepository):
    """실험 리포지토리 구현체"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, experiment: Experiment) -> Experiment:
        """실험 저장"""
        # SQLAlchemy 모델로 변환
        experiment_model = self._to_model(experiment)
        
        self.session.add(experiment_model)
        await self.session.commit()
        await self.session.refresh(experiment_model)
        
        return self._to_entity(experiment_model)
    
    async def get_by_id(self, experiment_id: UUID) -> Optional[Experiment]:
        """ID로 실험 조회"""
        result = await self.session.execute(
            select(ExperimentModel).where(ExperimentModel.experiment_id == experiment_id)
        )
        experiment_model = result.scalar_one_or_none()
        
        if not experiment_model:
            return None
        
        return self._to_entity(experiment_model)
    
    async def get_by_name_and_dataset(self, name: str, dataset_id: UUID) -> Optional[Experiment]:
        """이름과 데이터셋 ID로 실험 조회"""
        result = await self.session.execute(
            select(ExperimentModel).where(
                ExperimentModel.name == name,
                ExperimentModel.dataset_id == dataset_id
            )
        )
        experiment_model = result.scalar_one_or_none()
        
        if not experiment_model:
            return None
        
        return self._to_entity(experiment_model)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Experiment]:
        """모든 실험 조회 (페이징)"""
        result = await self.session.execute(
            select(ExperimentModel)
            .order_by(ExperimentModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        experiment_models = result.scalars().all()
        
        return [self._to_entity(model) for model in experiment_models]
    
    async def get_by_dataset_id(self, dataset_id: UUID, skip: int = 0, limit: int = 100) -> List[Experiment]:
        """데이터셋 ID로 실험 조회 (페이징)"""
        result = await self.session.execute(
            select(ExperimentModel)
            .where(ExperimentModel.dataset_id == dataset_id)
            .order_by(ExperimentModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        experiment_models = result.scalars().all()
        
        return [self._to_entity(model) for model in experiment_models]
    
    async def get_by_framework(self, framework: str, skip: int = 0, limit: int = 100) -> List[Experiment]:
        """프레임워크로 실험 조회 (페이징)"""
        result = await self.session.execute(
            select(ExperimentModel)
            .where(ExperimentModel.framework == framework)
            .order_by(ExperimentModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        experiment_models = result.scalars().all()
        
        return [self._to_entity(model) for model in experiment_models]
    
    async def update(self, experiment: Experiment) -> Experiment:
        """실험 업데이트"""
        # 기존 모델 조회
        result = await self.session.execute(
            select(ExperimentModel).where(ExperimentModel.experiment_id == experiment.experiment_id)
        )
        experiment_model = result.scalar_one_or_none()
        
        if not experiment_model:
            raise ValueError(f"Experiment with ID {experiment.experiment_id} not found")
        
        # 모델 업데이트
        self._update_model_from_entity(experiment_model, experiment)
        
        await self.session.commit()
        await self.session.refresh(experiment_model)
        
        return self._to_entity(experiment_model)
    
    async def delete(self, experiment_id: UUID) -> bool:
        """실험 삭제"""
        result = await self.session.execute(
            delete(ExperimentModel).where(ExperimentModel.experiment_id == experiment_id)
        )
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def count(self) -> int:
        """전체 실험 개수"""
        result = await self.session.execute(
            select(func.count(ExperimentModel.experiment_id))
        )
        return result.scalar()
    
    async def count_by_dataset_id(self, dataset_id: UUID) -> int:
        """데이터셋별 실험 개수"""
        result = await self.session.execute(
            select(func.count(ExperimentModel.experiment_id))
            .where(ExperimentModel.dataset_id == dataset_id)
        )
        return result.scalar()
    
    async def count_by_framework(self, framework: str) -> int:
        """프레임워크별 실험 개수"""
        result = await self.session.execute(
            select(func.count(ExperimentModel.experiment_id))
            .where(ExperimentModel.framework == framework)
        )
        return result.scalar()
    
    def _to_model(self, experiment: Experiment) -> ExperimentModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        return ExperimentModel(
            experiment_id=experiment.experiment_id,
            name=experiment.name,
            dataset_id=experiment.dataset_id,
            model_path=experiment.model_path,
            framework=experiment.framework,
            code_version=experiment.code_version,
            params=experiment.params,
            metrics=experiment.metrics,
            created_at=experiment.created_at
        )
    
    def _to_entity(self, experiment_model: ExperimentModel) -> Experiment:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return Experiment(
            experiment_id=experiment_model.experiment_id,
            name=experiment_model.name,
            dataset_id=experiment_model.dataset_id,
            model_path=experiment_model.model_path,
            framework=experiment_model.framework,
            code_version=experiment_model.code_version,
            params=experiment_model.params or {},
            metrics=experiment_model.metrics or {},
            created_at=experiment_model.created_at
        )
    
    def _update_model_from_entity(self, model: ExperimentModel, entity: Experiment) -> None:
        """도메인 엔티티로부터 SQLAlchemy 모델 업데이트"""
        model.name = entity.name
        model.dataset_id = entity.dataset_id
        model.model_path = entity.model_path
        model.framework = entity.framework
        model.code_version = entity.code_version
        model.params = entity.params
        model.metrics = entity.metrics
