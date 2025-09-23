"""
Notify Delivery DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class NotifyDeliveryCreateRequest(BaseModel):
    message_id: UUID
    user_id: UUID
    channel: str = Field(..., description="notify.channel_enum")
    endpoint: Optional[str] = None
    status: Optional[str] = Field("queued", description="notify.delivery_status_enum")
    send_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    ack_at: Optional[datetime] = None
    error_text: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    client_meta: Optional[Dict[str, Any]] = None


class NotifyDeliveryUpdateRequest(BaseModel):
    endpoint: Optional[str] = None
    status: Optional[str] = None
    send_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    ack_at: Optional[datetime] = None
    error_text: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    client_meta: Optional[Dict[str, Any]] = None


class NotifyDeliveryResponse(BaseModel):
    delivery_id: int
    message_id: UUID
    user_id: UUID
    channel: str
    endpoint: Optional[str]
    status: str
    send_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    ack_at: Optional[datetime]
    error_text: Optional[str]
    payload: Optional[Dict[str, Any]]
    client_meta: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


