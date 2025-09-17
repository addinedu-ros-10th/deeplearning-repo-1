"""
프레임 추론 RESTful API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_ml_session
from app.adapters.repositories.frame_prediction_repository_impl import FramePredictionRepositoryImpl
from app.application.use_cases.frame_prediction_use_cases import (
    CreateFramePredictionUseCase,
    CreateFramePredictionsBatchUseCase,
    GetFramePredictionUseCase,
    ListFramePredictionsUseCase,
    DeleteFramePredictionUseCase,
)
from app.application.dto.frame_prediction_dto import (
    FramePredictionCreateRequest,
    FramePredictionBatchCreateRequest,
    FramePredictionResponse,
)


router = APIRouter(prefix="/api/v1/frame-predictions", tags=["frame-predictions"])


def get_repository(session: AsyncSession = Depends(get_ml_session)) -> FramePredictionRepositoryImpl:
    return FramePredictionRepositoryImpl(session)


@router.post("/", response_model=FramePredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_frame_prediction(
    request: FramePredictionCreateRequest,
    repository: FramePredictionRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = CreateFramePredictionUseCase(repository)
        entity = await use_case.execute(request)
        return entity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create frame prediction: {str(e)}")


@router.post("/batch", response_model=List[FramePredictionResponse], status_code=status.HTTP_201_CREATED)
async def create_frame_predictions_batch(
    request: FramePredictionBatchCreateRequest,
    repository: FramePredictionRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = CreateFramePredictionsBatchUseCase(repository)
        entities = await use_case.execute(request.items)
        return entities
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create batch frame predictions: {str(e)}")


@router.get("/", response_model=List[FramePredictionResponse])
async def list_frame_predictions(
    session_id: Optional[UUID] = Query(None),
    experiment_id: Optional[UUID] = Query(None),
    input_uri: Optional[str] = Query(None),
    label_pred: Optional[str] = Query(None, pattern="^(normal|warning|fall)$"),
    frame_index_from: Optional[int] = Query(None, ge=0),
    frame_index_to: Optional[int] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: FramePredictionRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = ListFramePredictionsUseCase(repository)
        return await use_case.execute(
            session_id=session_id,
            experiment_id=experiment_id,
            input_uri=input_uri,
            label_pred=label_pred,
            frame_index_from=frame_index_from,
            frame_index_to=frame_index_to,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list frame predictions: {str(e)}")


@router.get("/{frame_pred_id}", response_model=FramePredictionResponse)
async def get_frame_prediction(
    frame_pred_id: int,
    repository: FramePredictionRepositoryImpl = Depends(get_repository),
):
    entity = await GetFramePredictionUseCase(repository).execute(frame_pred_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frame prediction not found")
    return entity


@router.delete("/{frame_pred_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_frame_prediction(
    frame_pred_id: int,
    repository: FramePredictionRepositoryImpl = Depends(get_repository),
):
    ok = await DeleteFramePredictionUseCase(repository).execute(frame_pred_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frame prediction not found")


