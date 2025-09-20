# YOLO 모델과 API 통합 가이드

YOLO 모델에서 생성된 데이터를 API 스키마에 맞게 변환하여 전송하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 필요한 파일들
```
Util/
├── common_api.py                    # API 클라이언트
├── data_converter.py                # 데이터 변환 유틸리티
├── yolo_api_integration_example.py  # 통합 예제
└── YOLO_API_INTEGRATION_GUIDE.md    # 이 가이드
```

### 2. 기본 사용법

```python
from common_api import CommonApiClient
from data_converter import convert_yolo_output_to_api_format

# API 클라이언트 생성
client = CommonApiClient(base_url="http://your-api-server.com")

# YOLO 예측 결과를 API 형식으로 변환
api_data = convert_yolo_output_to_api_format(
    session_id="your-session-id",
    experiment_id="your-experiment-id", 
    input_uri="http://192.168.0.61:81/stream",
    frame_index=0,
    probabilities={"normal": 0.1, "warning": 0.2, "fall": 0.7},
    label_pred="Fall",  # 자동으로 "fall"로 변환됨
    confidence=0.7,
    ts_rel_ms=1758283984550.982  # 자동으로 정수로 변환됨
)

# API로 전송
status_code, response = client.post("/frame-predictions", json=api_data)
```

## 🔧 주요 변환 기능

### 1. 필드명 변환
- `input_url` → `input_uri`
- 자동으로 API 스키마에 맞는 필드명으로 변환

### 2. 라벨 형식 변환
- `"Fall"` → `"fall"`
- `"Warning"` → `"warning"`
- `"Normal"` → `"normal"`
- 대소문자 구분 없이 소문자로 변환

### 3. 데이터 타입 변환
- PyTorch Tensor → float
- numpy array → float
- 부동소수점 타임스탬프 → 정수

### 4. 필수 필드 검증
- 누락된 필수 필드 자동 감지
- API 스키마 호환성 검증

## 📋 YOLO 코드 통합 예제

### 단일 예측 전송

```python
import time
import uuid
from common_api import CommonApiClient
from data_converter import convert_yolo_output_to_api_format

def process_yolo_frame(frame, model, client, session_id, experiment_id):
    """YOLO 모델로 프레임 처리 후 API로 전송"""
    
    # YOLO 예측 수행
    predictions = model(frame)
    
    for pred in predictions:
        # YOLO 출력에서 데이터 추출
        probabilities = {
            "normal": pred.probs[0].item(),
            "warning": pred.probs[1].item(), 
            "fall": pred.probs[2].item()
        }
        
        label_pred = pred.names[pred.probs.argmax().item()]
        confidence = pred.probs.max().item()
        
        # API 형식으로 변환
        api_data = convert_yolo_output_to_api_format(
            session_id=session_id,
            experiment_id=experiment_id,
            input_uri="http://192.168.0.61:81/stream",
            frame_index=pred.frame_index,
            probabilities=probabilities,
            label_pred=label_pred,
            confidence=confidence,
            ts_rel_ms=time.time() * 1000,
            passed=confidence > 0.5
        )
        
        # API로 전송
        status_code, response = client.post("/frame-predictions", json=api_data)
        
        if status_code == 201:
            print(f"✅ 예측 전송 성공: {response['frame_pred_id']}")
        else:
            print(f"❌ 예측 전송 실패: {status_code} - {response}")

# 사용 예제
client = CommonApiClient(base_url="http://your-api-server.com")
session_id = str(uuid.uuid4())
experiment_id = "your-experiment-id"

# 프레임 처리 루프
for frame in video_stream:
    process_yolo_frame(frame, yolo_model, client, session_id, experiment_id)
```

### 배치 예측 전송

