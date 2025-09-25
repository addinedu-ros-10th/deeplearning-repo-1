from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class NotifyDeviceRepository(ABC):
    @abstractmethod
    async def create(self, payload: dict) -> dict: ...

    @abstractmethod
    async def get_by_id(self, device_id: UUID) -> Optional[dict]: ...

    @abstractmethod
    async def list(self, *, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None, channel: Optional[str] = None, is_active: Optional[bool] = None) -> List[dict]: ...

    @abstractmethod
    async def update(self, device_id: UUID, payload: dict) -> Optional[dict]: ...

    @abstractmethod
    async def delete(self, device_id: UUID) -> bool: ...


