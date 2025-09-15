"""
실험 유즈케이스
실험 관련 비즈니스 로직 구현
"""

from typing import List, Optional
from uuid import UUID
from app.domain.entities.experiment import Experiment
from app.domain.ports.experiment_repository import ExperimentRepository
from app.domain.services.experiment_service import ExperimentService
from app.application.dto.experiment_dto import ExperimentCreateRequest, ExperimentUpdateRequest, ExperimentResponse

class CreateExperimentUseCase:
    """실험 생성 유즈케이스"""
    
    def __init__(self, experiment_repository: ExperimentRepository, experiment_service: ExperimentService):
        self.experiment_repository = experiment_repository
        self.experiment_service = experiment_service
    
    async def execute(self, request: ExperimentCreateRequest) -> ExperimentResponse:
        """실험 생성 실행"""
        # 도메인 엔티티 생성
        experiment = Experiment(
            name=request.name,
            dataset_id=request.dataset_id,
            model_path=request.model_path,
            framework=request.framework,
            code_version=request.code_version,
            params=request.params,
            metrics=request.metrics
        )
        
        # 도메인 서비스로 검증
        self.experiment_service.validate_experiment_creation(experiment)
        
        # 리포지토리에 저장
        created_experiment = await self.experiment_repository.save(experiment)
        
        # 응답 DTO로 변환
        return ExperimentResponse.model_validate(created_experiment)

class GetExperimentUseCase:
    """실험 조회 유즈케이스"""
    
    def __init__(self, experiment_repository: ExperimentRepository):
        self.experiment_repository = experiment_repository
    
    async def execute(self, experiment_id: UUID) -> Optional[ExperimentResponse]:
        """실험 조회 실행"""
        experiment = await self.experiment_repository.get_by_id(experiment_id)
        if experiment:
            return ExperimentResponse.model_validate(experiment)
        return None

class UpdateExperimentUseCase:
    """실험 업데이트 유즈케이스"""
    
    def __init__(self, experiment_repository: ExperimentRepository, experiment_service: ExperimentService):
        self.experiment_repository = experiment_repository
        self.experiment_service = experiment_service
    
    async def execute(self, experiment_id: UUID, request: ExperimentUpdateRequest) -> Optional[ExperimentResponse]:
        """실험 업데이트 실행"""
        # 기존 실험 조회
        existing_experiment = await self.experiment_repository.get_by_id(experiment_id)
        if not existing_experiment:
            return None
        
        # 업데이트할 필드만 적용
        update_data = request.dict(exclude_unset=True)
        updated_experiment = self.experiment_service.update_experiment_details(existing_experiment, update_data)
        
        # 리포지토리에 저장
        saved_experiment = await self.experiment_repository.update(updated_experiment)
        
        # 응답 DTO로 변환
        return ExperimentResponse.model_validate(saved_experiment)

class DeleteExperimentUseCase:
    """실험 삭제 유즈케이스"""
    
    def __init__(self, experiment_repository: ExperimentRepository):
        self.experiment_repository = experiment_repository
    
    async def execute(self, experiment_id: UUID) -> bool:
        """실험 삭제 실행"""
        return await self.experiment_repository.delete(experiment_id)

class ListExperimentsUseCase:
    """실험 목록 조회 유즈케이스"""
    
    def __init__(self, experiment_repository: ExperimentRepository):
        self.experiment_repository = experiment_repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[ExperimentResponse]:
        """실험 목록 조회 실행"""
        experiments = await self.experiment_repository.get_all(skip=skip, limit=limit)
        return [ExperimentResponse.model_validate(experiment) for experiment in experiments]

class ListExperimentsByDatasetUseCase:
    """데이터셋으로 실험 목록 조회 유즈케이스"""
    
    def __init__(self, experiment_repository: ExperimentRepository):
        self.experiment_repository = experiment_repository
    
    async def execute(self, dataset_id: UUID, skip: int = 0, limit: int = 100) -> List[ExperimentResponse]:
        """실험 목록 조회 실행"""
        experiments = await self.experiment_repository.get_by_dataset_id(dataset_id, skip=skip, limit=limit)
        return [ExperimentResponse.model_validate(experiment) for experiment in experiments]