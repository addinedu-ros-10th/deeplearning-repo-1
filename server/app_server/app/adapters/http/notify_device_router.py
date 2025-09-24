"""
알림 디바이스 RESTful API 라우터 (notify.notify_device)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_app_session
from app.adapters.repositories.notify_device_repository_impl import NotifyDeviceRepositoryImpl
from app.application.use_cases.notify_device_use_cases import (
    CreateNotifyDeviceUseCase,
    GetNotifyDeviceUseCase,
    ListNotifyDevicesUseCase,
    UpdateNotifyDeviceUseCase,
    DeleteNotifyDeviceUseCase,
)
from app.application.dto.notify_device_dto import (
    NotifyDeviceCreateRequest,
    NotifyDeviceUpdateRequest,
    NotifyDeviceResponse,
)


router = APIRouter(prefix="/api/v1/notify/devices", tags=["notify-devices"])


def get_repository(session: AsyncSession = Depends(get_app_session)) -> NotifyDeviceRepositoryImpl:
    return NotifyDeviceRepositoryImpl(session)


@router.post("/", response_model=NotifyDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    request: NotifyDeviceCreateRequest,
    repo: NotifyDeviceRepositoryImpl = Depends(get_repository),
):
    try:
        use_case = CreateNotifyDeviceUseCase(repo)
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[NotifyDeviceResponse])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[UUID] = Query(None),
    channel: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    repo: NotifyDeviceRepositoryImpl = Depends(get_repository),
):
    use_case = ListNotifyDevicesUseCase(repo)
    return await use_case.execute(skip=skip, limit=limit, user_id=user_id, channel=channel, is_active=is_active)


@router.get("/{device_id}", response_model=NotifyDeviceResponse)
async def get_device(
    device_id: UUID,
    repo: NotifyDeviceRepositoryImpl = Depends(get_repository),
):
    use_case = GetNotifyDeviceUseCase(repo)
    entity = await use_case.execute(device_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return entity


@router.put("/{device_id}", response_model=NotifyDeviceResponse)
async def update_device(
    device_id: UUID,
    request: NotifyDeviceUpdateRequest,
    repo: NotifyDeviceRepositoryImpl = Depends(get_repository),
):
    use_case = UpdateNotifyDeviceUseCase(repo)
    entity = await use_case.execute(device_id, request)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return entity


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    repo: NotifyDeviceRepositoryImpl = Depends(get_repository),
):
    use_case = DeleteNotifyDeviceUseCase(repo)
    ok = await use_case.execute(device_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return None


