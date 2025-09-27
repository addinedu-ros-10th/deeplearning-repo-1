import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.infrastructure.db.session import db_manager
from app.infrastructure.db.models.notify_models import NotifyDelivery as NotifyDeliveryModel, NotifyMessage as NotifyMessageModel
from app.services.ws_notify import ws_notifier


logger = logging.getLogger(__name__)


async def _fetch_next_queued(session: AsyncSession, limit: int = 100):
    stmt = (
        select(NotifyDeliveryModel)
        .join(NotifyMessageModel, NotifyMessageModel.message_id == NotifyDeliveryModel.message_id)
        .where(NotifyDeliveryModel.status == 'queued')
        .where((NotifyMessageModel.expires_at.is_(None)) | (NotifyMessageModel.expires_at >= func.now()))
        .order_by(NotifyDeliveryModel.created_at.asc())
        .limit(limit)
    )
    res = await session.execute(stmt)
    return res.scalars().all()


async def dispatcher_loop(poll_interval: float = 0.5, batch: int = 100):
    if os.getenv('NOTIFY_ENABLE', 'true').lower() != 'true':
        logger.info("[notify] NOTIFY_ENABLE is false; dispatcher not started")
        return
    if os.getenv('NOTIFY_DISPATCH_ENABLE', 'false').lower() != 'true':
        logger.info("[notify] NOTIFY_DISPATCH_ENABLE is false; dispatcher not started")
        return

    logger.info("[notify] dispatcher started (ws=%s)", os.getenv('NOTIFY_WS_ENABLE', 'false'))
    while True:
        try:
            async with db_manager.get_app_session() as session:  # type: ignore
                deliveries = await _fetch_next_queued(session, limit=batch)
                for d in deliveries:
                    # sent
                    await session.execute(
                        NotifyDeliveryModel.__table__.update().where(NotifyDeliveryModel.delivery_id == d.delivery_id).values(status='sent', send_at=None)
                    )
                    # notify via WS (optional)
                    if os.getenv('NOTIFY_WS_ENABLE', 'false').lower() == 'true':
                        try:
                            await ws_notifier.notify({"user_id": d.user_id, "payload": d.payload or {}})
                        except Exception as e:
                            logger.warning("[notify] ws notify failed: %s", e)
                    # delivered
                    await session.execute(
                        NotifyDeliveryModel.__table__.update().where(NotifyDeliveryModel.delivery_id == d.delivery_id).values(status='delivered')
                    )
                await session.commit()
        except Exception as e:
            logger.error("[notify] dispatcher error: %s", e)
        await asyncio.sleep(poll_interval)


