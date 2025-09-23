from dataclasses import dataclass
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


@dataclass
class NotifyMessage:
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


