"""
프레임 단위 추론 결과 도메인 엔티티
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID


@dataclass
class FramePrediction:
    """프레임 단위 추론 결과 엔티티"""
    session_id: UUID
    experiment_id: UUID
    input_uri: str
    frame_index: int
    probabilities: Dict[str, float]
    label_pred: str
    frame_pred_id: Optional[int] = None
    ts_rel_ms: Optional[int] = None
    confidence: Optional[float] = None
    passed: Optional[bool] = None
    threshold_name: Optional[str] = None
    threshold_snapshot: Optional[Dict] = None
    created_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        return (
            isinstance(self.frame_index, int)
            and self.frame_index >= 0
            and isinstance(self.input_uri, str)
            and bool(self.input_uri)
            and isinstance(self.probabilities, dict)
            and self.label_pred in {"normal", "warning", "fall"}
        )


