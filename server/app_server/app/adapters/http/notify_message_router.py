"""
알림 메시지 RESTful API 라우터 (notify.notify_message)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_app_session
from app.adapters.repositories.notify_message_repository_impl import NotifyMessageRepositoryImpl
from app.application.use_cases.notify_message_use_cases import (
    CreateNotifyMessageUseCase,
    GetNotifyMessageUseCase,
    ListNotifyMessagesUseCase,
    UpdateNotifyMessageUseCase,
    DeleteNotifyMessageUseCase,
)
from app.application.dto.notify_message_dto import (
    NotifyMessageCreateRequest,
    NotifyMessageUpdateRequest,
    NotifyMessageResponse,
)


router = APIRouter(prefix="/api/v1/notify/messages", tags=["notify-messages"])


def get_repository(session: AsyncSession = Depends(get_app_session)) -> NotifyMessageRepositoryImpl:
    return NotifyMessageRepositoryImpl(session)


@router.post("/", response_model=NotifyMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    request: NotifyMessageCreateRequest,
    repo: NotifyMessageRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = CreateNotifyMessageUseCase(repo)
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[NotifyMessageResponse])
async def list_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    kind: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    repo: NotifyMessageRepositoryImpl = Depends(get_repository),
):
    use_case = ListNotifyMessagesUseCase(repo)
    return await use_case.execute(skip=skip, limit=limit, kind=kind, severity=severity)


@router.get("/{message_id}", response_model=NotifyMessageResponse)
async def get_message(
    message_id: UUID,
    repo: NotifyMessageRepositoryImpl = Depends(get_repository),
):
    use_case = GetNotifyMessageUseCase(repo)
    entity = await use_case.execute(message_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return entity


@router.put("/{message_id}", response_model=NotifyMessageResponse)
async def update_message(
    message_id: UUID,
    request: NotifyMessageUpdateRequest,
    repo: NotifyMessageRepositoryImpl = Depends(get_repository),
):
    use_case = UpdateNotifyMessageUseCase(repo)
    entity = await use_case.execute(message_id, request)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return entity


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: UUID,
    repo: NotifyMessageRepositoryImpl = Depends(get_repository),
):
    use_case = DeleteNotifyMessageUseCase(repo)
    ok = await use_case.execute(message_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return None


