"""
프레임 추론 리포지토리 구현
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete

from app.domain.entities.frame_prediction import FramePrediction
from app.domain.ports.frame_prediction_repository import FramePredictionRepository
from app.infrastructure.db.models.ml_models import FramePredictionModel


class FramePredictionRepositoryImpl(FramePredictionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: FramePrediction) -> FramePrediction:
        model = FramePredictionModel(
            session_id=entity.session_id,
            experiment_id=entity.experiment_id,
            input_uri=entity.input_uri,
            frame_index=entity.frame_index,
            ts_rel_ms=entity.ts_rel_ms,
            label_pred=entity.label_pred,
            confidence=entity.confidence,
            probabilities=entity.probabilities,
            passed=entity.passed,
            threshold_name=entity.threshold_name,
            threshold_snapshot=entity.threshold_snapshot,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        entity.frame_pred_id = model.frame_pred_id
        entity.created_at = model.created_at
        return entity

    async def save_many(self, entities: List[FramePrediction]) -> List[FramePrediction]:
        values = [
            {
                "session_id": e.session_id,
                "experiment_id": e.experiment_id,
                "input_uri": e.input_uri,
                "frame_index": e.frame_index,
                "ts_rel_ms": e.ts_rel_ms,
                "label_pred": e.label_pred,
                "confidence": e.confidence,
                "probabilities": e.probabilities,
                "passed": e.passed,
                "threshold_name": e.threshold_name,
                "threshold_snapshot": e.threshold_snapshot,
            }
            for e in entities
        ]
        stmt = insert(FramePredictionModel).values(values).returning(FramePredictionModel.frame_pred_id, FramePredictionModel.created_at)
        result = await self.session.execute(stmt)
        await self.session.commit()
        ids_and_created = result.fetchall()
        for e, (fp_id, created_at) in zip(entities, ids_and_created):
            e.frame_pred_id = fp_id
            e.created_at = created_at
        return entities

    async def get_by_id(self, frame_pred_id: int) -> Optional[FramePrediction]:
        result = await self.session.execute(
            select(FramePredictionModel).where(FramePredictionModel.frame_pred_id == frame_pred_id)
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
        label_pred: Optional[str] = None,
        frame_index_from: Optional[int] = None,
        frame_index_to: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FramePrediction]:
        stmt = select(FramePredictionModel).order_by(FramePredictionModel.frame_pred_id).offset(skip).limit(limit)
        if session_id is not None:
            stmt = stmt.where(FramePredictionModel.session_id == session_id)
        if experiment_id is not None:
            stmt = stmt.where(FramePredictionModel.experiment_id == experiment_id)
        if input_uri is not None:
            stmt = stmt.where(FramePredictionModel.input_uri == input_uri)
        if label_pred is not None:
            stmt = stmt.where(FramePredictionModel.label_pred == label_pred)
        if frame_index_from is not None:
            stmt = stmt.where(FramePredictionModel.frame_index >= frame_index_from)
        if frame_index_to is not None:
            stmt = stmt.where(FramePredictionModel.frame_index <= frame_index_to)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, frame_pred_id: int) -> bool:
        result = await self.session.execute(
            delete(FramePredictionModel).where(FramePredictionModel.frame_pred_id == frame_pred_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    def _to_entity(self, m: FramePredictionModel) -> FramePrediction:
        return FramePrediction(
            frame_pred_id=m.frame_pred_id,
            session_id=m.session_id,
            experiment_id=m.experiment_id,
            input_uri=m.input_uri,
            frame_index=m.frame_index,
            ts_rel_ms=m.ts_rel_ms,
            label_pred=m.label_pred,
            confidence=float(m.confidence) if m.confidence is not None else None,
            probabilities=m.probabilities,
            passed=m.passed,
            threshold_name=m.threshold_name,
            threshold_snapshot=m.threshold_snapshot,
            created_at=m.created_at,
        )


