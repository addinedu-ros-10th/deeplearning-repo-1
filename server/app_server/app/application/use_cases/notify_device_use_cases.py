from typing import Optional
from uuid import UUID
from app.domain.ports.notify_device_repository import NotifyDeviceRepository
from app.application.dto.notify_device_dto import (
    NotifyDeviceCreateRequest,
    NotifyDeviceUpdateRequest,
)


class CreateNotifyDeviceUseCase:
    def __init__(self, repo: NotifyDeviceRepository):
        self.repo = repo

    async def execute(self, req: NotifyDeviceCreateRequest):
        return await self.repo.create(req.model_dump(exclude_unset=True))


class GetNotifyDeviceUseCase:
    def __init__(self, repo: NotifyDeviceRepository):
        self.repo = repo

    async def execute(self, device_id: UUID):
        return await self.repo.get_by_id(device_id)


class ListNotifyDevicesUseCase:
    def __init__(self, repo: NotifyDeviceRepository):
        self.repo = repo

    async def execute(self, *, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None, channel: Optional[str] = None, is_active: Optional[bool] = None):
        return await self.repo.list(skip=skip, limit=limit, user_id=user_id, channel=channel, is_active=is_active)


class UpdateNotifyDeviceUseCase:
    def __init__(self, repo: NotifyDeviceRepository):
        self.repo = repo

    async def execute(self, device_id: UUID, req: NotifyDeviceUpdateRequest):
        return await self.repo.update(device_id, req.model_dump(exclude_unset=True))


class DeleteNotifyDeviceUseCase:
    def __init__(self, repo: NotifyDeviceRepository):
        self.repo = repo

    async def execute(self, device_id: UUID) -> bool:
        return await self.repo.delete(device_id)


