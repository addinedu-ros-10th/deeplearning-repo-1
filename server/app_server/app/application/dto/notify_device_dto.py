"""
Notify Device DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class NotifyDeviceCreateRequest(BaseModel):
    user_id: UUID
    channel: str = Field(..., description="notify.channel_enum")
    endpoint: str
    is_active: Optional[bool] = True
    device_meta: Optional[Dict[str, Any]] = None
    last_seen_at: Optional[datetime] = None


class NotifyDeviceUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    device_meta: Optional[Dict[str, Any]] = None
    last_seen_at: Optional[datetime] = None


class NotifyDeviceResponse(BaseModel):
    device_id: UUID
    user_id: UUID
    channel: str
    endpoint: str
    is_active: bool
    device_meta: Optional[Dict[str, Any]]
    last_seen_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


