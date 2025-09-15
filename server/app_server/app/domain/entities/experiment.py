"""
실험 도메인 엔티티
ML 레지스트리의 실험 도메인 로직
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

@dataclass
class Experiment:
    """실험 도메인 엔티티"""
    name: str
    dataset_id: UUID
    model_path: str
    experiment_id: Optional[UUID] = None
    framework: Optional[str] = None
    code_version: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if self.experiment_id is None:
            self.experiment_id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def add_param(self, key: str, value: Any) -> None:
        """하이퍼파라미터 추가"""
        if not key or not isinstance(key, str):
            raise ValueError("파라미터 키는 비어있지 않은 문자열이어야 합니다.")
        
        if self.params is None:
            self.params = {}
        
        self.params[key] = value
    
    def remove_param(self, key: str) -> None:
        """하이퍼파라미터 제거"""
        if self.params and key in self.params:
            del self.params[key]
    
    def add_metric(self, key: str, value: Any) -> None:
        """평가 지표 추가"""
        if not key or not isinstance(key, str):
            raise ValueError("지표 키는 비어있지 않은 문자열이어야 합니다.")
        
        if self.metrics is None:
            self.metrics = {}
        
        self.metrics[key] = value
    
    def remove_metric(self, key: str) -> None:
        """평가 지표 제거"""
        if self.metrics and key in self.metrics:
            del self.metrics[key]
    
    def update_framework(self, framework: str) -> None:
        """프레임워크 업데이트"""
        if framework is not None and len(framework) > 50:
            raise ValueError("프레임워크는 50자를 초과할 수 없습니다.")
        self.framework = framework
    
    def update_code_version(self, code_version: str) -> None:
        """코드 버전 업데이트"""
        if code_version is not None and len(code_version) > 100:
            raise ValueError("코드 버전은 100자를 초과할 수 없습니다.")
        self.code_version = code_version
    
    def update_model_path(self, model_path: str) -> None:
        """모델 경로 업데이트"""
        if not model_path or not isinstance(model_path, str):
            raise ValueError("모델 경로는 비어있지 않은 문자열이어야 합니다.")
        
        self.model_path = model_path
    
    def is_valid(self) -> bool:
        """실험 유효성 검사"""
        return (
            bool(self.name) and
            bool(self.dataset_id) and
            bool(self.model_path)
        )
    
    def get_display_name(self) -> str:
        """표시용 이름 반환"""
        return f"{self.name} ({self.framework or 'Unknown'})"
    
    def get_param_count(self) -> int:
        """파라미터 개수 반환"""
        return len(self.params) if self.params else 0
    
    def get_metric_count(self) -> int:
        """지표 개수 반환"""
        return len(self.metrics) if self.metrics else 0