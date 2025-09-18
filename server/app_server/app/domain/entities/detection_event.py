"""
임계치 충족 이벤트 도메인 엔티티
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID, uuid4


@dataclass
class DetectionEvent:
    """임계치 충족 이벤트 엔티티"""
    session_id: UUID
    experiment_id: UUID
    input_uri: str
    start_frame: int
    end_frame: int
    event_type: str
    top_label: str
    threshold_snapshot: Dict
    event_id: Optional[UUID] = None
    start_ts_ms: Optional[int] = None
    end_ts_ms: Optional[int] = None
    max_confidence: Optional[float] = None
    agg_prob: Optional[Dict] = None
    threshold_name: Optional[str] = None
    trigger_reason: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = uuid4()

    def is_valid(self) -> bool:
        return (
            isinstance(self.start_frame, int)
            and isinstance(self.end_frame, int)
            and self.end_frame >= self.start_frame
            and self.top_label in {"normal", "warning", "fall"}
            and isinstance(self.threshold_snapshot, dict)
            and isinstance(self.input_uri, str)
            and bool(self.input_uri)
        )


