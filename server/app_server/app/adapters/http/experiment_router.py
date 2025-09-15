"""
실험 RESTful API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_ml_session
from app.adapters.repositories.experiment_repository_impl import ExperimentRepositoryImpl
from app.application.use_cases.experiment_use_cases import (
    CreateExperimentUseCase,
    GetExperimentUseCase,
    ListExperimentsUseCase,
    ListExperimentsByDatasetUseCase,
    UpdateExperimentUseCase,
    DeleteExperimentUseCase
)
from app.domain.services.experiment_service import ExperimentService
from app.application.dto.experiment_dto import (
    ExperimentCreateRequest,
    ExperimentUpdateRequest,
    ExperimentResponse
)

router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])

def get_experiment_repository(session: AsyncSession = Depends(get_ml_session)) -> ExperimentRepositoryImpl:
    """실험 리포지토리 의존성 주입"""
    return ExperimentRepositoryImpl(session)

def get_experiment_service() -> ExperimentService:
    """실험 서비스 의존성 주입"""
    return ExperimentService()

@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    request: ExperimentCreateRequest,
    repository: ExperimentRepositoryImpl = Depends(get_experiment_repository),
    service: ExperimentService = Depends(get_experiment_service)
):
    """실험 생성"""
    try:
        use_case = CreateExperimentUseCase(repository, service)
        return await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create experiment: {str(e)}"
        )

@router.get("/", response_model=List[ExperimentResponse])
async def list_experiments(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    repository: ExperimentRepositoryImpl = Depends(get_experiment_repository)
):
    """실험 목록 조회"""
    try:
        use_case = ListExperimentsUseCase(repository)
        return await use_case.execute(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list experiments: {str(e)}"
        )

@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: UUID,
    repository: ExperimentRepositoryImpl = Depends(get_experiment_repository)
):
    """특정 실험 조회"""
    try:
        use_case = GetExperimentUseCase(repository)
        experiment = await use_case.execute(experiment_id)
        
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment not found"
            )
        
        return experiment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get experiment: {str(e)}"
        )

@router.get("/dataset/{dataset_id}", response_model=List[ExperimentResponse])
async def list_experiments_by_dataset(
    dataset_id: UUID,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    repository: ExperimentRepositoryImpl = Depends(get_experiment_repository)
):
    """데이터셋으로 실험 목록 조회"""
    try:
        use_case = ListExperimentsByDatasetUseCase(repository)
        return await use_case.execute(dataset_id=dataset_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list experiments by dataset: {str(e)}"
        )

@router.put("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: UUID,
    request: ExperimentUpdateRequest,
    repository: ExperimentRepositoryImpl = Depends(get_experiment_repository),
    service: ExperimentService = Depends(get_experiment_service)
):
    """실험 업데이트"""
    try:
        use_case = UpdateExperimentUseCase(repository, service)
        result = await use_case.execute(experiment_id, request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update experiment: {str(e)}"
        )

@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
    experiment_id: UUID,
    repository: ExperimentRepositoryImpl = Depends(get_experiment_repository)
):
    """실험 삭제"""
    try:
        use_case = DeleteExperimentUseCase(repository)
        success = await use_case.execute(experiment_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete experiment: {str(e)}"
        )