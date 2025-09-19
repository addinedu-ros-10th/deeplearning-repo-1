#!/usr/bin/env python3
"""
실험(Experiment) API 사용 예제

이 스크립트는 common_api.py를 사용하여 실험 API를 호출하는 예제입니다.
실제 운영 환경과 로컬 환경 모두에서 사용할 수 있습니다.

사용법:
    python experiment_api_example.py [--base-url <URL>] [--env <local|prod>]

예시:
    # 로컬 환경 (기본값)
    python experiment_api_example.py
    
    # 운영 환경
    python experiment_api_example.py --env prod
    
    # 커스텀 URL
    python experiment_api_example.py --base-url http://custom-host:8000
"""

import sys
import argparse
import json
from datetime import datetime
from typing import Dict, Any

# common_api 모듈 import
sys.path.append('..')
from common_api import CommonApiClient


def get_base_url(env: str = 'local') -> str:
    """환경에 따른 기본 URL 반환"""
    if env == 'prod':
        return "http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com"
    else:
        return "http://localhost:8000"


def create_experiment_example(client: CommonApiClient) -> Dict[str, Any]:
    """실험 생성 예제"""
    print("=" * 60)
    print("실험(Experiment) 생성 예제")
    print("=" * 60)
    
    # 실험 데이터 준비 (고유한 이름을 위해 타임스탬프 추가)
    import time
    timestamp = int(time.time())
    experiment_data = {
        "name": f"data_461_nb_sdj_ver0.0_{timestamp}",
        "dataset_id": "0f5b28a4-d701-4c40-8bd5-a773a3a2605a",
        "model_path": "/home/guehojung/Downloads/data_461_nb_sdj_ver1.0.pt",
        "framework": "pytorch",
        "code_version": "1.0",
        "params": {
            "batch": 3,
            "epoch": 100,
            "learning_rate": 0.001
        },
        "metrics": {
            "accuracy": 0.95,
            "f1_score": 0.92
        }
    }
    
    print("요청 데이터:")
    print(json.dumps(experiment_data, indent=2, ensure_ascii=False))
    print()
    
    # 실험 생성 요청
    print("실험 생성 중...")
    status_code, response = client.post("/experiments", json=experiment_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 201:
        print("✅ 실험 생성 성공!")
        return response
    else:
        print(f"❌ 실험 생성 실패: {status_code}")
        return {}


def list_experiments_example(client: CommonApiClient) -> None:
    """실험 목록 조회 예제"""
    print("\n" + "=" * 60)
    print("실험 목록 조회 예제")
    print("=" * 60)
    
    # 실험 목록 조회
    print("실험 목록 조회 중...")
    status_code, response = client.get("/experiments", params={"skip": 0, "limit": 10})
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 실험 목록 조회 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 실험 목록 조회 실패: {status_code}")


def get_experiment_example(client: CommonApiClient, experiment_id: str) -> None:
    """특정 실험 조회 예제"""
    print("\n" + "=" * 60)
    print(f"특정 실험 조회 예제 (ID: {experiment_id})")
    print("=" * 60)
    
    # 특정 실험 조회
    print("실험 조회 중...")
    status_code, response = client.get(f"/experiments/{experiment_id}")
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 실험 조회 성공!")
    else:
        print(f"❌ 실험 조회 실패: {status_code}")


def update_experiment_example(client: CommonApiClient, experiment_id: str) -> None:
    """실험 업데이트 예제"""
    print("\n" + "=" * 60)
    print(f"실험 업데이트 예제 (ID: {experiment_id})")
    print("=" * 60)
    
    # 업데이트 데이터 준비
    update_data = {
        "name": "data_461_nb_sdj_ver0.1",  # 버전 업데이트
        "metrics": {
            "additionalProp1": {
                "accuracy": 0.95,
                "f1_score": 0.92,
                "precision": 0.94,
                "recall": 0.90
            }
        }
    }
    
    print("업데이트 데이터:")
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    print()
    
    # 실험 업데이트 요청
    print("실험 업데이트 중...")
    status_code, response = client.put(f"/experiments/{experiment_id}", json=update_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 실험 업데이트 성공!")
    else:
        print(f"❌ 실험 업데이트 실패: {status_code}")


def delete_experiment_example(client: CommonApiClient, experiment_id: str) -> None:
    """실험 삭제 예제"""
    print("\n" + "=" * 60)
    print(f"실험 삭제 예제 (ID: {experiment_id})")
    print("=" * 60)
    
    # 실험 삭제 요청
    print("실험 삭제 중...")
    status_code, response = client.delete(f"/experiments/{experiment_id}")
    
    print(f"응답 상태 코드: {status_code}")
    if response:
        print("응답 데이터:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 실험 삭제 성공!")
    else:
        print(f"❌ 실험 삭제 실패: {status_code}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='실험 API 사용 예제')
    parser.add_argument('--base-url', type=str, help='API 기본 URL')
    parser.add_argument('--env', choices=['local', 'prod'], default='local', 
                       help='환경 선택 (local 또는 prod)')
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
        # 1. 실험 생성
        created_experiment = create_experiment_example(client)
        experiment_id = created_experiment.get('experiment_id')
        
        if not experiment_id:
            print("❌ 실험 생성에 실패하여 다음 단계를 건너뜁니다.")
            return
        
        # 2. 실험 목록 조회
        list_experiments_example(client)
        
        # 3. 특정 실험 조회
        get_experiment_example(client, experiment_id)
        
        # 4. 실험 업데이트
        update_experiment_example(client, experiment_id)
        
        # 5. 실험 삭제 (옵션)
        if not args.skip_delete:
            delete_experiment_example(client, experiment_id)
        else:
            print("\n" + "=" * 60)
            print("실험 삭제 예제 건너뛰기 (--skip-delete 옵션)")
            print("=" * 60)
            print(f"생성된 실험 ID: {experiment_id}")
            print("수동으로 삭제하려면 다음 명령을 사용하세요:")
            print(f"curl -X DELETE '{base_url}/api/v1/experiments/{experiment_id}'")
        
        print("\n" + "=" * 60)
        print("✅ 모든 예제 실행 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("API 서버가 실행 중인지 확인하세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
