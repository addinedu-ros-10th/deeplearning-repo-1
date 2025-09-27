#!/usr/bin/env python3
"""
감지 이벤트(Detection Event) API 사용 예제

이 스크립트는 common_api.py를 사용하여 감지 이벤트 API를 호출하는 예제입니다.
실제 운영 환경과 로컬 환경 모두에서 사용할 수 있습니다.

사용법:
    python detection_event_api_example.py [--base-url <URL>] [--env <local|prod>]

예시:
    # 로컬 환경 (기본값)
    python detection_event_api_example.py
    
    # 운영 환경
    python detection_event_api_example.py --env prod
    
    # 커스텀 URL
    python detection_event_api_example.py --base-url http://custom-host:8000
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


def create_detection_event_example(client: CommonApiClient, experiment_id: str) -> Dict[str, Any]:
    """감지 이벤트 생성 예제"""
    print("=" * 60)
    print("감지 이벤트(Detection Event) 생성 예제")
    print("=" * 60)
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 감지 이벤트 데이터 준비 (올바른 API 스키마)
    detection_event_data = {
        "session_id": session_id,
        "experiment_id": experiment_id,
        "input_uri": "file:///data/video_demo.mp4",
        "start_frame": 10,
        "end_frame": 20,
        "event_type": "fall_detected",
        "top_label": "fall",
        "threshold_snapshot": {"fall": 0.8, "warning": 0.6, "normal": 0.3},
        "max_confidence": 0.95,
        "agg_prob": {"fall": 0.85, "warning": 0.10, "normal": 0.05},
        "start_ts_ms": 1000,
        "end_ts_ms": 2000,
        "threshold_name": "default_v1",
        "trigger_reason": "confidence_threshold_exceeded"
    }
    
    print("요청 데이터:")
    print(json.dumps(detection_event_data, indent=2, ensure_ascii=False))
    print()
    
    # 감지 이벤트 생성 요청
    print("감지 이벤트 생성 중...")
    status_code, response = client.post("/detection-events", json=detection_event_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 201:
        print("✅ 감지 이벤트 생성 성공!")
        return response
    else:
        print(f"❌ 감지 이벤트 생성 실패: {status_code}")
        return {}


def create_multiple_detection_events_example(client: CommonApiClient, experiment_id: str) -> List[Dict[str, Any]]:
    """여러 감지 이벤트 생성 예제"""
    print("\n" + "=" * 60)
    print("여러 감지 이벤트 생성 예제")
    print("=" * 60)
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 여러 감지 이벤트 데이터 준비 (올바른 API 스키마)
    events_data = [
        {
            "session_id": session_id,
            "experiment_id": experiment_id,
            "input_uri": "file:///data/video_demo.mp4",
            "start_frame": 5,
            "end_frame": 15,
            "event_type": "warning_detected",
            "top_label": "warning",
            "threshold_snapshot": {"warning": 0.7, "fall": 0.8, "normal": 0.3},
            "max_confidence": 0.75,
            "agg_prob": {"warning": 0.70, "normal": 0.25, "fall": 0.05},
            "start_ts_ms": 500,
            "end_ts_ms": 1500,
            "threshold_name": "default_v1",
            "trigger_reason": "warning_threshold_exceeded"
        },
        {
            "session_id": session_id,
            "experiment_id": experiment_id,
            "input_uri": "file:///data/video_demo.mp4",
            "start_frame": 15,
            "end_frame": 25,
            "event_type": "fall_detected",
            "top_label": "fall",
            "threshold_snapshot": {"fall": 0.8, "warning": 0.6, "normal": 0.3},
            "max_confidence": 0.92,
            "agg_prob": {"fall": 0.90, "warning": 0.08, "normal": 0.02},
            "start_ts_ms": 1500,
            "end_ts_ms": 2500,
            "threshold_name": "default_v1",
            "trigger_reason": "fall_threshold_exceeded"
        },
        {
            "session_id": session_id,
            "experiment_id": experiment_id,
            "input_uri": "file:///data/video_demo.mp4",
            "start_frame": 25,
            "end_frame": 35,
            "event_type": "normal_detected",
            "top_label": "normal",
            "threshold_snapshot": {"normal": 0.5, "warning": 0.7, "fall": 0.8},
            "max_confidence": 0.88,
            "agg_prob": {"normal": 0.85, "warning": 0.10, "fall": 0.05},
            "start_ts_ms": 2500,
            "end_ts_ms": 3500,
            "threshold_name": "default_v1",
            "trigger_reason": "normal_behavior_detected"
        }
    ]
    
    created_events = []
    
    for i, event_data in enumerate(events_data, 1):
        print(f"\n--- 이벤트 {i} 생성 ---")
        print("요청 데이터:")
        print(json.dumps(event_data, indent=2, ensure_ascii=False))
        
        # 감지 이벤트 생성 요청
        print("감지 이벤트 생성 중...")
        status_code, response = client.post("/detection-events", json=event_data)
        
        print(f"응답 상태 코드: {status_code}")
        if status_code == 201:
            print("✅ 감지 이벤트 생성 성공!")
            created_events.append(response)
        else:
            print(f"❌ 감지 이벤트 생성 실패: {status_code}")
            print("응답 데이터:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
    
    return created_events


def list_detection_events_example(client: CommonApiClient, session_id: str = None) -> None:
    """감지 이벤트 목록 조회 예제"""
    print("\n" + "=" * 60)
    print("감지 이벤트 목록 조회 예제")
    print("=" * 60)
    
    # 쿼리 파라미터 설정
    params = {"skip": 0, "limit": 10}
    if session_id:
        params["session_id"] = session_id
        print(f"세션 ID로 필터링: {session_id}")
    
    # 감지 이벤트 목록 조회
    print("감지 이벤트 목록 조회 중...")
    status_code, response = client.get("/detection-events", params=params)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 감지 이벤트 목록 조회 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 감지 이벤트 목록 조회 실패: {status_code}")


def get_detection_event_example(client: CommonApiClient, event_id: str) -> None:
    """특정 감지 이벤트 조회 예제"""
    print("\n" + "=" * 60)
    print(f"특정 감지 이벤트 조회 예제 (ID: {event_id})")
    print("=" * 60)
    
    # 특정 감지 이벤트 조회
    print("감지 이벤트 조회 중...")
    status_code, response = client.get(f"/detection-events/{event_id}")
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 감지 이벤트 조회 성공!")
    else:
        print(f"❌ 감지 이벤트 조회 실패: {status_code}")


def filter_detection_events_by_type_example(client: CommonApiClient, event_type: str) -> None:
    """이벤트 타입으로 감지 이벤트 필터링 예제"""
    print("\n" + "=" * 60)
    print(f"이벤트 타입으로 감지 이벤트 필터링 예제 (타입: {event_type})")
    print("=" * 60)
    
    # 이벤트 타입으로 필터링
    print("감지 이벤트 필터링 중...")
    status_code, response = client.get("/detection-events", params={
        "event_type": event_type,
        "skip": 0,
        "limit": 10
    })
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 감지 이벤트 필터링 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 감지 이벤트 필터링 실패: {status_code}")


def update_detection_event_example(client: CommonApiClient, event_id: str) -> None:
    """감지 이벤트 업데이트 예제"""
    print("\n" + "=" * 60)
    print(f"감지 이벤트 업데이트 예제 (ID: {event_id})")
    print("=" * 60)
    
    # 업데이트 데이터 준비
    update_data = {
        "confidence": 0.98,
        "metadata": {
            "video_path": "file:///data/video_demo.mp4",
            "frame_index": 15,
            "detection_model": "yolo_v8_fall_detection_updated",
            "threshold": 0.85,
            "updated_at": datetime.now().isoformat()
        }
    }
    
    print("업데이트 데이터:")
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    print()
    
    # 감지 이벤트 업데이트 요청
    print("감지 이벤트 업데이트 중...")
    status_code, response = client.put(f"/detection-events/{event_id}", json=update_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 감지 이벤트 업데이트 성공!")
    else:
        print(f"❌ 감지 이벤트 업데이트 실패: {status_code}")


def delete_detection_event_example(client: CommonApiClient, event_id: str) -> None:
    """감지 이벤트 삭제 예제"""
    print("\n" + "=" * 60)
    print(f"감지 이벤트 삭제 예제 (ID: {event_id})")
    print("=" * 60)
    
    # 감지 이벤트 삭제 요청
    print("감지 이벤트 삭제 중...")
    status_code, response = client.delete(f"/detection-events/{event_id}")
    
    print(f"응답 상태 코드: {status_code}")
    if response:
        print("응답 데이터:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 감지 이벤트 삭제 성공!")
    else:
        print(f"❌ 감지 이벤트 삭제 실패: {status_code}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='감지 이벤트 API 사용 예제')
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
        
        # 1. 감지 이벤트 생성 (단건)
        created_event = create_detection_event_example(client, experiment_id)
        event_id = created_event.get('event_id')
        session_id = created_event.get('session_id')
        
        # 2. 여러 감지 이벤트 생성
        multiple_events = create_multiple_detection_events_example(client, experiment_id)
        
        # 3. 감지 이벤트 목록 조회
        list_detection_events_example(client, session_id)
        
        # 4. 특정 감지 이벤트 조회
        if event_id:
            get_detection_event_example(client, event_id)
            
            # 5. 이벤트 타입으로 필터링
            filter_detection_events_by_type_example(client, "fall_detected")
            
            # 6. 감지 이벤트 업데이트
            update_detection_event_example(client, event_id)
            
            # 7. 감지 이벤트 삭제 (옵션)
            if not args.skip_delete:
                delete_detection_event_example(client, event_id)
            else:
                print("\n" + "=" * 60)
                print("감지 이벤트 삭제 예제 건너뛰기 (--skip-delete 옵션)")
                print("=" * 60)
                print(f"생성된 감지 이벤트 ID: {event_id}")
                print("수동으로 삭제하려면 다음 명령을 사용하세요:")
                print(f"curl -X DELETE '{base_url}/api/v1/detection-events/{event_id}'")
        
        print("\n" + "=" * 60)
        print("✅ 모든 예제 실행 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("API 서버가 실행 중인지 확인하세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
