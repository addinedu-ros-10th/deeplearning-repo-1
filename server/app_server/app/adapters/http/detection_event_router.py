"""
이벤트 RESTful API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_ml_session
from app.adapters.repositories.detection_event_repository_impl import DetectionEventRepositoryImpl
from app.application.use_cases.detection_event_use_cases import (
    CreateDetectionEventUseCase,
    GetDetectionEventUseCase,
    ListDetectionEventsUseCase,
    DeleteDetectionEventUseCase,
)
from app.application.dto.detection_event_dto import (
    DetectionEventCreateRequest,
    DetectionEventResponse,
)


router = APIRouter(prefix="/api/v1/detection-events", tags=["detection-events"])


def get_repository(session: AsyncSession = Depends(get_ml_session)) -> DetectionEventRepositoryImpl:
    return DetectionEventRepositoryImpl(session)


@router.post("/", response_model=DetectionEventResponse, status_code=status.HTTP_201_CREATED)
async def create_detection_event(
    request: DetectionEventCreateRequest,
    repository: DetectionEventRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = CreateDetectionEventUseCase(repository)
        entity = await use_case.execute(request)
        return entity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create detection event: {str(e)}")


@router.get("/", response_model=List[DetectionEventResponse])
async def list_detection_events(
    session_id: Optional[UUID] = Query(None),
    experiment_id: Optional[UUID] = Query(None),
    input_uri: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    top_label: Optional[str] = Query(None, pattern="^(normal|warning|fall)$"),
    start_ts_ms_from: Optional[int] = Query(None, ge=0),
    start_ts_ms_to: Optional[int] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: DetectionEventRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = ListDetectionEventsUseCase(repository)
        return await use_case.execute(
            session_id=session_id,
            experiment_id=experiment_id,
            input_uri=input_uri,
            event_type=event_type,
            top_label=top_label,
            start_ts_ms_from=start_ts_ms_from,
            start_ts_ms_to=start_ts_ms_to,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list detection events: {str(e)}")


@router.get("/{event_id}", response_model=DetectionEventResponse)
async def get_detection_event(
    event_id: UUID,
    repository: DetectionEventRepositoryImpl = Depends(get_repository),
):
    entity = await GetDetectionEventUseCase(repository).execute(event_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection event not found")
    return entity


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detection_event(
    event_id: UUID,
    repository: DetectionEventRepositoryImpl = Depends(get_repository),
):
    ok = await DeleteDetectionEventUseCase(repository).execute(event_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection event not found")


