"""
데이터셋 도메인 엔티티
ML 레지스트리의 데이터셋 도메인 로직
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID, uuid4

@dataclass
class Dataset:
    """데이터셋 도메인 엔티티"""
    name: str
    version: str
    storage_path: str
    dataset_id: Optional[UUID] = None
    description: Optional[str] = None
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None
    source_url: Optional[str] = None
    license: Optional[str] = None
    class_schema: Optional[Dict[str, List[str]]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if self.dataset_id is None:
            self.dataset_id = uuid4()
        if self.class_schema is None:
            self.class_schema = {"labels": ["normal", "warning", "fall"]}
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """태그 추가"""
        if not tag or not isinstance(tag, str):
            raise ValueError("태그는 비어있지 않은 문자열이어야 합니다.")
        
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """태그 제거"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def update_class_schema(self, labels: List[str]) -> None:
        """클래스 스키마 업데이트"""
        if not labels or not isinstance(labels, list):
            raise ValueError("라벨은 비어있지 않은 리스트여야 합니다.")
        
        if not all(isinstance(label, str) for label in labels):
            raise ValueError("모든 라벨은 문자열이어야 합니다.")
        
        self.class_schema = {"labels": labels}
    
    def update_description(self, description: str) -> None:
        """설명 업데이트"""
        if description is not None and len(description) > 1000:
            raise ValueError("설명은 1000자를 초과할 수 없습니다.")
        self.description = description
    
    def update_creator_info(self, name: str, email: str) -> None:
        """생성자 정보 업데이트"""
        if name is not None and len(name) > 100:
            raise ValueError("생성자 이름은 100자를 초과할 수 없습니다.")
        
        if email is not None and len(email) > 255:
            raise ValueError("생성자 이메일은 255자를 초과할 수 없습니다.")
        
        self.creator_name = name
        self.creator_email = email
    
    def update_storage_path(self, storage_path: str) -> None:
        """저장소 경로 업데이트"""
        if not storage_path or not isinstance(storage_path, str):
            raise ValueError("저장소 경로는 비어있지 않은 문자열이어야 합니다.")
        
        self.storage_path = storage_path
    
    def is_valid(self) -> bool:
        """데이터셋 유효성 검사"""
        return (
            bool(self.name) and
            bool(self.version) and
            bool(self.storage_path) and
            isinstance(self.class_schema, dict) and
            "labels" in self.class_schema and
            isinstance(self.class_schema["labels"], list) and
            len(self.class_schema["labels"]) > 0
        )
    
    def get_display_name(self) -> str:
        """표시용 이름 반환"""
        return f"{self.name} v{self.version}"
    
    def get_label_count(self) -> int:
        """라벨 개수 반환"""
        return len(self.class_schema.get("labels", []))
    
    def has_tag(self, tag: str) -> bool:
        """특정 태그 존재 여부 확인"""
        return tag in self.tags