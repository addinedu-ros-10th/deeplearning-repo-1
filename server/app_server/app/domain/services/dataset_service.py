"""
데이터셋 도메인 서비스
데이터셋 관련 비즈니스 로직
"""

from typing import List, Optional
from uuid import UUID
from app.domain.entities.dataset import Dataset
from app.domain.value_objects.dataset_id import DatasetId

class DatasetService:
    """데이터셋 도메인 서비스"""
    
    def validate_dataset_creation(self, dataset: Dataset) -> None:
        """데이터셋 생성 전 유효성 검사 로직 (예: 이름 중복, 필수 필드 등)"""
        if not dataset.name:
            raise ValueError("Dataset name cannot be empty.")
        if not dataset.storage_path:
            raise ValueError("Dataset storage path cannot be empty.")
        # 추가적인 도메인 규칙 검증 (예: class_schema 형식, tags 유효성 등)
        if not isinstance(dataset.class_schema, dict) or "labels" not in dataset.class_schema:
            raise ValueError("Dataset class_schema must be a dictionary with a 'labels' key.")

    def update_dataset_metadata(self, existing_dataset: Dataset, update_data: dict) -> Dataset:
        """데이터셋 메타데이터 업데이트 로직"""
        for key, value in update_data.items():
            if hasattr(existing_dataset, key) and value is not None:
                setattr(existing_dataset, key, value)
        return existing_dataset
    
    @staticmethod
    def validate_dataset_name(name: str) -> bool:
        """데이터셋 이름 유효성 검사"""
        if not name or not isinstance(name, str):
            return False
        
        if len(name) < 1 or len(name) > 255:
            return False
        
        # 특수 문자 제한
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in name for char in invalid_chars):
            return False
        
        return True
    
    @staticmethod
    def validate_version(version: str) -> bool:
        """버전 유효성 검사"""
        if not version or not isinstance(version, str):
            return False
        
        if len(version) < 1 or len(version) > 50:
            return False
        
        # 버전 형식 검증 (예: v1, 1.0.0, 2025-09-13 등)
        import re
        version_pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(version_pattern, version))
    
    @staticmethod
    def validate_class_schema(class_schema: dict) -> bool:
        """클래스 스키마 유효성 검사"""
        if not isinstance(class_schema, dict):
            return False
        
        if "labels" not in class_schema:
            return False
        
        labels = class_schema["labels"]
        if not isinstance(labels, list) or len(labels) == 0:
            return False
        
        # 모든 라벨이 문자열인지 확인
        if not all(isinstance(label, str) and len(label) > 0 for label in labels):
            return False
        
        # 중복 라벨 확인
        if len(labels) != len(set(labels)):
            return False
        
        return True
    
    @staticmethod
    def validate_tags(tags: List[str]) -> bool:
        """태그 유효성 검사"""
        if not isinstance(tags, list):
            return False
        
        for tag in tags:
            if not isinstance(tag, str) or len(tag) == 0 or len(tag) > 50:
                return False
        
        # 중복 태그 확인
        if len(tags) != len(set(tags)):
            return False
        
        return True
    
    @staticmethod
    def create_dataset(
        name: str,
        version: str,
        storage_path: str,
        description: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_email: Optional[str] = None,
        source_url: Optional[str] = None,
        license: Optional[str] = None,
        class_schema: Optional[dict] = None,
        tags: Optional[List[str]] = None
    ) -> Dataset:
        """데이터셋 생성"""
        # 유효성 검사
        if not DatasetService.validate_dataset_name(name):
            raise ValueError("유효하지 않은 데이터셋 이름입니다.")
        
        if not DatasetService.validate_version(version):
            raise ValueError("유효하지 않은 버전입니다.")
        
        if not storage_path or len(storage_path) > 500:
            raise ValueError("유효하지 않은 저장소 경로입니다.")
        
        if class_schema and not DatasetService.validate_class_schema(class_schema):
            raise ValueError("유효하지 않은 클래스 스키마입니다.")
        
        if tags and not DatasetService.validate_tags(tags):
            raise ValueError("유효하지 않은 태그입니다.")
        
        # 기본값 설정
        if class_schema is None:
            class_schema = {"labels": ["normal", "warning", "fall"]}
        
        if tags is None:
            tags = []
        
        # 데이터셋 생성
        dataset = Dataset(
            dataset_id=DatasetId.generate().value,
            name=name,
            version=version,
            storage_path=storage_path,
            description=description,
            creator_name=creator_name,
            creator_email=creator_email,
            source_url=source_url,
            license=license,
            class_schema=class_schema,
            tags=tags
        )
        
        return dataset
    
    @staticmethod
    def update_dataset(
        dataset: Dataset,
        name: Optional[str] = None,
        storage_path: Optional[str] = None,
        description: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_email: Optional[str] = None,
        source_url: Optional[str] = None,
        license: Optional[str] = None,
        class_schema: Optional[dict] = None,
        tags: Optional[List[str]] = None
    ) -> Dataset:
        """데이터셋 업데이트"""
        if name is not None:
            if not DatasetService.validate_dataset_name(name):
                raise ValueError("유효하지 않은 데이터셋 이름입니다.")
            dataset.name = name
        
        if storage_path is not None:
            if not storage_path or len(storage_path) > 500:
                raise ValueError("유효하지 않은 저장소 경로입니다.")
            dataset.storage_path = storage_path
        
        if description is not None:
            dataset.update_description(description)
        
        if creator_name is not None or creator_email is not None:
            dataset.update_creator_info(creator_name, creator_email)
        
        if source_url is not None:
            if len(source_url) > 500:
                raise ValueError("소스 URL은 500자를 초과할 수 없습니다.")
            dataset.source_url = source_url
        
        if license is not None:
            if len(license) > 500:
                raise ValueError("라이선스는 500자를 초과할 수 없습니다.")
            dataset.license = license
        
        if class_schema is not None:
            if not DatasetService.validate_class_schema(class_schema):
                raise ValueError("유효하지 않은 클래스 스키마입니다.")
            dataset.update_class_schema(class_schema["labels"])
        
        if tags is not None:
            if not DatasetService.validate_tags(tags):
                raise ValueError("유효하지 않은 태그입니다.")
            dataset.tags = tags
        
        return dataset
