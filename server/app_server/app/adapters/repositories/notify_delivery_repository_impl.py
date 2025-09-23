from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.infrastructure.db.models.notify_models import NotifyDelivery as NotifyDeliveryModel
from app.domain.ports.notify_delivery_repository import NotifyDeliveryRepository


class NotifyDeliveryRepositoryImpl(NotifyDeliveryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: dict) -> dict:
        stmt = insert(NotifyDeliveryModel).values(**payload).returning(NotifyDeliveryModel)
        res = await self.session.execute(stmt)
        await self.session.commit()
        m = res.scalar_one()
        return self._to_dict(m)

    async def get_by_id(self, delivery_id: int) -> Optional[dict]:
        res = await self.session.execute(select(NotifyDeliveryModel).where(NotifyDeliveryModel.delivery_id == delivery_id))
        m = res.scalar_one_or_none()
        return self._to_dict(m) if m else None

    async def list(self, *, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None, status: Optional[str] = None) -> List[dict]:
        stmt = select(NotifyDeliveryModel).offset(skip).limit(limit).order_by(NotifyDeliveryModel.created_at.desc())
        if user_id:
            stmt = stmt.where(NotifyDeliveryModel.user_id == user_id)
        if status:
            stmt = stmt.where(NotifyDeliveryModel.status == status)
        res = await self.session.execute(stmt)
        return [self._to_dict(m) for m in res.scalars().all()]

    async def update(self, delivery_id: int, payload: dict) -> Optional[dict]:
        await self.session.execute(update(NotifyDeliveryModel).where(NotifyDeliveryModel.delivery_id == delivery_id).values(**payload))
        await self.session.commit()
        res = await self.session.execute(select(NotifyDeliveryModel).where(NotifyDeliveryModel.delivery_id == delivery_id))
        m = res.scalar_one_or_none()
        return self._to_dict(m) if m else None

    async def delete(self, delivery_id: int) -> bool:
        res = await self.session.execute(delete(NotifyDeliveryModel).where(NotifyDeliveryModel.delivery_id == delivery_id))
        await self.session.commit()
        return res.rowcount > 0

    @staticmethod
    def _to_dict(m: NotifyDeliveryModel) -> dict:
        return {
            "delivery_id": m.delivery_id,
            "message_id": m.message_id,
            "user_id": m.user_id,
            "channel": m.channel,
            "endpoint": m.endpoint,
            "status": m.status,
            "send_at": m.send_at,
            "delivered_at": m.delivered_at,
            "read_at": m.read_at,
            "ack_at": m.ack_at,
            "error_text": m.error_text,
            "payload": m.payload,
            "client_meta": m.client_meta,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }


