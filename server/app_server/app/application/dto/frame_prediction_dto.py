"""
프레임 추론 DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime


class FramePredictionCreateRequest(BaseModel):
    session_id: UUID
    experiment_id: UUID
    input_uri: str = Field(..., min_length=1)
    frame_index: int = Field(..., ge=0)
    probabilities: Dict[str, float]
    label_pred: str = Field(..., pattern="^(normal|warning|fall)$")
    ts_rel_ms: Optional[int] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    passed: Optional[bool] = None
    threshold_name: Optional[str] = None
    threshold_snapshot: Optional[Dict] = None


class FramePredictionBatchCreateRequest(BaseModel):
    items: List[FramePredictionCreateRequest] = Field(..., min_items=1, max_items=10000)


class FramePredictionResponse(BaseModel):
    frame_pred_id: int
    session_id: UUID
    experiment_id: UUID
    input_uri: str
    frame_index: int
    ts_rel_ms: Optional[int]
    label_pred: str
    confidence: Optional[float]
    probabilities: Dict[str, float]
    passed: Optional[bool]
    threshold_name: Optional[str]
    threshold_snapshot: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True


