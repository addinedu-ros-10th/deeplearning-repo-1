"""
이벤트 유즈케이스
"""

from typing import List, Optional
from uuid import UUID
from app.domain.entities.detection_event import DetectionEvent
from app.domain.ports.detection_event_repository import DetectionEventRepository
from app.application.dto.detection_event_dto import (
    DetectionEventCreateRequest,
)


class CreateDetectionEventUseCase:
    def __init__(self, repository: DetectionEventRepository):
        self.repository = repository

    async def execute(self, request: DetectionEventCreateRequest) -> DetectionEvent:
        entity = DetectionEvent(
            session_id=request.session_id,
            experiment_id=request.experiment_id,
            input_uri=request.input_uri,
            start_frame=request.start_frame,
            end_frame=request.end_frame,
            event_type=request.event_type,
            top_label=request.top_label,
            threshold_snapshot=request.threshold_snapshot,
            start_ts_ms=request.start_ts_ms,
            end_ts_ms=request.end_ts_ms,
            max_confidence=request.max_confidence,
            agg_prob=request.agg_prob,
            threshold_name=request.threshold_name,
            trigger_reason=request.trigger_reason,
        )
        if not entity.is_valid():
            raise ValueError("Invalid DetectionEvent payload")
        return await self.repository.save(entity)


class GetDetectionEventUseCase:
    def __init__(self, repository: DetectionEventRepository):
        self.repository = repository

    async def execute(self, event_id: UUID) -> Optional[DetectionEvent]:
        return await self.repository.get_by_id(event_id)


class ListDetectionEventsUseCase:
    def __init__(self, repository: DetectionEventRepository):
        self.repository = repository

    async def execute(
        self,
        *,
        session_id: Optional[UUID] = None,
        experiment_id: Optional[UUID] = None,
        input_uri: Optional[str] = None,
        event_type: Optional[str] = None,
        top_label: Optional[str] = None,
        start_ts_ms_from: Optional[int] = None,
        start_ts_ms_to: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DetectionEvent]:
        return await self.repository.list(
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


class DeleteDetectionEventUseCase:
    def __init__(self, repository: DetectionEventRepository):
        self.repository = repository

    async def execute(self, event_id: UUID) -> bool:
        return await self.repository.delete(event_id)