```python
from data_converter import convert_batch_frame_predictions

def process_yolo_batch(frames, model, client, session_id, experiment_id, batch_size=10):
    """여러 프레임을 배치로 처리 후 API로 전송"""
    
    raw_predictions = []
    
    for i, frame in enumerate(frames):
        predictions = model(frame)
        
        for pred in predictions:
            raw_prediction = {
                "session_id": session_id,
                "experiment_id": experiment_id,
                "input_url": "http://192.168.0.61:81/stream",
                "frame_index": i,
                "probabilities": {
                    "normal": pred.probs[0].item(),
                    "warning": pred.probs[1].item(),
                    "fall": pred.probs[2].item()
                },
                "label_pred": pred.names[pred.probs.argmax().item()],
                "confidence": pred.probs.max().item(),
                "ts_rel_ms": time.time() * 1000,
                "passed": pred.probs.max().item() > 0.5
            }
            raw_predictions.append(raw_prediction)
    
    # 배치로 변환
    batch_data = convert_batch_frame_predictions(raw_predictions)
    
    # API로 전송
    status_code, response = client.post("/frame-predictions/batch", json=batch_data)
    
    if status_code == 201:
        print(f"✅ 배치 전송 성공: {len(response)}개 예측 생성됨")
    else:
        print(f"❌ 배치 전송 실패: {status_code} - {response}")
```

## 🛠️ 문제 해결

### 1. Tensor 직렬화 오류
```
TypeError: Object of type Tensor is not JSON serializable
```

**해결방법**: `convert_tensor_to_float()` 함수 사용
```python
from data_converter import convert_tensor_to_float

# Tensor를 float로 변환
confidence = convert_tensor_to_float(pred.confidence)
```

### 2. API 스키마 검증 오류
```
Field required: input_uri
String should match pattern "^(normal|warning|fall)$"
```

**해결방법**: `convert_yolo_output_to_api_format()` 함수 사용
```python
# 자동으로 모든 변환 수행
api_data = convert_yolo_output_to_api_format(...)
```

### 3. 타임스탬프 형식 오류
```
Input should be a valid integer, got a number with a fractional part
```

**해결방법**: 자동으로 정수로 변환됨
```python
# 부동소수점 타임스탬프도 자동으로 정수로 변환
ts_rel_ms = time.time() * 1000  # 1758283984550.982
# 변환 후: 1758283984550
```

## 📊 성능 최적화

### 1. 배치 처리
- 단일 예측보다 배치 처리가 효율적
- 권장 배치 크기: 5-10개

### 2. 비동기 처리
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_batch_send(predictions, client):
    """비동기 배치 전송"""
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        batch_data = convert_batch_frame_predictions(predictions)
        status_code, response = await loop.run_in_executor(
            executor, 
            lambda: client.post("/frame-predictions/batch", json=batch_data)
        )
        return status_code, response
```

### 3. 오류 처리 및 재시도
```python
import time
from requests.exceptions import RequestException

def send_with_retry(client, data, max_retries=3):
    """재시도 로직이 포함된 전송"""
    for attempt in range(max_retries):
        try:
            status_code, response = client.post("/frame-predictions", json=data)
            if status_code == 201:
                return status_code, response
        except RequestException as e:
            print(f"시도 {attempt + 1} 실패: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 지수 백오프
    return None, None
```

## 🔍 디버깅

### 1. 데이터 변환 확인
```python
from data_converter import validate_api_data

# 변환된 데이터 유효성 검사
errors = validate_api_data(api_data)
if errors:
    print("유효성 검사 오류:")
    for error in errors:
        print(f"  - {error}")
```

### 2. API 응답 확인
```python
status_code, response = client.post("/frame-predictions", json=api_data)
print(f"상태 코드: {status_code}")
print(f"응답: {response}")
```

### 3. 로깅 설정
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API 호출 로깅
logger.info(f"API 전송: {len(predictions)}개 예측")
logger.info(f"응답: {status_code} - {response}")
```

## 📚 추가 리소스

- **API 문서**: `server/app_server/docs/apis/frame_predictions_api.md`
- **예제 코드**: `yolo_api_integration_example.py`
- **데이터 변환**: `data_converter.py`
- **공통 클라이언트**: `common_api.py`

