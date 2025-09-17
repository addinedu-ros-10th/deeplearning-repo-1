"""
프레임 추론 리포지토리 포트
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.frame_prediction import FramePrediction


class FramePredictionRepository(ABC):
    """프레임 추론 리포지토리 인터페이스"""

    @abstractmethod
    async def save(self, entity: FramePrediction) -> FramePrediction:
        pass

    @abstractmethod
    async def save_many(self, entities: List[FramePrediction]) -> List[FramePrediction]:
        pass

    @abstractmethod
    async def get_by_id(self, frame_pred_id: int) -> Optional[FramePrediction]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, frame_pred_id: int) -> bool:
        pass


