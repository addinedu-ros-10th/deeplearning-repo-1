"""
데이터셋 DTO
요청/응답 데이터 전송 객체
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class DatasetCreateRequest(BaseModel):
    """데이터셋 생성 요청 DTO"""
    name: str = Field(..., min_length=1, max_length=100, description="데이터셋 이름")
    version: str = Field(..., min_length=1, max_length=50, description="데이터셋 버전")
    storage_path: str = Field(..., min_length=1, max_length=500, description="저장소 경로")
    description: Optional[str] = Field(None, max_length=1000, description="설명")
    creator_name: Optional[str] = Field(None, max_length=100, description="생성자 이름")
    creator_email: Optional[str] = Field(None, max_length=100, description="생성자 이메일")
    source_url: Optional[str] = Field(None, max_length=500, description="소스 URL")
    license: Optional[str] = Field(None, max_length=500, description="라이선스")
    class_schema: Dict[str, List[str]] = Field(
        default={"labels": ["normal", "warning", "fall"]}, 
        description="클래스 스키마"
    )
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('데이터셋 이름은 비어있을 수 없습니다.')
        return v.strip()
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        if not v or not v.strip():
            raise ValueError('버전은 비어있을 수 없습니다.')
        return v.strip()
    
    @field_validator('storage_path')
    @classmethod
    def validate_storage_path(cls, v):
        if not v or not v.strip():
            raise ValueError('저장소 경로는 비어있을 수 없습니다.')
        return v.strip()
    
    @field_validator('class_schema')
    @classmethod
    def validate_class_schema(cls, v):
        if not isinstance(v, dict) or "labels" not in v:
            raise ValueError('클래스 스키마는 labels 키를 포함해야 합니다.')
        
        labels = v["labels"]
        if not isinstance(labels, list) or len(labels) == 0:
            raise ValueError('라벨은 비어있지 않은 리스트여야 합니다.')
        
        if not all(isinstance(label, str) and label.strip() for label in labels):
            raise ValueError('모든 라벨은 비어있지 않은 문자열이어야 합니다.')
        
        if len(labels) != len(set(labels)):
            raise ValueError('중복된 라벨이 있습니다.')
        
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if not isinstance(v, list):
            raise ValueError('태그는 리스트여야 합니다.')
        
        for tag in v:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError('모든 태그는 비어있지 않은 문자열이어야 합니다.')
        
        return [tag.strip() for tag in v]

class DatasetUpdateRequest(BaseModel):
    """데이터셋 업데이트 요청 DTO"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="데이터셋 이름")
    version: Optional[str] = Field(None, min_length=1, max_length=50, description="데이터셋 버전")
    storage_path: Optional[str] = Field(None, min_length=1, max_length=500, description="저장소 경로")
    description: Optional[str] = Field(None, max_length=1000, description="설명")
    creator_name: Optional[str] = Field(None, max_length=100, description="생성자 이름")
    creator_email: Optional[str] = Field(None, max_length=100, description="생성자 이메일")
    source_url: Optional[str] = Field(None, max_length=500, description="소스 URL")
    license: Optional[str] = Field(None, max_length=500, description="라이선스")
    class_schema: Optional[Dict[str, List[str]]] = Field(None, description="클래스 스키마")
    tags: Optional[List[str]] = Field(None, description="태그 목록")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('데이터셋 이름은 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('버전은 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('storage_path')
    @classmethod
    def validate_storage_path(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('저장소 경로는 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('class_schema')
    @classmethod
    def validate_class_schema(cls, v):
        if v is not None:
            if not isinstance(v, dict) or "labels" not in v:
                raise ValueError('클래스 스키마는 labels 키를 포함해야 합니다.')
            
            labels = v["labels"]
            if not isinstance(labels, list) or len(labels) == 0:
                raise ValueError('라벨은 비어있지 않은 리스트여야 합니다.')
            
            if not all(isinstance(label, str) and label.strip() for label in labels):
                raise ValueError('모든 라벨은 비어있지 않은 문자열이어야 합니다.')
            
            if len(labels) != len(set(labels)):
                raise ValueError('중복된 라벨이 있습니다.')
        
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('태그는 리스트여야 합니다.')
            
            for tag in v:
                if not isinstance(tag, str) or not tag.strip():
                    raise ValueError('모든 태그는 비어있지 않은 문자열이어야 합니다.')
            
            return [tag.strip() for tag in v]
        return v

class DatasetResponse(BaseModel):
    """데이터셋 응답 DTO"""
    dataset_id: UUID = Field(..., description="데이터셋 ID")
    name: str = Field(..., description="데이터셋 이름")
    version: str = Field(..., description="데이터셋 버전")
    storage_path: str = Field(..., description="저장소 경로")
    description: Optional[str] = Field(None, description="설명")
    creator_name: Optional[str] = Field(None, description="생성자 이름")
    creator_email: Optional[str] = Field(None, description="생성자 이메일")
    source_url: Optional[str] = Field(None, description="소스 URL")
    license: Optional[str] = Field(None, description="라이선스")
    class_schema: Dict[str, List[str]] = Field(..., description="클래스 스키마")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    created_at: datetime = Field(..., description="생성일시")
    
    class Config:
        from_attributes = True