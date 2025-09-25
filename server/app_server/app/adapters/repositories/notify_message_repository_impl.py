from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.domain.entities.notify_message import NotifyMessage
from app.domain.ports.notify_message_repository import NotifyMessageRepository
from app.infrastructure.db.models.notify_models import NotifyMessage as NotifyMessageModel


class NotifyMessageRepositoryImpl(NotifyMessageRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: dict) -> NotifyMessage:
        stmt = insert(NotifyMessageModel).values(**payload).returning(NotifyMessageModel)
        res = await self.session.execute(stmt)
        await self.session.commit()
        model = res.scalar_one()
        return self._to_entity(model)

    async def get_by_id(self, message_id: UUID) -> Optional[NotifyMessage]:
        res = await self.session.execute(select(NotifyMessageModel).where(NotifyMessageModel.message_id == message_id))
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, *, skip: int = 0, limit: int = 100, kind: Optional[str] = None, severity: Optional[str] = None) -> List[NotifyMessage]:
        stmt = select(NotifyMessageModel).offset(skip).limit(limit).order_by(NotifyMessageModel.created_at.desc())
        if kind:
            stmt = stmt.where(NotifyMessageModel.kind == kind)
        if severity:
            stmt = stmt.where(NotifyMessageModel.severity == severity)
        res = await self.session.execute(stmt)
        return [self._to_entity(m) for m in res.scalars().all()]

    async def update(self, message_id: UUID, payload: dict) -> Optional[NotifyMessage]:
        await self.session.execute(
            update(NotifyMessageModel).where(NotifyMessageModel.message_id == message_id).values(**payload)
        )
        await self.session.commit()
        res = await self.session.execute(select(NotifyMessageModel).where(NotifyMessageModel.message_id == message_id))
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete(self, message_id: UUID) -> bool:
        res = await self.session.execute(delete(NotifyMessageModel).where(NotifyMessageModel.message_id == message_id))
        await self.session.commit()
        return res.rowcount > 0

    @staticmethod
    def _to_entity(m: NotifyMessageModel) -> NotifyMessage:
        return NotifyMessage(
            message_id=m.message_id,
            kind=m.kind,
            severity=m.severity,
            title=m.title,
            body=m.body,
            data=m.data,
            scheduled_at=m.scheduled_at,
            expires_at=m.expires_at,
            created_by=m.created_by,
            created_ip=str(m.created_ip) if m.created_ip else None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


