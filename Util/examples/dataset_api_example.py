#!/usr/bin/env python3
"""
데이터셋(Dataset) API 사용 예제

이 스크립트는 common_api.py를 사용하여 데이터셋 API를 호출하는 예제입니다.
실제 운영 환경과 로컬 환경 모두에서 사용할 수 있습니다.

사용법:
    python dataset_api_example.py [--base-url <URL>] [--env <local|prod>]

예시:
    # 로컬 환경 (기본값)
    python dataset_api_example.py
    
    # 운영 환경
    python dataset_api_example.py --env prod
    
    # 커스텀 URL
    python dataset_api_example.py --base-url http://custom-host:8000
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


def create_dataset_example(client: CommonApiClient) -> Dict[str, Any]:
    """데이터셋 생성 예제"""
    print("=" * 60)
    print("데이터셋(Dataset) 생성 예제")
    print("=" * 60)
    
    # 데이터셋 데이터 준비
    dataset_data = {
        "name": "fall_detection_demo_v1",
        "version": "1.0",
        "storage_path": "file:///data/fall_detection_demo",
        "description": "낙상 감지 데모 데이터셋 - AI Hub 데이터 기반",
        "creator_name": "개발팀",
        "creator_email": "dev@example.com",
        "source_url": "https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71641",
        "license": "AI HUB 데이터 활용 시 저작권 사항\n자유로운 활용 및 배포 가능",
        "class_schema": {
            "labels": ["normal", "warning", "fall"]
        },
        "tags": ["낙상감지", "AI허브", "데모"]
    }
    
    print("요청 데이터:")
    print(json.dumps(dataset_data, indent=2, ensure_ascii=False))
    print()
    
    # 데이터셋 생성 요청
    print("데이터셋 생성 중...")
    status_code, response = client.post("/datasets", json=dataset_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 201:
        print("✅ 데이터셋 생성 성공!")
        return response
    else:
        print(f"❌ 데이터셋 생성 실패: {status_code}")
        return {}


def list_datasets_example(client: CommonApiClient) -> None:
    """데이터셋 목록 조회 예제"""
    print("\n" + "=" * 60)
    print("데이터셋 목록 조회 예제")
    print("=" * 60)
    
    # 데이터셋 목록 조회
    print("데이터셋 목록 조회 중...")
    status_code, response = client.get("/datasets", params={"skip": 0, "limit": 10})
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 데이터셋 목록 조회 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 데이터셋 목록 조회 실패: {status_code}")


def get_dataset_example(client: CommonApiClient, dataset_id: str) -> None:
    """특정 데이터셋 조회 예제"""
    print("\n" + "=" * 60)
    print(f"특정 데이터셋 조회 예제 (ID: {dataset_id})")
    print("=" * 60)
    
    # 특정 데이터셋 조회
    print("데이터셋 조회 중...")
    status_code, response = client.get(f"/datasets/{dataset_id}")
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 데이터셋 조회 성공!")
    else:
        print(f"❌ 데이터셋 조회 실패: {status_code}")


def search_datasets_by_name_example(client: CommonApiClient, name: str) -> None:
    """이름으로 데이터셋 검색 예제"""
    print("\n" + "=" * 60)
    print(f"이름으로 데이터셋 검색 예제 (이름: {name})")
    print("=" * 60)
    
    # 이름으로 데이터셋 검색
    print("데이터셋 검색 중...")
    status_code, response = client.get(f"/datasets/name/{name}", params={"skip": 0, "limit": 10})
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 데이터셋 검색 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 데이터셋 검색 실패: {status_code}")


def search_datasets_by_tag_example(client: CommonApiClient, tag: str) -> None:
    """태그로 데이터셋 검색 예제"""
    print("\n" + "=" * 60)
    print(f"태그로 데이터셋 검색 예제 (태그: {tag})")
    print("=" * 60)
    
    # 태그로 데이터셋 검색
    print("데이터셋 검색 중...")
    status_code, response = client.get(f"/datasets/tag/{tag}", params={"skip": 0, "limit": 10})
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print(f"✅ 데이터셋 검색 성공! (총 {len(response)}개)")
    else:
        print(f"❌ 데이터셋 검색 실패: {status_code}")


def update_dataset_example(client: CommonApiClient, dataset_id: str) -> None:
    """데이터셋 업데이트 예제"""
    print("\n" + "=" * 60)
    print(f"데이터셋 업데이트 예제 (ID: {dataset_id})")
    print("=" * 60)
    
    # 업데이트 데이터 준비
    update_data = {
        "description": "낙상 감지 데모 데이터셋 - AI Hub 데이터 기반 (업데이트됨)",
        "tags": ["낙상감지", "AI허브", "데모", "업데이트됨"]
    }
    
    print("업데이트 데이터:")
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    print()
    
    # 데이터셋 업데이트 요청
    print("데이터셋 업데이트 중...")
    status_code, response = client.put(f"/datasets/{dataset_id}", json=update_data)
    
    print(f"응답 상태 코드: {status_code}")
    print("응답 데이터:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 데이터셋 업데이트 성공!")
    else:
        print(f"❌ 데이터셋 업데이트 실패: {status_code}")


def delete_dataset_example(client: CommonApiClient, dataset_id: str) -> None:
    """데이터셋 삭제 예제"""
    print("\n" + "=" * 60)
    print(f"데이터셋 삭제 예제 (ID: {dataset_id})")
    print("=" * 60)
    
    # 데이터셋 삭제 요청
    print("데이터셋 삭제 중...")
    status_code, response = client.delete(f"/datasets/{dataset_id}")
    
    print(f"응답 상태 코드: {status_code}")
    if response:
        print("응답 데이터:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if status_code == 200:
        print("✅ 데이터셋 삭제 성공!")
    else:
        print(f"❌ 데이터셋 삭제 실패: {status_code}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='데이터셋 API 사용 예제')
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
        # 1. 데이터셋 생성
        created_dataset = create_dataset_example(client)
        dataset_id = created_dataset.get('dataset_id')
        
        if not dataset_id:
            print("❌ 데이터셋 생성에 실패하여 다음 단계를 건너뜁니다.")
            return
        
        # 2. 데이터셋 목록 조회
        list_datasets_example(client)
        
        # 3. 특정 데이터셋 조회
        get_dataset_example(client, dataset_id)
        
        # 4. 이름으로 데이터셋 검색
        search_datasets_by_name_example(client, "fall_detection_demo_v1")
        
        # 5. 태그로 데이터셋 검색
        search_datasets_by_tag_example(client, "낙상감지")
        
        # 6. 데이터셋 업데이트
        update_dataset_example(client, dataset_id)
        
        # 7. 데이터셋 삭제 (옵션)
        if not args.skip_delete:
            delete_dataset_example(client, dataset_id)
        else:
            print("\n" + "=" * 60)
            print("데이터셋 삭제 예제 건너뛰기 (--skip-delete 옵션)")
            print("=" * 60)
            print(f"생성된 데이터셋 ID: {dataset_id}")
            print("수동으로 삭제하려면 다음 명령을 사용하세요:")
            print(f"curl -X DELETE '{base_url}/api/v1/datasets/{dataset_id}'")
        
        print("\n" + "=" * 60)
        print("✅ 모든 예제 실행 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("API 서버가 실행 중인지 확인하세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
