"""
데이터셋 리포지토리 포트
데이터셋 도메인과 인프라 레이어 간의 인터페이스
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.dataset import Dataset

class DatasetRepository(ABC):
    """데이터셋 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save(self, dataset: Dataset) -> Dataset:
        """데이터셋 저장"""
        pass
    
    @abstractmethod
    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        """ID로 데이터셋 조회"""
        pass
    
    @abstractmethod
    async def get_by_name_and_version(self, name: str, version: str) -> Optional[Dataset]:
        """이름과 버전으로 데이터셋 조회"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """모든 데이터셋 조회 (페이징)"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """이름으로 데이터셋 조회 (페이징)"""
        pass
    
    @abstractmethod
    async def get_by_tag(self, tag: str, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """태그로 데이터셋 조회 (페이징)"""
        pass
    
    @abstractmethod
    async def update(self, dataset: Dataset) -> Dataset:
        """데이터셋 업데이트"""
        pass
    
    @abstractmethod
    async def delete(self, dataset_id: UUID) -> bool:
        """데이터셋 삭제"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """전체 데이터셋 개수"""
        pass
    
    @abstractmethod
    async def count_by_name(self, name: str) -> int:
        """이름별 데이터셋 개수"""
        pass
    
    @abstractmethod
    async def count_by_tag(self, tag: str) -> int:
        """태그별 데이터셋 개수"""
        pass
