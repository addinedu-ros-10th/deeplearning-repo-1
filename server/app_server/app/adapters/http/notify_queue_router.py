"""
알림 큐잉 엔드포인트 (/api/v1/notify/queue)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_app_session
from app.adapters.repositories.notify_message_repository_impl import NotifyMessageRepositoryImpl
from app.adapters.repositories.notify_delivery_repository_impl import NotifyDeliveryRepositoryImpl
from app.adapters.repositories.notify_device_repository_impl import NotifyDeviceRepositoryImpl
from app.application.use_cases.notify_queue_use_cases import CreateMessageAndQueueUseCase
from app.application.dto.notify_queue_dto import NotifyQueueRequest, NotifyQueueResponse


router = APIRouter(prefix="/api/v1/notify", tags=["notify-queue"])


def get_repos(session: AsyncSession = Depends(get_app_session)):
    return (
        NotifyMessageRepositoryImpl(session),
        NotifyDeliveryRepositoryImpl(session),
        NotifyDeviceRepositoryImpl(session),
    )


@router.post("/queue", response_model=NotifyQueueResponse, status_code=status.HTTP_201_CREATED)
async def queue_notify(
    request: NotifyQueueRequest,
    deps = Depends(get_repos),
):
    try:
        msg_repo, deliv_repo, device_repo = deps
        use_case = CreateMessageAndQueueUseCase(msg_repo, deliv_repo, device_repo)
        result = await use_case.execute(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


