"""
공통 RESTful API 클라이언트 (Common API Client)

설치(필수):
    pip install requests

이 모듈은 표준 RESTful API 또는 일반 HTTP API를 간편하게 호출하기 위한 범용 클라이언트입니다.
이 프로젝트(서버)에서 제공하는 Datasets/Experiments/Frame-Predictions/Detection-Events API를
예시로 사용 방법을 상세히 설명합니다. (외부 API에도 그대로 적용 가능)

1) BASE_URL 설정 방법
   - Nginx 뒤에서 제공되는 운영/스테이징:  http(s)://<host>/api/v1
   - Uvicorn 로컬 직접 실행:            http://localhost:8000/api/v1
   - 주의: BASE_URL 끝에 "/api/v1"가 없는 경우, 본 클라이언트가 자동으로 "/api/v1"를 덧붙입니다.

2) ENDPOINT(엔드포인트) 경로 작성 규칙
   - 선행 슬래시(/)를 포함하여 작성: 
       "/datasets", "/experiments", "/frame-predictions", "/detection-events"
   - 하위 리소스:  f"/datasets/{dataset_id}", f"/experiments/{experiment_id}"

3) JSON Data(요청 본문) 작성 규칙
   - POST/PUT/PATCH 등 바디가 필요한 메서드에서 `json=dict` 형태로 전달
   - GET/DELETE 등에서는 쿼리스트링 파라미터는 `params=dict` 로 전달

4) HTTP METHOD 의미 요약 (REST 관례)
   - GET:    조회(컬렉션/단건). 서버 상태 변경 없음. 캐시 가능성 높음.
   - POST:   생성(컬렉션에 새 리소스 추가) 또는 서버측 처리 트리거.
   - PUT:    전체 업데이트(리소스 교체). 일부 API는 부분 업데이트로 취급하기도 함.
   - PATCH:  부분 업데이트(리소스 일부 필드만 변경).
   - DELETE: 삭제(리소스 제거). 이 프로젝트는 논리/물리 삭제 정책에 따라 다를 수 있음.
   - HEAD/OPTIONS: 메타 정보/프리플라이트 확인용. 본 클라이언트에 보조 메서드 제공.

5) 인증/헤더/타임아웃/재시도
   - headers: 공통/개별 요청 헤더 지정 (예: Authorization: Bearer <token>)
   - timeout: 요청 타임아웃(초)
   - retries/backoff: 네트워크 일시 장애에 대한 재시도 설정(기본 0, 선택)

6) Reference(참조 키) 사용 가이드 (이 프로젝트 기준)
   - dataset_id (UUID): Datasets API에서 생성/목록 조회로 획득, Experiments 생성 시 참조
   - experiment_id (UUID): Experiments API에서 획득, Frame-Predictions/Detection-Events에서 참조
   - session_id (UUID): 클라이언트가 한 번의 추론 실행(동일 입력)을 묶기 위해 생성/사용

예시 코드(이 프로젝트 API 예시):
    from common_api import CommonApiClient
    
    client = CommonApiClient(base_url="http://localhost:8000/api/v1")
    
    # 1) 데이터셋 생성 (POST)
    code, dataset = client.post(
        "/datasets",
        json={
            "name": "demo",
            "version": "v1",
            "storage_path": "file:///data/demo",
            "class_schema": {"labels": ["normal","warning","fall"]},
            "tags": ["demo"]
        }
    )
    assert code == 201
    dataset_id = dataset["dataset_id"]

    # 2) 데이터셋 목록 조회 (GET, 쿼리 파라미터)
    code, datasets = client.get("/datasets", params={"skip": 0, "limit": 10})

    # 3) 실험 생성 (POST, dataset_id 참조)
    code, exp = client.post(
        "/experiments",
        json={
            "name": "exp-lstm-v1",
            "dataset_id": dataset_id,
            "model_path": "s3://bucket/model.pt",
            "framework": "pytorch"
        }
    )
    experiment_id = exp.get("experiment_id")

    # 4) 프레임 예측(단건) 생성 (POST)
    import uuid
    sid = str(uuid.uuid4())
    code, fp = client.post(
        "/frame-predictions",
        json={
            "session_id": sid,
            "experiment_id": experiment_id,
            "input_uri": "file:///video.mp4",
            "frame_index": 0,
            "probabilities": {"normal": 1.0},
            "label_pred": "normal"
        }
    )
    assert code == 201

    # 5) 이벤트 조회 (GET)
    code, events = client.get("/detection-events", params={"session_id": sid})
    print(code, events)
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import requests

try:
    # 재시도(선택) 지원
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    HTTPAdapter = None  # type: ignore
    Retry = None       # type: ignore


class CommonApiClient:
    """범용 REST API 클라이언트

    - BASE_URL: API 루트. 
      * 예: http://localhost:8000/api/v1  또는 http://host/api/v1
      * 만약 "/api/v1" 가 빠져 있으면 자동으로 덧붙입니다.
    - ENDPOINT: 리소스 경로. 
      * 예: "/datasets", "/experiments/{id}"
    - JSON Data: POST/PUT/PATCH 바디로 전달할 dict
    - params: GET/DELETE 등에 사용할 쿼리스트링 dict
    - headers: Authorization 등 필요 헤더를 dict 로 전달
    """

    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        retries: int = 0,
        backoff_factor: float = 0.3,
    ) -> None:
        # /api/v1 자동 보정
        if not base_url.endswith("/api/v1"):
            if base_url.rstrip("/").endswith("/api"):
                base_url = base_url.rstrip("/") + "/v1"
            elif not base_url.rstrip("/").endswith("/api/v1"):
                base_url = base_url.rstrip("/") + "/api/v1"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = default_headers or {}

        self.session = requests.Session()
        # 재시도 설정(선택)
        if retries and HTTPAdapter and Retry:
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"),
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

    # ----------------- 범용 요청 메서드 -----------------
    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Any] = None,
    ) -> Tuple[int, Any]:
        """범용 HTTP 요청 메서드

        method: GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS 등
        endpoint: "/datasets" 같은 리소스 경로(절대 URL도 지원)
        params: 쿼리스트링 dict
        json: JSON 바디(dict)
        data: 폼/바이너리 등 비JSON 바디
        headers: 요청 헤더
        auth: requests 인증 객체(예: HTTPBasicAuth, Bearer 토큰 직접 헤더로 권장)
        """
        url = endpoint
        if not endpoint.lower().startswith("http"):
            url = self.base_url + endpoint

        all_headers = {**self.default_headers, **(headers or {})}
        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            data=data,
            headers=all_headers,
            auth=auth,
            timeout=self.timeout,
        )
        return self._resp(resp)

    # ----------------- 편의 메서드 -----------------
    def get(self, endpoint: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
        return self.request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint: str, *, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, data: Optional[Any] = None) -> Tuple[int, Any]:
        return self.request("POST", endpoint, json=json, data=data, headers=headers)

    def put(self, endpoint: str, *, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
        return self.request("PUT", endpoint, json=json, headers=headers)

    def patch(self, endpoint: str, *, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
        return self.request("PATCH", endpoint, json=json, headers=headers)

    def delete(self, endpoint: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
        return self.request("DELETE", endpoint, params=params, headers=headers)

    def head(self, endpoint: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
        return self.request("HEAD", endpoint, params=params, headers=headers)

    def options(self, endpoint: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
        return self.request("OPTIONS", endpoint, params=params, headers=headers)

    # ----------------- 응답 처리 -----------------
    @staticmethod
    def _resp(r: requests.Response) -> Tuple[int, Any]:
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text


if __name__ == "__main__":
    # 간단 예제 실행: Datasets 목록 가져오기
    client = CommonApiClient(base_url="http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com")
    status, body = client.post(
        "/frame-predictions/batch", json={
                                    "items": [
                                        {
                                        "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                        "experiment_id": "12bd0c67-a10c-4e01-adec-871010e49031",
                                        "input_uri": "http://192.168.0.61:81/stream",
                                        "frame_index": 1,
                                        "probabilities": {
                                            "normal": 0.95,
                                            "warning": 0.03,
                                            "fall": 0.02
                                        },
                                        "label_pred": "normal",
                                        "ts_rel_ms": 100,
                                        "confidence": 0.95,
                                        "passed": True,
                                        "threshold_name": "test",
                                        "threshold_snapshot": {
                                            "additionalProp1": {}
                                        }
                                        },
                                        {
                                        "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                        "experiment_id": "12bd0c67-a10c-4e01-adec-871010e49031",
                                        "input_uri": "http://192.168.0.61:81/stream",
                                        "frame_index": 2,
                                        "probabilities": {
                                            "normal": 0.1,
                                            "warning": 0.85,
                                            "fall": 0.05
                                        },
                                        "label_pred": "warning",
                                        "ts_rel_ms": 200,
                                        "confidence": 0.85,
                                        "passed": True,
                                        "threshold_name": "test",
                                        "threshold_snapshot": {
                                            "additionalProp1": {}
                                        }
                                        }
                                    ]
                                }
)
    print(status, body)

