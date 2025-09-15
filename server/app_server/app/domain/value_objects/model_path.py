"""
모델 경로 값 객체
모델 파일 경로 검증 및 관리
"""

from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class ModelPath:
    """모델 경로 값 객체"""
    value: str
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not self.value or not isinstance(self.value, str):
            raise ValueError("모델 경로는 비어있지 않은 문자열이어야 합니다.")
        
        if len(self.value) > 500:
            raise ValueError("모델 경로는 500자를 초과할 수 없습니다.")
        
        # 기본적인 경로 형식 검증
        if not self._is_valid_path(self.value):
            raise ValueError("유효하지 않은 모델 경로 형식입니다.")
    
    def _is_valid_path(self, path: str) -> bool:
        """경로 형식 검증"""
        # 허용되는 경로 패턴들
        patterns = [
            r'^file:///.*',  # file:// 경로
            r'^s3://.*',     # S3 경로
            r'^gs://.*',     # Google Cloud Storage 경로
            r'^https?://.*', # HTTP/HTTPS 경로
            r'^/.*',         # 절대 경로
            r'^\./.*',       # 상대 경로
        ]
        
        return any(re.match(pattern, path) for pattern in patterns)
    
    def __str__(self) -> str:
        """문자열 표현"""
        return self.value
    
    def __repr__(self) -> str:
        """디버그 표현"""
        return f"ModelPath('{self.value}')"
    
    @classmethod
    def from_string(cls, value: str) -> 'ModelPath':
        """문자열에서 ModelPath 생성"""
        return cls(value)
    
    def is_file_path(self) -> bool:
        """파일 경로인지 확인"""
        return self.value.startswith('file://') or self.value.startswith('/')
    
    def is_s3_path(self) -> bool:
        """S3 경로인지 확인"""
        return self.value.startswith('s3://')
    
    def is_http_path(self) -> bool:
        """HTTP 경로인지 확인"""
        return self.value.startswith('http://') or self.value.startswith('https://')
    
    def get_extension(self) -> Optional[str]:
        """파일 확장자 반환"""
        if '.' in self.value:
            return self.value.split('.')[-1].lower()
        return None
    
    def is_model_file(self) -> bool:
        """모델 파일인지 확인"""
        valid_extensions = ['pt', 'pth', 'h5', 'hdf5', 'onnx', 'pb', 'tflite', 'pkl', 'joblib']
        extension = self.get_extension()
        return extension in valid_extensions if extension else False
