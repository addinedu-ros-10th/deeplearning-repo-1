"""
이벤트 DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class DetectionEventCreateRequest(BaseModel):
    session_id: UUID
    experiment_id: UUID
    input_uri: str = Field(..., min_length=1)
    start_frame: int = Field(..., ge=0)
    end_frame: int = Field(..., ge=0)
    event_type: str = Field(..., min_length=1, max_length=32)
    top_label: str = Field(..., pattern="^(normal|warning|fall)$")
    threshold_snapshot: Dict
    start_ts_ms: Optional[int] = None
    end_ts_ms: Optional[int] = None
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    agg_prob: Optional[Dict] = None
    threshold_name: Optional[str] = None
    trigger_reason: Optional[str] = None


class DetectionEventResponse(BaseModel):
    event_id: UUID
    session_id: UUID
    experiment_id: UUID
    input_uri: str
    start_frame: int
    end_frame: int
    start_ts_ms: Optional[int]
    end_ts_ms: Optional[int]
    event_type: str
    top_label: str
    max_confidence: Optional[float]
    agg_prob: Optional[Dict]
    threshold_name: Optional[str]
    threshold_snapshot: Dict
    trigger_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


