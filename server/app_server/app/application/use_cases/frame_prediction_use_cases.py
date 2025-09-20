"""
프레임 추론 유즈케이스
"""

from typing import List, Optional
from uuid import UUID
from app.domain.entities.frame_prediction import FramePrediction
from app.domain.ports.frame_prediction_repository import FramePredictionRepository
from app.application.dto.frame_prediction_dto import (
    FramePredictionCreateRequest,
)


class CreateFramePredictionUseCase:
    def __init__(self, repository: FramePredictionRepository):
        self.repository = repository

    async def execute(self, request: FramePredictionCreateRequest) -> FramePrediction:
        entity = FramePrediction(
            session_id=request.session_id,
            experiment_id=request.experiment_id,
            input_uri=request.input_uri,
            frame_index=request.frame_index,
            probabilities=request.probabilities,
            label_pred=request.label_pred,
            ts_rel_ms=request.ts_rel_ms,
            confidence=request.confidence,
            passed=request.passed,
            threshold_name=request.threshold_name,
            threshold_snapshot=request.threshold_snapshot,
        )
        if not entity.is_valid():
            raise ValueError("Invalid FramePrediction payload")
        return await self.repository.save(entity)


class CreateFramePredictionsBatchUseCase:
    def __init__(self, repository: FramePredictionRepository):
        self.repository = repository

    async def execute(self, requests: List[FramePredictionCreateRequest]) -> List[FramePrediction]:
        entities = [
            FramePrediction(
                session_id=r.session_id,
                experiment_id=r.experiment_id,
                input_uri=r.input_uri,
                frame_index=r.frame_index,
                probabilities=r.probabilities,
                label_pred=r.label_pred,
                ts_rel_ms=r.ts_rel_ms,
                confidence=r.confidence,
                passed=r.passed,
                threshold_name=r.threshold_name,
                threshold_snapshot=r.threshold_snapshot,
            )
            for r in requests
        ]
        for e in entities:
            if not e.is_valid():
                raise ValueError("Invalid FramePrediction payload in batch")
        return await self.repository.save_many(entities)


class GetFramePredictionUseCase:
    def __init__(self, repository: FramePredictionRepository):
        self.repository = repository

    async def execute(self, frame_pred_id: int) -> Optional[FramePrediction]:
        return await self.repository.get_by_id(frame_pred_id)


class ListFramePredictionsUseCase:
    def __init__(self, repository: FramePredictionRepository):
        self.repository = repository

    async def execute(
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
        return await self.repository.list(
            session_id=session_id,
            experiment_id=experiment_id,
            input_uri=input_uri,
            label_pred=label_pred,
            frame_index_from=frame_index_from,
            frame_index_to=frame_index_to,
            skip=skip,
            limit=limit,
        )


class DeleteFramePredictionUseCase:
    def __init__(self, repository: FramePredictionRepository):
        self.repository = repository

    async def execute(self, frame_pred_id: int) -> bool:
        return await self.repository.delete(frame_pred_id)


