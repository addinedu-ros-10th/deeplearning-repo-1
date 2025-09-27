#!/usr/bin/env python3
"""
API 데이터 변환 유틸리티

YOLO 모델에서 생성된 데이터를 API 스키마에 맞게 변환합니다.
"""

import json
from typing import Dict, List, Any, Union


def convert_label_to_lowercase(label: str) -> str:
    """라벨을 소문자로 변환"""
    label_mapping = {
        "Fall": "fall",
        "Warning": "warning", 
        "Normal": "normal",
        "FALL": "fall",
        "WARNING": "warning",
        "NORMAL": "normal"
    }
    return label_mapping.get(label, label.lower())


def convert_tensor_to_float(value: Any) -> float:
    """PyTorch Tensor나 numpy array를 float로 변환"""
    if hasattr(value, 'item'):  # PyTorch Tensor
        return float(value.item())
    elif hasattr(value, 'tolist'):  # numpy array
        return float(value.tolist())
    elif isinstance(value, (int, float)):
        return float(value)
    else:
        return float(value)


def convert_probabilities(probabilities: Dict[str, Any]) -> Dict[str, float]:
    """확률 딕셔너리를 float 값으로 변환"""
    converted = {}
    for key, value in probabilities.items():
        converted[key] = convert_tensor_to_float(value)
    return converted


def convert_frame_prediction_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """원시 프레임 예측 데이터를 API 스키마에 맞게 변환"""
    
    # 필수 필드 변환
    converted = {
        "session_id": str(raw_data.get("session_id", "")),
        "experiment_id": str(raw_data.get("experiment_id", "")),
        "input_uri": str(raw_data.get("input_url", raw_data.get("input_uri", ""))),  # input_url → input_uri
        "frame_index": int(raw_data.get("frame_index", 0)),
        "probabilities": convert_probabilities(raw_data.get("probabilities", {})),
        "label_pred": convert_label_to_lowercase(raw_data.get("label_pred", "normal")),
        "confidence": convert_tensor_to_float(raw_data.get("confidence", 0.0)),
        "passed": bool(raw_data.get("passed", False)),
        "threshold_name": str(raw_data.get("threshold_name", "default")),
        "threshold_snapshot": raw_data.get("threshold_snapshot", {})
    }
    
    # 선택적 필드 (있는 경우만 추가)
    if "ts_rel_ms" in raw_data:
        ts_value = raw_data["ts_rel_ms"]
        # 부동소수점을 정수로 변환
        converted["ts_rel_ms"] = int(convert_tensor_to_float(ts_value))
    
    return converted


def convert_batch_frame_predictions(raw_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """배치 프레임 예측 데이터를 API 스키마에 맞게 변환"""
    
    converted_items = []
    for item in raw_items:
        converted_item = convert_frame_prediction_data(item)
        converted_items.append(converted_item)
    
    return {"items": converted_items}


def validate_api_data(data: Dict[str, Any]) -> List[str]:
    """API 데이터 유효성 검사"""
    errors = []
    
    # 필수 필드 검사
    required_fields = ["session_id", "experiment_id", "input_uri", "frame_index", "probabilities", "label_pred"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # 라벨 형식 검사
    if "label_pred" in data:
        valid_labels = ["normal", "warning", "fall"]
        if data["label_pred"] not in valid_labels:
            errors.append(f"Invalid label_pred: {data['label_pred']}. Must be one of {valid_labels}")
    
    # ts_rel_ms 정수 검사
    if "ts_rel_ms" in data and not isinstance(data["ts_rel_ms"], int):
        errors.append(f"ts_rel_ms must be integer, got {type(data['ts_rel_ms'])}")
    
    return errors


def convert_yolo_output_to_api_format(
    session_id: str,
    experiment_id: str,
    input_uri: str,
    frame_index: int,
    probabilities: Dict[str, Any],
    label_pred: str,
    confidence: Any,
    ts_rel_ms: Any = None,
    passed: bool = False,
    threshold_name: str = "default",
    threshold_snapshot: Dict[str, Any] = None
) -> Dict[str, Any]:
    """YOLO 모델 출력을 API 형식으로 변환하는 편의 함수"""
    
    raw_data = {
        "session_id": session_id,
        "experiment_id": experiment_id,
        "input_url": input_uri,  # input_uri로 변환됨
        "frame_index": frame_index,
        "probabilities": probabilities,
        "label_pred": label_pred,
        "confidence": confidence,
        "ts_rel_ms": ts_rel_ms,
        "passed": passed,
        "threshold_name": threshold_name,
        "threshold_snapshot": threshold_snapshot or {}
    }
    
    return convert_frame_prediction_data(raw_data)


# 사용 예제
if __name__ == "__main__":
    # 예제 데이터
    sample_data = {
        "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "experiment_id": "12bd0c67-a10c-4e01-adec-871010e49031",
        "input_url": "http://192.168.0.61:81/stream",  # input_uri로 변환됨
        "frame_index": 0,
        "probabilities": {"normal": 0.08444983512163162, "warning": 0.4310123920440674, "fall": 0.48453783988952637},
        "label_pred": "Fall",  # fall로 변환됨
        "ts_rel_ms": 1758283984550.982,  # 정수로 변환됨
        "confidence": 0.48453783988952637,
        "passed": False,
        "threshold_name": "test",
        "threshold_snapshot": {"additionalProp1": {}}
    }
    
    print("원본 데이터:")
    print(json.dumps(sample_data, indent=2, ensure_ascii=False))
    print()
    
    # 변환
    converted = convert_frame_prediction_data(sample_data)
    print("변환된 데이터:")
    print(json.dumps(converted, indent=2, ensure_ascii=False))
    print()
    
    # 유효성 검사
    errors = validate_api_data(converted)
    if errors:
        print("유효성 검사 오류:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 유효성 검사 통과!")

