#!/usr/bin/env python3
"""
YOLO 모델과 API 통합 예제

YOLO 모델에서 생성된 데이터를 API 스키마에 맞게 변환하여 전송하는 예제입니다.
"""

import json
import time
import uuid
from typing import Dict, List, Any
from common_api import CommonApiClient
from data_converter import convert_batch_frame_predictions, convert_yolo_output_to_api_format


def simulate_yolo_predictions(num_frames: int = 10) -> List[Dict[str, Any]]:
    """YOLO 모델 예측 결과를 시뮬레이션"""
    
    # 시뮬레이션 데이터 생성
    predictions = []
    session_id = str(uuid.uuid4())
    experiment_id = "12bd0c67-a10c-4e01-adec-871010e49031"
    input_uri = "http://192.168.0.61:81/stream"
    
    labels = ["Fall", "Warning", "Normal"]
    
    for frame_idx in range(num_frames):
        # 랜덤한 예측 결과 생성
        import random
        
        # 확률 분포 생성 (합이 1이 되도록)
        probs = [random.random() for _ in range(3)]
        total = sum(probs)
        probs = [p/total for p in probs]
        
        # 가장 높은 확률의 라벨 선택
        max_idx = probs.index(max(probs))
        label_pred = labels[max_idx]
        confidence = max(probs)
        
        # YOLO 출력 형식 (원시 데이터)
        raw_prediction = {
            "session_id": session_id,
            "experiment_id": experiment_id,
            "input_url": input_uri,  # API에서는 input_uri로 변환됨
            "frame_index": frame_idx,
            "probabilities": {
                "normal": probs[2],
                "warning": probs[1], 
                "fall": probs[0]
            },
            "label_pred": label_pred,  # API에서는 소문자로 변환됨
            "ts_rel_ms": time.time() * 1000,  # API에서는 정수로 변환됨
            "confidence": confidence,
            "passed": confidence > 0.5,
            "threshold_name": "yolo_threshold",
            "threshold_snapshot": {"threshold": 0.5}
        }
        
        predictions.append(raw_prediction)
    
    return predictions


def send_yolo_predictions_to_api(
    client: CommonApiClient, 
    raw_predictions: List[Dict[str, Any]], 
    batch_size: int = 5
) -> Dict[str, Any]:
    """YOLO 예측 결과를 API로 전송"""
    
    results = {
        "total_predictions": len(raw_predictions),
        "successful_batches": 0,
        "failed_batches": 0,
        "created_predictions": 0,
        "errors": []
    }
    
    # 배치 단위로 처리
    for i in range(0, len(raw_predictions), batch_size):
        batch_raw = raw_predictions[i:i + batch_size]
        
        try:
            # API 스키마에 맞게 변환
            batch_data = convert_batch_frame_predictions(batch_raw)
            
            print(f"배치 {i//batch_size + 1} 전송 중... ({len(batch_data['items'])}개 예측)")
            
            # API로 전송
            status_code, response = client.post("/frame-predictions/batch", json=batch_data)
            
            if status_code == 201:
                results["successful_batches"] += 1
                results["created_predictions"] += len(response)
                print(f"  ✅ 성공: {len(response)}개 예측 생성됨")
            else:
                results["failed_batches"] += 1
                error_msg = f"배치 {i//batch_size + 1} 실패: {status_code} - {response}"
                results["errors"].append(error_msg)
                print(f"  ❌ 실패: {error_msg}")
                
        except Exception as e:
            results["failed_batches"] += 1
            error_msg = f"배치 {i//batch_size + 1} 오류: {str(e)}"
            results["errors"].append(error_msg)
            print(f"  ❌ 오류: {error_msg}")
    
    return results


def main():
    """메인 실행 함수"""
    
    print("=" * 60)
    print("YOLO 모델과 API 통합 예제")
    print("=" * 60)
    
    # API 클라이언트 생성
    client = CommonApiClient(base_url="http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com")
    
    # YOLO 예측 결과 시뮬레이션
    print("\n1. YOLO 예측 결과 시뮬레이션...")
    raw_predictions = simulate_yolo_predictions(num_frames=20)
    print(f"   📊 {len(raw_predictions)}개 프레임 예측 생성됨")
    
    # 첫 번째 예측 결과 확인
    print("\n2. 첫 번째 예측 결과 (변환 전):")
    print(json.dumps(raw_predictions[0], indent=2, ensure_ascii=False))
    
    # 변환된 결과 확인
    converted = convert_batch_frame_predictions(raw_predictions[:1])
    print("\n3. 변환된 결과 (API 스키마):")
    print(json.dumps(converted, indent=2, ensure_ascii=False))
    
    # API로 전송
    print("\n4. API로 전송 중...")
    results = send_yolo_predictions_to_api(client, raw_predictions, batch_size=5)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("전송 결과 요약")
    print("=" * 60)
    print(f"총 예측 수: {results['total_predictions']}")
    print(f"성공한 배치: {results['successful_batches']}")
    print(f"실패한 배치: {results['failed_batches']}")
    print(f"생성된 예측: {results['created_predictions']}")
    
    if results['errors']:
        print(f"\n오류 목록:")
        for error in results['errors']:
            print(f"  - {error}")
    else:
        print("\n✅ 모든 배치가 성공적으로 전송되었습니다!")


def create_yolo_integration_function():
    """YOLO 코드에 통합할 수 있는 함수"""
    
    def send_prediction_to_api(
        client: CommonApiClient,
        session_id: str,
        experiment_id: str,
        input_uri: str,
        frame_index: int,
        probabilities: Dict[str, Any],
        label_pred: str,
        confidence: Any,
        ts_rel_ms: Any = None,
        passed: bool = False,
        threshold_name: str = "yolo",
        threshold_snapshot: Dict[str, Any] = None
    ) -> tuple:
        """
        단일 YOLO 예측 결과를 API로 전송
        
        Returns:
            tuple: (status_code, response)
        """
        
        # API 형식으로 변환
        api_data = convert_yolo_output_to_api_format(
            session_id=session_id,
            experiment_id=experiment_id,
            input_uri=input_uri,
            frame_index=frame_index,
            probabilities=probabilities,
            label_pred=label_pred,
            confidence=confidence,
            ts_rel_ms=ts_rel_ms,
            passed=passed,
            threshold_name=threshold_name,
            threshold_snapshot=threshold_snapshot
        )
        
        # API로 전송
        return client.post("/frame-predictions", json=api_data)
    
    def send_batch_predictions_to_api(
        client: CommonApiClient,
        raw_predictions: List[Dict[str, Any]]
    ) -> tuple:
        """
        배치 YOLO 예측 결과를 API로 전송
        
        Returns:
            tuple: (status_code, response)
        """
        
        # API 형식으로 변환
        batch_data = convert_batch_frame_predictions(raw_predictions)
        
        # API로 전송
        return client.post("/frame-predictions/batch", json=batch_data)
    
    return send_prediction_to_api, send_batch_predictions_to_api


if __name__ == "__main__":
    main()

