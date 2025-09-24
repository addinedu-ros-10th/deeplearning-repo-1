from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.notify_message import NotifyMessage


class NotifyMessageRepository(ABC):
    @abstractmethod
    async def create(self, payload: dict) -> NotifyMessage: ...

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Optional[NotifyMessage]: ...

    @abstractmethod
    async def list(self, *, skip: int = 0, limit: int = 100, kind: Optional[str] = None, severity: Optional[str] = None) -> List[NotifyMessage]: ...

    @abstractmethod
    async def update(self, message_id: UUID, payload: dict) -> Optional[NotifyMessage]: ...

    @abstractmethod
    async def delete(self, message_id: UUID) -> bool: ...


