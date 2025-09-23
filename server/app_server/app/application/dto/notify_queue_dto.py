"""
Notify Queue DTOs
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class NotifyQueueRequest(BaseModel):
    kind: str = Field(..., description="notify.kind_enum")
    severity: Optional[str] = Field("green", description="notify.severity_enum")
    title: Optional[str] = None
    body: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # None → 무기한
    recipients: List[UUID]
    channel: str = Field("websocket", description="notify.channel_enum")
    created_by: Optional[UUID] = None
    created_ip: Optional[str] = None


class NotifyQueueResponse(BaseModel):
    message_id: UUID
    queued_count: int


