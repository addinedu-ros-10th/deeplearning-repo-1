from uuid import UUID
from typing import Sequence
from app.domain.ports.notify_message_repository import NotifyMessageRepository
from app.domain.ports.notify_delivery_repository import NotifyDeliveryRepository
from app.domain.ports.notify_device_repository import NotifyDeviceRepository
from app.application.dto.notify_queue_dto import NotifyQueueRequest


class CreateMessageAndQueueUseCase:
    def __init__(self, msg_repo: NotifyMessageRepository, deliv_repo: NotifyDeliveryRepository, device_repo: NotifyDeviceRepository):
        self.msg_repo = msg_repo
        self.deliv_repo = deliv_repo
        self.device_repo = device_repo

    async def execute(self, req: NotifyQueueRequest) -> dict:
        # 1) 메시지 생성
        message = await self.msg_repo.create(req.model_dump(exclude={"recipients", "channel"}, exclude_unset=True))

        # 2) recipients × channel 큐잉 (endpoint는 이후 렌더링 단계에서 사용)
        queued = 0
        for user_id in req.recipients:
            payload = {
                "title": req.title, 
                "body": req.body, 
                "data": req.data,
                "kind": req.kind,
                "severity": req.severity,
                "message_id": str(message.message_id),
                "created_at": message.created_at.isoformat() if message.created_at else None
            }
            await self.deliv_repo.create({
                "message_id": message.message_id,
                "user_id": user_id,
                "channel": req.channel,
                "status": "queued",
                "payload": payload,
            })
            queued += 1

        return {"message_id": message.message_id, "queued_count": queued}


