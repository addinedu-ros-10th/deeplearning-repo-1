"""
알림 딜리버리 RESTful API 라우터 (notify.notify_delivery)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_app_session
from app.adapters.repositories.notify_delivery_repository_impl import NotifyDeliveryRepositoryImpl
from app.application.use_cases.notify_delivery_use_cases import (
    CreateNotifyDeliveryUseCase,
    GetNotifyDeliveryUseCase,
    ListNotifyDeliveriesUseCase,
    UpdateNotifyDeliveryUseCase,
    DeleteNotifyDeliveryUseCase,
)
from app.application.dto.notify_delivery_dto import (
    NotifyDeliveryCreateRequest,
    NotifyDeliveryUpdateRequest,
    NotifyDeliveryResponse,
)
from fastapi import Path


router = APIRouter(prefix="/api/v1/notify/deliveries", tags=["notify-deliveries"])


def get_repository(session: AsyncSession = Depends(get_app_session)) -> NotifyDeliveryRepositoryImpl:
    return NotifyDeliveryRepositoryImpl(session)


@router.post("/", response_model=NotifyDeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    request: NotifyDeliveryCreateRequest,
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = CreateNotifyDeliveryUseCase(repo)
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[NotifyDeliveryResponse])
async def list_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[UUID] = Query(None),
    status_q: Optional[str] = Query(None, alias="status"),
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    use_case = ListNotifyDeliveriesUseCase(repo)
    return await use_case.execute(skip=skip, limit=limit, user_id=user_id, status=status_q)


@router.get("/{delivery_id}", response_model=NotifyDeliveryResponse)
async def get_delivery(
    delivery_id: int,
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    use_case = GetNotifyDeliveryUseCase(repo)
    entity = await use_case.execute(delivery_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return entity


@router.put("/{delivery_id}", response_model=NotifyDeliveryResponse)
async def update_delivery(
    delivery_id: int,
    request: NotifyDeliveryUpdateRequest,
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    use_case = UpdateNotifyDeliveryUseCase(repo)
    entity = await use_case.execute(delivery_id, request)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return entity


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery(
    delivery_id: int,
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    use_case = DeleteNotifyDeliveryUseCase(repo)
    ok = await use_case.execute(delivery_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return None


@router.post("/{delivery_id}/read", status_code=status.HTTP_200_OK)
async def mark_read(
    delivery_id: int = Path(..., ge=1),
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    # lightweight direct update using repository update
    entity = await repo.update(delivery_id, {"status": "read"})
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return entity


@router.post("/{delivery_id}/ack", status_code=status.HTTP_200_OK)
async def mark_ack(
    delivery_id: int = Path(..., ge=1),
    repo: NotifyDeliveryRepositoryImpl = Depends(get_repository),
):
    entity = await repo.update(delivery_id, {"status": "ack"})
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return entity


