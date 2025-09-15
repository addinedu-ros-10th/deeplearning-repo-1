"""
데이터셋 RESTful API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_ml_session
from app.adapters.repositories.dataset_repository_impl import DatasetRepositoryImpl
from app.application.use_cases.dataset_use_cases import (
    CreateDatasetUseCase,
    GetDatasetUseCase,
    ListDatasetsUseCase,
    ListDatasetsByNameUseCase,
    ListDatasetsByTagUseCase,
    UpdateDatasetUseCase,
    DeleteDatasetUseCase
)
from app.domain.services.dataset_service import DatasetService
from app.application.dto.dataset_dto import (
    DatasetCreateRequest,
    DatasetUpdateRequest,
    DatasetResponse
)

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])

def get_dataset_repository(session: AsyncSession = Depends(get_ml_session)) -> DatasetRepositoryImpl:
    """데이터셋 리포지토리 의존성 주입"""
    return DatasetRepositoryImpl(session)

def get_dataset_service() -> DatasetService:
    """데이터셋 서비스 의존성 주입"""
    return DatasetService()

@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    request: DatasetCreateRequest,
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository),
    service: DatasetService = Depends(get_dataset_service)
):
    """데이터셋 생성"""
    try:
        use_case = CreateDatasetUseCase(repository, service)
        return await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dataset: {str(e)}"
        )

@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository)
):
    """데이터셋 목록 조회"""
    try:
        use_case = ListDatasetsUseCase(repository)
        return await use_case.execute(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets: {str(e)}"
        )

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: UUID,
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository)
):
    """특정 데이터셋 조회"""
    try:
        use_case = GetDatasetUseCase(repository)
        dataset = await use_case.execute(dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset: {str(e)}"
        )

@router.get("/name/{name}", response_model=List[DatasetResponse])
async def list_datasets_by_name(
    name: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository)
):
    """이름으로 데이터셋 목록 조회"""
    try:
        use_case = ListDatasetsByNameUseCase(repository)
        return await use_case.execute(name=name, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets by name: {str(e)}"
        )

@router.get("/tag/{tag}", response_model=List[DatasetResponse])
async def list_datasets_by_tag(
    tag: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository)
):
    """태그로 데이터셋 목록 조회"""
    try:
        use_case = ListDatasetsByTagUseCase(repository)
        return await use_case.execute(tag=tag, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets by tag: {str(e)}"
        )

@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: UUID,
    request: DatasetUpdateRequest,
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository),
    service: DatasetService = Depends(get_dataset_service)
):
    """데이터셋 업데이트"""
    try:
        use_case = UpdateDatasetUseCase(repository, service)
        result = await use_case.execute(dataset_id, request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dataset: {str(e)}"
        )

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: UUID,
    repository: DatasetRepositoryImpl = Depends(get_dataset_repository)
):
    """데이터셋 삭제"""
    try:
        use_case = DeleteDatasetUseCase(repository)
        success = await use_case.execute(dataset_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset: {str(e)}"
        )