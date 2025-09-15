"""
실험 리포지토리 포트
실험 도메인과 인프라 레이어 간의 인터페이스
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.experiment import Experiment

class ExperimentRepository(ABC):
    """실험 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save(self, experiment: Experiment) -> Experiment:
        """실험 저장"""
        pass
    
    @abstractmethod
    async def get_by_id(self, experiment_id: UUID) -> Optional[Experiment]:
        """ID로 실험 조회"""
        pass
    
    @abstractmethod
    async def get_by_name_and_dataset(self, name: str, dataset_id: UUID) -> Optional[Experiment]:
        """이름과 데이터셋 ID로 실험 조회"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Experiment]:
        """모든 실험 조회 (페이징)"""
        pass
    
    @abstractmethod
    async def get_by_dataset_id(self, dataset_id: UUID, skip: int = 0, limit: int = 100) -> List[Experiment]:
        """데이터셋 ID로 실험 조회 (페이징)"""
        pass
    
    @abstractmethod
    async def get_by_framework(self, framework: str, skip: int = 0, limit: int = 100) -> List[Experiment]:
        """프레임워크로 실험 조회 (페이징)"""
        pass
    
    @abstractmethod
    async def update(self, experiment: Experiment) -> Experiment:
        """실험 업데이트"""
        pass
    
    @abstractmethod
    async def delete(self, experiment_id: UUID) -> bool:
        """실험 삭제"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """전체 실험 개수"""
        pass
    
    @abstractmethod
    async def count_by_dataset_id(self, dataset_id: UUID) -> int:
        """데이터셋별 실험 개수"""
        pass
    
    @abstractmethod
    async def count_by_framework(self, framework: str) -> int:
        """프레임워크별 실험 개수"""
        pass
