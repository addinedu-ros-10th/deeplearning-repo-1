"""
실험 도메인 서비스
실험 관련 비즈니스 로직
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from app.domain.entities.experiment import Experiment
from app.domain.value_objects.experiment_id import ExperimentId
from app.domain.value_objects.model_path import ModelPath

class ExperimentService:
    """실험 도메인 서비스"""
    
    def validate_experiment_creation(self, experiment: Experiment) -> None:
        """실험 생성 전 유효성 검사 로직"""
        if not experiment.name:
            raise ValueError("Experiment name cannot be empty.")
        if not experiment.dataset_id:
            raise ValueError("Dataset ID cannot be empty.")
        if not experiment.model_path:
            raise ValueError("Model path cannot be empty.")
        # 추가적인 도메인 규칙 검증
        if not isinstance(experiment.params, dict):
            raise ValueError("Experiment params must be a dictionary.")
        if not isinstance(experiment.metrics, dict):
            raise ValueError("Experiment metrics must be a dictionary.")

    def update_experiment_details(self, existing_experiment: Experiment, update_data: dict) -> Experiment:
        """실험 세부사항 업데이트"""
        for key, value in update_data.items():
            if hasattr(existing_experiment, key) and value is not None:
                setattr(existing_experiment, key, value)
        return existing_experiment
    
    @staticmethod
    def validate_experiment_name(name: str) -> bool:
        """실험 이름 유효성 검사"""
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
    def validate_framework(framework: str) -> bool:
        """프레임워크 유효성 검사"""
        if not framework or not isinstance(framework, str):
            return False
        
        valid_frameworks = [
            'PyTorch', 'TensorFlow', 'Keras', 'ONNX', 'Scikit-learn',
            'XGBoost', 'LightGBM', 'CatBoost', 'Hugging Face', 'Transformers'
        ]
        
        return framework in valid_frameworks
    
    @staticmethod
    def validate_code_version(code_version: str) -> bool:
        """코드 버전 유효성 검사"""
        if not code_version or not isinstance(code_version, str):
            return False
        
        if len(code_version) < 1 or len(code_version) > 50:
            return False
        
        # Git commit hash 형식 또는 버전 형식 검증
        import re
        version_pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(version_pattern, code_version))
    
    @staticmethod
    def validate_params(params: Dict[str, Any]) -> bool:
        """파라미터 유효성 검사"""
        if not isinstance(params, dict):
            return False
        
        # 파라미터 키 검증
        for key in params.keys():
            if not isinstance(key, str) or len(key) == 0 or len(key) > 100:
                return False
        
        return True
    
    @staticmethod
    def validate_metrics(metrics: Dict[str, Any]) -> bool:
        """메트릭 유효성 검사"""
        if not isinstance(metrics, dict):
            return False
        
        # 메트릭 키 검증
        for key in metrics.keys():
            if not isinstance(key, str) or len(key) == 0 or len(key) > 100:
                return False
        
        # 메트릭 값이 숫자 또는 문자열인지 확인
        for value in metrics.values():
            if not isinstance(value, (int, float, str)):
                return False
        
        return True
    
    @staticmethod
    def create_experiment(
        name: str,
        dataset_id: UUID,
        model_path: str,
        framework: Optional[str] = None,
        code_version: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Experiment:
        """실험 생성"""
        # 유효성 검사
        if not ExperimentService.validate_experiment_name(name):
            raise ValueError("유효하지 않은 실험 이름입니다.")
        
        if not dataset_id:
            raise ValueError("데이터셋 ID는 필수입니다.")
        
        # 모델 경로 검증
        try:
            ModelPath.from_string(model_path)
        except ValueError as e:
            raise ValueError(f"유효하지 않은 모델 경로: {e}")
        
        if framework and not ExperimentService.validate_framework(framework):
            raise ValueError("유효하지 않은 프레임워크입니다.")
        
        if code_version and not ExperimentService.validate_code_version(code_version):
            raise ValueError("유효하지 않은 코드 버전입니다.")
        
        if params and not ExperimentService.validate_params(params):
            raise ValueError("유효하지 않은 파라미터입니다.")
        
        if metrics and not ExperimentService.validate_metrics(metrics):
            raise ValueError("유효하지 않은 메트릭입니다.")
        
        # 기본값 설정
        if params is None:
            params = {}
        if metrics is None:
            metrics = {}
        
        # 실험 생성
        experiment = Experiment(
            experiment_id=ExperimentId.generate().value,
            name=name,
            dataset_id=dataset_id,
            model_path=model_path,
            framework=framework,
            code_version=code_version,
            params=params,
            metrics=metrics
        )
        
        return experiment
    
    @staticmethod
    def update_experiment(
        experiment: Experiment,
        name: Optional[str] = None,
        model_path: Optional[str] = None,
        framework: Optional[str] = None,
        code_version: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Experiment:
        """실험 업데이트"""
        if name is not None:
            if not ExperimentService.validate_experiment_name(name):
                raise ValueError("유효하지 않은 실험 이름입니다.")
            experiment.name = name
        
        if model_path is not None:
            try:
                ModelPath.from_string(model_path)
                experiment.update_model_path(model_path)
            except ValueError as e:
                raise ValueError(f"유효하지 않은 모델 경로: {e}")
        
        if framework is not None:
            if not ExperimentService.validate_framework(framework):
                raise ValueError("유효하지 않은 프레임워크입니다.")
            experiment.update_framework(framework)
        
        if code_version is not None:
            if not ExperimentService.validate_code_version(code_version):
                raise ValueError("유효하지 않은 코드 버전입니다.")
            experiment.update_code_version(code_version)
        
        if params is not None:
            if not ExperimentService.validate_params(params):
                raise ValueError("유효하지 않은 파라미터입니다.")
            experiment.update_params(params)
        
        if metrics is not None:
            if not ExperimentService.validate_metrics(metrics):
                raise ValueError("유효하지 않은 메트릭입니다.")
            experiment.update_metrics(metrics)
        
        return experiment
    
    @staticmethod
    def add_param(experiment: Experiment, key: str, value: Any) -> Experiment:
        """파라미터 추가"""
        if not ExperimentService.validate_params({key: value}):
            raise ValueError("유효하지 않은 파라미터입니다.")
        
        experiment.add_param(key, value)
        return experiment
    
    @staticmethod
    def add_metric(experiment: Experiment, key: str, value: Any) -> Experiment:
        """메트릭 추가"""
        if not ExperimentService.validate_metrics({key: value}):
            raise ValueError("유효하지 않은 메트릭입니다.")
        
        experiment.add_metric(key, value)
        return experiment
