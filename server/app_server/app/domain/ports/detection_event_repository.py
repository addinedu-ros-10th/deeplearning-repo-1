"""
이벤트 리포지토리 포트
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.detection_event import DetectionEvent


class DetectionEventRepository(ABC):
    """이벤트 리포지토리 인터페이스"""

    @abstractmethod
    async def save(self, entity: DetectionEvent) -> DetectionEvent:
        pass

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[DetectionEvent]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, event_id: UUID) -> bool:
        pass


