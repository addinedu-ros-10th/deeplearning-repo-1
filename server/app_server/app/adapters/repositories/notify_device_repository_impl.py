from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.infrastructure.db.models.notify_models import NotifyDevice as NotifyDeviceModel
from app.domain.ports.notify_device_repository import NotifyDeviceRepository


class NotifyDeviceRepositoryImpl(NotifyDeviceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: dict) -> dict:
        stmt = insert(NotifyDeviceModel).values(**payload).returning(NotifyDeviceModel)
        res = await self.session.execute(stmt)
        await self.session.commit()
        m = res.scalar_one()
        return self._to_dict(m)

    async def get_by_id(self, device_id: UUID) -> Optional[dict]:
        res = await self.session.execute(select(NotifyDeviceModel).where(NotifyDeviceModel.device_id == device_id))
        m = res.scalar_one_or_none()
        return self._to_dict(m) if m else None

    async def list(self, *, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None, channel: Optional[str] = None, is_active: Optional[bool] = None) -> List[dict]:
        stmt = select(NotifyDeviceModel).offset(skip).limit(limit).order_by(NotifyDeviceModel.created_at.desc())
        if user_id:
            stmt = stmt.where(NotifyDeviceModel.user_id == user_id)
        if channel:
            stmt = stmt.where(NotifyDeviceModel.channel == channel)
        if is_active is not None:
            stmt = stmt.where(NotifyDeviceModel.is_active == is_active)
        res = await self.session.execute(stmt)
        return [self._to_dict(m) for m in res.scalars().all()]

    async def update(self, device_id: UUID, payload: dict) -> Optional[dict]:
        await self.session.execute(update(NotifyDeviceModel).where(NotifyDeviceModel.device_id == device_id).values(**payload))
        await self.session.commit()
        res = await self.session.execute(select(NotifyDeviceModel).where(NotifyDeviceModel.device_id == device_id))
        m = res.scalar_one_or_none()
        return self._to_dict(m) if m else None

    async def delete(self, device_id: UUID) -> bool:
        res = await self.session.execute(delete(NotifyDeviceModel).where(NotifyDeviceModel.device_id == device_id))
        await self.session.commit()
        return res.rowcount > 0

    @staticmethod
    def _to_dict(m: NotifyDeviceModel) -> dict:
        return {
            "device_id": m.device_id,
            "user_id": m.user_id,
            "channel": m.channel,
            "endpoint": m.endpoint,
            "is_active": m.is_active,
            "device_meta": m.device_meta,
            "last_seen_at": m.last_seen_at,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }


