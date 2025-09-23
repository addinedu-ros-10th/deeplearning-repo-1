from typing import List, Optional
from uuid import UUID
from app.domain.ports.notify_message_repository import NotifyMessageRepository
from app.application.dto.notify_message_dto import (
    NotifyMessageCreateRequest,
    NotifyMessageUpdateRequest,
)


class CreateNotifyMessageUseCase:
    def __init__(self, repo: NotifyMessageRepository):
        self.repo = repo

    async def execute(self, req: NotifyMessageCreateRequest):
        payload = req.model_dump(exclude_unset=True)
        return await self.repo.create(payload)


class GetNotifyMessageUseCase:
    def __init__(self, repo: NotifyMessageRepository):
        self.repo = repo

    async def execute(self, message_id: UUID):
        return await self.repo.get_by_id(message_id)


class ListNotifyMessagesUseCase:
    def __init__(self, repo: NotifyMessageRepository):
        self.repo = repo

    async def execute(self, *, skip: int = 0, limit: int = 100, kind: Optional[str] = None, severity: Optional[str] = None):
        return await self.repo.list(skip=skip, limit=limit, kind=kind, severity=severity)


class UpdateNotifyMessageUseCase:
    def __init__(self, repo: NotifyMessageRepository):
        self.repo = repo

    async def execute(self, message_id: UUID, req: NotifyMessageUpdateRequest):
        payload = req.model_dump(exclude_unset=True)
        return await self.repo.update(message_id, payload)


class DeleteNotifyMessageUseCase:
    def __init__(self, repo: NotifyMessageRepository):
        self.repo = repo

    async def execute(self, message_id: UUID) -> bool:
        return await self.repo.delete(message_id)


