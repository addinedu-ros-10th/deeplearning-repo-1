#!/usr/bin/env python3
"""
프레임 예측(Frame Prediction) API 사용 예제

이 스크립트는 common_api.py를 사용하여 프레임 예측 API를 호출하는 예제입니다.
실제 운영 환경과 로컬 환경 모두에서 사용할 수 있습니다.

사용법:
    python frame_prediction_api_example.py [--base-url <URL>] [--env <local|prod>]

예시:
    # 로컬 환경 (기본값)
    python frame_prediction_api_example.py
    
    # 운영 환경
    python frame_prediction_api_example.py --env prod
    
    # 커스텀 URL
    python frame_prediction_api_example.py --base-url http://custom-host:8000
"""

import sys
import argparse
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# common_api 모듈 import
sys.path.append('..')
from common_api import CommonApiClient


def get_base_url(env: str = 'local') -> str:
    """환경에 따른 기본 URL 반환"""
    if env == 'prod':
        return "http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com"
    else:
        return "http://localhost:8000"


def create_frame_prediction_example(client: CommonApiClient, experiment_id: str) -> Dict[str, Any]:
    """프레임 예측 생성 예제 (단건)"""
    print("=" * 60)
    print("프레임 예측(Frame Prediction) 생성 예제 (단건)")
    print("=" * 60)
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 프레임 예측 데이터 준비
    frame_prediction_data = {
        "session_id": session_id,
        "experiment_id": experiment_id,
        "input_uri": "file:///data/video_demo.mp4",
        "frame_index": 0,
        "probabilities": {
            "normal": 0.85,
            "warning": 0.10,
            "fall": 0.05
        },
        "label_pred": "normal",
        "confidence": 0.85,
        "bbox": {
            "x": 100,
            "y": 150,
            "width": 200,
            "height": 300
        }
    }
    
    print("요청 데이터:")
    print(json.dumps(frame_prediction_data, indent=2, ensure_ascii=False))
    print()
    
    # 프레임 예측 생성 요청
    print("프레임 예측 생성 중...")
    status_code, response = client.post("/frame-predictions", json=frame_prediction_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 201:
        print("✅ 프레임 예측 생성 성공!")
        return response
    else:
        print(f"❌ 프레임 예측 생성 실패: {status_code}")
        return {}


def create_frame_predictions_batch_example(client: CommonApiClient, experiment_id: str) -> List[Dict[str, Any]]:
    """프레임 예측 생성 예제 (배치)"""
    print("\n" + "=" * 60)
    print("프레임 예측(Frame Prediction) 생성 예제 (배치)")
    print("=" * 60)
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 배치 프레임 예측 데이터 준비 (올바른 API 스키마)
    batch_data = {
        "items": [
            {
                "session_id": session_id,
                "experiment_id": experiment_id,
                "input_uri": "file:///data/video_demo.mp4",
                "frame_index": 0,
                "probabilities": {"normal": 0.85, "warning": 0.10, "fall": 0.05},
                "label_pred": "normal",
                "confidence": 0.85
            },
            {
                "session_id": session_id,
                "experiment_id": experiment_id,
                "input_uri": "file:///data/video_demo.mp4",
                "frame_index": 1,
                "probabilities": {"normal": 0.70, "warning": 0.25, "fall": 0.05},
                "label_pred": "normal",
                "confidence": 0.70
            },
            {
                "session_id": session_id,
                "experiment_id": experiment_id,
                "input_uri": "file:///data/video_demo.mp4",
                "frame_index": 2,
                "probabilities": {"normal": 0.30, "warning": 0.60, "fall": 0.10},
                "label_pred": "warning",
                "confidence": 0.60
            }
        ]
    }
    
    print("요청 데이터:")
    print(json.dumps(batch_data, indent=2, ensure_ascii=False))
    print()
    
    # 배치 프레임 예측 생성 요청
    print("배치 프레임 예측 생성 중...")
    status_code, response = client.post("/frame-predictions/batch", json=batch_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 201:
        print("✅ 배치 프레임 예측 생성 성공!")
        return response
    else:
        print(f"❌ 배치 프레임 예측 생성 실패: {status_code}")
        return []


def list_frame_predictions_example(client: CommonApiClient, session_id: str = None) -> None:
    """프레임 예측 목록 조회 예제"""
    print("\n" + "=" * 60)
    print("프레임 예측 목록 조회 예제")
    print("=" * 60)
    
    # 쿼리 파라미터 설정
    params = {"skip": 0, "limit": 10}
    if session_id:
        params["session_id"] = session_id
        print(f"세션 ID로 필터링: {session_id}")
    
    # 프레임 예측 목록 조회
    print("프레임 예측 목록 조회 중...")
    status_code, response = client.get("/frame-predictions", params=params)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 프레임 예측 목록 조회 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 프레임 예측 목록 조회 실패: {status_code}")


def get_frame_prediction_example(client: CommonApiClient, prediction_id: str) -> None:
    """특정 프레임 예측 조회 예제"""
    print("\n" + "=" * 60)
    print(f"특정 프레임 예측 조회 예제 (ID: {prediction_id})")
    print("=" * 60)
    
    # 특정 프레임 예측 조회
    print("프레임 예측 조회 중...")
    status_code, response = client.get(f"/frame-predictions/{prediction_id}")
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 프레임 예측 조회 성공!")
    else:
        print(f"❌ 프레임 예측 조회 실패: {status_code}")


def update_frame_prediction_example(client: CommonApiClient, prediction_id: str) -> None:
    """프레임 예측 업데이트 예제"""
    print("\n" + "=" * 60)
    print(f"프레임 예측 업데이트 예제 (ID: {prediction_id})")
    print("=" * 60)
    
    # 업데이트 데이터 준비
    update_data = {
        "probabilities": {
            "normal": 0.90,
            "warning": 0.08,
            "fall": 0.02
        },
        "label_pred": "normal",
        "confidence": 0.90
    }
    
    print("업데이트 데이터:")
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    print()
    
    # 프레임 예측 업데이트 요청
    print("프레임 예측 업데이트 중...")
    status_code, response = client.put(f"/frame-predictions/{prediction_id}", json=update_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 프레임 예측 업데이트 성공!")
    else:
        print(f"❌ 프레임 예측 업데이트 실패: {status_code}")


def delete_frame_prediction_example(client: CommonApiClient, prediction_id: str) -> None:
    """프레임 예측 삭제 예제"""
    print("\n" + "=" * 60)
    print(f"프레임 예측 삭제 예제 (ID: {prediction_id})")
    print("=" * 60)
    
    # 프레임 예측 삭제 요청
    print("프레임 예측 삭제 중...")
    status_code, response = client.delete(f"/frame-predictions/{prediction_id}")
    
    print(f"응답 상태 코드: {status_code}")
    if response:
        print("응답 데이터:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 프레임 예측 삭제 성공!")
    else:
        print(f"❌ 프레임 예측 삭제 실패: {status_code}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='프레임 예측 API 사용 예제')
    parser.add_argument('--base-url', type=str, help='API 기본 URL')
    parser.add_argument('--env', choices=['local', 'prod'], default='local', 
                       help='환경 선택 (local 또는 prod)')
    parser.add_argument('--experiment-id', type=str, 
                       help='실험 ID (지정하지 않으면 기존 실험 사용)')
    parser.add_argument('--skip-delete', action='store_true', 
                       help='삭제 예제 건너뛰기')
    
    args = parser.parse_args()
    
    # API 클라이언트 설정
    if args.base_url:
        base_url = args.base_url
    else:
        base_url = get_base_url(args.env)
    
    print(f"API 기본 URL: {base_url}")
    print(f"환경: {args.env}")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # API 클라이언트 생성
    client = CommonApiClient(
        base_url=base_url,
        timeout=30.0,  # 타임아웃 30초
        retries=2      # 재시도 2회
    )
    
    try:
        # 실험 ID 확인
        experiment_id = args.experiment_id
        if not experiment_id:
            # 기존 실험 목록에서 첫 번째 실험 사용
            print("실험 ID가 지정되지 않았습니다. 기존 실험을 조회합니다...")
            status_code, experiments = client.get("/experiments", params={"skip": 0, "limit": 1})
            if status_code == 200 and experiments:
                experiment_id = experiments[0]["experiment_id"]
                print(f"사용할 실험 ID: {experiment_id}")
            else:
                print("❌ 사용 가능한 실험이 없습니다. 실험을 먼저 생성하세요.")
                return
        
        # 1. 프레임 예측 생성 (단건)
        created_prediction = create_frame_prediction_example(client, experiment_id)
        prediction_id = created_prediction.get('prediction_id')
        session_id = created_prediction.get('session_id')
        
        # 2. 프레임 예측 생성 (배치)
        batch_predictions = create_frame_predictions_batch_example(client, experiment_id)
        
        # 3. 프레임 예측 목록 조회
        list_frame_predictions_example(client, session_id)
        
        # 4. 특정 프레임 예측 조회
        if prediction_id:
            get_frame_prediction_example(client, prediction_id)
            
            # 5. 프레임 예측 업데이트
            update_frame_prediction_example(client, prediction_id)
            
            # 6. 프레임 예측 삭제 (옵션)
            if not args.skip_delete:
                delete_frame_prediction_example(client, prediction_id)
            else:
                print("\n" + "=" * 60)
                print("프레임 예측 삭제 예제 건너뛰기 (--skip-delete 옵션)")
                print("=" * 60)
                print(f"생성된 프레임 예측 ID: {prediction_id}")
                print("수동으로 삭제하려면 다음 명령을 사용하세요:")
                print(f"curl -X DELETE '{base_url}/api/v1/frame-predictions/{prediction_id}'")
        
        print("\n" + "=" * 60)
        print("✅ 모든 예제 실행 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("API 서버가 실행 중인지 확인하세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
