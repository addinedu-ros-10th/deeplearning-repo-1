"""
이벤트 리포지토리 구현
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.domain.entities.detection_event import DetectionEvent
from app.domain.ports.detection_event_repository import DetectionEventRepository
from app.infrastructure.db.models.ml_models import DetectionEventModel


class DetectionEventRepositoryImpl(DetectionEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: DetectionEvent) -> DetectionEvent:
        model = DetectionEventModel(
            event_id=entity.event_id,
            session_id=entity.session_id,
            experiment_id=entity.experiment_id,
            input_uri=entity.input_uri,
            start_frame=entity.start_frame,
            end_frame=entity.end_frame,
            start_ts_ms=entity.start_ts_ms,
            end_ts_ms=entity.end_ts_ms,
            event_type=entity.event_type,
            top_label=entity.top_label,
            max_confidence=entity.max_confidence,
            agg_prob=entity.agg_prob,
            threshold_name=entity.threshold_name,
            threshold_snapshot=entity.threshold_snapshot,
            trigger_reason=entity.trigger_reason,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        entity.created_at = model.created_at
        return entity

    async def get_by_id(self, event_id: UUID) -> Optional[DetectionEvent]:
        result = await self.session.execute(
            select(DetectionEventModel).where(DetectionEventModel.event_id == event_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list(
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
        stmt = select(DetectionEventModel).order_by(DetectionEventModel.created_at.desc()).offset(skip).limit(limit)
        if session_id is not None:
            stmt = stmt.where(DetectionEventModel.session_id == session_id)
        if experiment_id is not None:
            stmt = stmt.where(DetectionEventModel.experiment_id == experiment_id)
        if input_uri is not None:
            stmt = stmt.where(DetectionEventModel.input_uri == input_uri)
        if event_type is not None:
            stmt = stmt.where(DetectionEventModel.event_type == event_type)
        if top_label is not None:
            stmt = stmt.where(DetectionEventModel.top_label == top_label)
        if start_ts_ms_from is not None:
            stmt = stmt.where(DetectionEventModel.start_ts_ms >= start_ts_ms_from)
        if start_ts_ms_to is not None:
            stmt = stmt.where(DetectionEventModel.start_ts_ms <= start_ts_ms_to)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, event_id: UUID) -> bool:
        result = await self.session.execute(
            delete(DetectionEventModel).where(DetectionEventModel.event_id == event_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    def _to_entity(self, m: DetectionEventModel) -> DetectionEvent:
        return DetectionEvent(
            event_id=m.event_id,
            session_id=m.session_id,
            experiment_id=m.experiment_id,
            input_uri=m.input_uri,
            start_frame=m.start_frame,
            end_frame=m.end_frame,
            start_ts_ms=m.start_ts_ms,
            end_ts_ms=m.end_ts_ms,
            event_type=m.event_type,
            top_label=m.top_label,
            max_confidence=float(m.max_confidence) if m.max_confidence is not None else None,
            agg_prob=m.agg_prob,
            threshold_name=m.threshold_name,
            threshold_snapshot=m.threshold_snapshot,
            trigger_reason=m.trigger_reason,
            created_at=m.created_at,
        )


