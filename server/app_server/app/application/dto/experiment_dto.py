"""
실험 DTO
요청/응답 데이터 전송 객체
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ExperimentCreateRequest(BaseModel):
    """실험 생성 요청 DTO"""
    name: str = Field(..., min_length=1, max_length=100, description="실험 이름")
    dataset_id: UUID = Field(..., description="데이터셋 ID")
    model_path: str = Field(..., min_length=1, max_length=500, description="모델 경로")
    framework: Optional[str] = Field(None, max_length=50, description="프레임워크")
    code_version: Optional[str] = Field(None, max_length=100, description="코드 버전")
    params: Optional[Dict[str, Any]] = Field(None, description="하이퍼파라미터")
    metrics: Optional[Dict[str, Any]] = Field(None, description="평가 지표")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('실험 이름은 비어있을 수 없습니다.')
        return v.strip()
    
    @field_validator('model_path')
    @classmethod
    def validate_model_path(cls, v):
        if not v or not v.strip():
            raise ValueError('모델 경로는 비어있을 수 없습니다.')
        return v.strip()
    
    @field_validator('framework')
    @classmethod
    def validate_framework(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('프레임워크는 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('code_version')
    @classmethod
    def validate_code_version(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('코드 버전은 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('params')
    @classmethod
    def validate_params(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('하이퍼파라미터는 딕셔너리여야 합니다.')
        return v
    
    @field_validator('metrics')
    @classmethod
    def validate_metrics(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('평가 지표는 딕셔너리여야 합니다.')
        return v

class ExperimentUpdateRequest(BaseModel):
    """실험 업데이트 요청 DTO"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="실험 이름")
    dataset_id: Optional[UUID] = Field(None, description="데이터셋 ID")
    model_path: Optional[str] = Field(None, min_length=1, max_length=500, description="모델 경로")
    framework: Optional[str] = Field(None, max_length=50, description="프레임워크")
    code_version: Optional[str] = Field(None, max_length=100, description="코드 버전")
    params: Optional[Dict[str, Any]] = Field(None, description="하이퍼파라미터")
    metrics: Optional[Dict[str, Any]] = Field(None, description="평가 지표")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('실험 이름은 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('model_path')
    @classmethod
    def validate_model_path(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('모델 경로는 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('framework')
    @classmethod
    def validate_framework(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('프레임워크는 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('code_version')
    @classmethod
    def validate_code_version(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('코드 버전은 비어있을 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('params')
    @classmethod
    def validate_params(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('하이퍼파라미터는 딕셔너리여야 합니다.')
        return v
    
    @field_validator('metrics')
    @classmethod
    def validate_metrics(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('평가 지표는 딕셔너리여야 합니다.')
        return v

class ExperimentResponse(BaseModel):
    """실험 응답 DTO"""
    experiment_id: UUID = Field(..., description="실험 ID")
    name: str = Field(..., description="실험 이름")
    dataset_id: UUID = Field(..., description="데이터셋 ID")
    model_path: str = Field(..., description="모델 경로")
    framework: Optional[str] = Field(None, description="프레임워크")
    code_version: Optional[str] = Field(None, description="코드 버전")
    params: Optional[Dict[str, Any]] = Field(None, description="하이퍼파라미터")
    metrics: Optional[Dict[str, Any]] = Field(None, description="평가 지표")
    created_at: datetime = Field(..., description="생성일시")
    
    class Config:
        from_attributes = True