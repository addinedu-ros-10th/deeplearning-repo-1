"""
실험 ID 값 객체
UUID 기반 실험 식별자
"""

from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass(frozen=True)
class ExperimentId:
    """실험 ID 값 객체"""
    value: UUID
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not isinstance(self.value, UUID):
            raise ValueError("ExperimentId는 유효한 UUID여야 합니다.")
    
    def __str__(self) -> str:
        """문자열 표현"""
        return str(self.value)
    
    def __repr__(self) -> str:
        """디버그 표현"""
        return f"ExperimentId({self.value})"
    
    @classmethod
    def generate(cls) -> 'ExperimentId':
        """새로운 ExperimentId 생성"""
        return cls(uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> 'ExperimentId':
        """문자열에서 ExperimentId 생성"""
        try:
            uuid_value = UUID(value)
            return cls(uuid_value)
        except ValueError:
            raise ValueError(f"유효하지 않은 UUID 문자열: {value}")
    
    def to_string(self) -> str:
        """문자열로 변환"""
        return str(self.value)

