"""
Notify Message DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class NotifyMessageCreateRequest(BaseModel):
    kind: str = Field(..., description="notify.kind_enum")
    severity: Optional[str] = Field("green", description="notify.severity_enum")
    title: Optional[str] = None
    body: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_ip: Optional[str] = None


class NotifyMessageUpdateRequest(BaseModel):
    kind: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class NotifyMessageResponse(BaseModel):
    message_id: UUID
    kind: str
    severity: str
    title: Optional[str]
    body: Optional[str]
    data: Optional[Dict[str, Any]]
    scheduled_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_by: Optional[UUID]
    created_ip: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


