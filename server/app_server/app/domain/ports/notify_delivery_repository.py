from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class NotifyDeliveryRepository(ABC):
    @abstractmethod
    async def create(self, payload: dict) -> dict: ...

    @abstractmethod
    async def get_by_id(self, delivery_id: int) -> Optional[dict]: ...

    @abstractmethod
    async def list(self, *, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None, status: Optional[str] = None) -> List[dict]: ...

    @abstractmethod
    async def update(self, delivery_id: int, payload: dict) -> Optional[dict]: ...

    @abstractmethod
    async def delete(self, delivery_id: int) -> bool: ...

    # status helpers
    @abstractmethod
    async def mark_sent(self, delivery_id: int) -> Optional[dict]: ...

    @abstractmethod
    async def mark_delivered(self, delivery_id: int) -> Optional[dict]: ...

    @abstractmethod
    async def mark_read(self, delivery_id: int) -> Optional[dict]: ...

    @abstractmethod
    async def mark_ack(self, delivery_id: int) -> Optional[dict]: ...

    @abstractmethod
    async def next_queued(self, limit: int = 100) -> List[dict]: ...


