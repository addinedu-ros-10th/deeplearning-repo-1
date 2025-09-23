from typing import Optional
from uuid import UUID
from app.domain.ports.notify_delivery_repository import NotifyDeliveryRepository
from app.application.dto.notify_delivery_dto import (
    NotifyDeliveryCreateRequest,
    NotifyDeliveryUpdateRequest,
)


class CreateNotifyDeliveryUseCase:
    def __init__(self, repo: NotifyDeliveryRepository):
        self.repo = repo

    async def execute(self, req: NotifyDeliveryCreateRequest):
        return await self.repo.create(req.model_dump(exclude_unset=True))


class GetNotifyDeliveryUseCase:
    def __init__(self, repo: NotifyDeliveryRepository):
        self.repo = repo

    async def execute(self, delivery_id: int):
        return await self.repo.get_by_id(delivery_id)


class ListNotifyDeliveriesUseCase:
    def __init__(self, repo: NotifyDeliveryRepository):
        self.repo = repo

    async def execute(self, *, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None, status: Optional[str] = None):
        return await self.repo.list(skip=skip, limit=limit, user_id=user_id, status=status)


class UpdateNotifyDeliveryUseCase:
    def __init__(self, repo: NotifyDeliveryRepository):
        self.repo = repo

    async def execute(self, delivery_id: int, req: NotifyDeliveryUpdateRequest):
        return await self.repo.update(delivery_id, req.model_dump(exclude_unset=True))


class DeleteNotifyDeliveryUseCase:
    def __init__(self, repo: NotifyDeliveryRepository):
        self.repo = repo

    async def execute(self, delivery_id: int) -> bool:
        return await self.repo.delete(delivery_id)


