# API 사용 예제 모음

이 디렉토리는 `common_api.py`를 사용하여 ML Registry API를 호출하는 다양한 예제들을 포함합니다.

## 📁 파일 구조

```
Util/examples/
├── README.md                           # 이 파일
├── dataset_api_example.py              # 데이터셋 API 예제
├── experiment_api_example.py           # 실험 API 예제
├── frame_prediction_api_example.py     # 프레임 예측 API 예제
└── detection_event_api_example.py      # 감지 이벤트 API 예제
```

## 🚀 사용 방법

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install requests

# 예제 디렉토리로 이동
cd Util/examples
```

### 2. 기본 실행

```bash
# 로컬 환경에서 실행 (기본값)
python dataset_api_example.py
python experiment_api_example.py
python frame_prediction_api_example.py
python detection_event_api_example.py
```

### 3. 환경별 실행

```bash
# 운영 환경에서 실행
python dataset_api_example.py --env prod
python experiment_api_example.py --env prod

# 커스텀 URL로 실행
python dataset_api_example.py --base-url http://custom-host:8000
```

### 4. 옵션 설정

```bash
# 삭제 예제 건너뛰기
python dataset_api_example.py --skip-delete

# 특정 실험 ID 사용 (프레임 예측, 감지 이벤트)
python frame_prediction_api_example.py --experiment-id <EXPERIMENT_ID>
python detection_event_api_example.py --experiment-id <EXPERIMENT_ID>
```

## 📋 각 예제별 기능

### 1. 데이터셋 API 예제 (`dataset_api_example.py`)

- ✅ 데이터셋 생성
- ✅ 데이터셋 목록 조회
- ✅ 특정 데이터셋 조회
- ✅ 이름으로 데이터셋 검색
- ✅ 태그로 데이터셋 검색
- ✅ 데이터셋 업데이트
- ✅ 데이터셋 삭제

### 2. 실험 API 예제 (`experiment_api_example.py`)

- ✅ 실험 생성
- ✅ 실험 목록 조회
- ✅ 특정 실험 조회
- ✅ 실험 업데이트
- ✅ 실험 삭제

### 3. 프레임 예측 API 예제 (`frame_prediction_api_example.py`)

- ✅ 프레임 예측 생성 (단건)
- ✅ 프레임 예측 생성 (배치)
- ✅ 프레임 예측 목록 조회
- ✅ 특정 프레임 예측 조회
- ✅ 프레임 예측 업데이트
- ✅ 프레임 예측 삭제

### 4. 감지 이벤트 API 예제 (`detection_event_api_example.py`)

- ✅ 감지 이벤트 생성 (단건)
- ✅ 여러 감지 이벤트 생성
- ✅ 감지 이벤트 목록 조회
- ✅ 특정 감지 이벤트 조회
- ✅ 이벤트 타입으로 필터링
- ✅ 감지 이벤트 업데이트
- ✅ 감지 이벤트 삭제

## 🔧 공통 기능

### 환경 설정

- **로컬 환경**: `http://localhost:8000`
- **운영 환경**: `http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com`
- **커스텀 URL**: `--base-url` 옵션으로 지정

### 에러 처리

- 네트워크 오류 시 자동 재시도 (2회)
- 타임아웃 설정 (30초)
- 상세한 오류 메시지 출력

### 로깅

- 요청/응답 데이터 JSON 형태로 출력
- 상태 코드 및 성공/실패 메시지 표시
- 실행 시간 및 환경 정보 표시

## 📝 사용 예시

### 전체 워크플로우 예제

```bash
# 1. 데이터셋 생성
python dataset_api_example.py --skip-delete

# 2. 실험 생성 (위에서 생성된 데이터셋 ID 사용)
python experiment_api_example.py --skip-delete

# 3. 프레임 예측 생성 (위에서 생성된 실험 ID 사용)
python frame_prediction_api_example.py --experiment-id <EXPERIMENT_ID> --skip-delete

# 4. 감지 이벤트 생성 (위에서 생성된 실험 ID 사용)
python detection_event_api_example.py --experiment-id <EXPERIMENT_ID> --skip-delete
```

### 운영 환경 테스트

```bash
# 운영 환경에서 모든 API 테스트
python dataset_api_example.py --env prod --skip-delete
python experiment_api_example.py --env prod --skip-delete
python frame_prediction_api_example.py --env prod --experiment-id <EXPERIMENT_ID> --skip-delete
python detection_event_api_example.py --env prod --experiment-id <EXPERIMENT_ID> --skip-delete
```

## 🛠️ 문제 해결

### 1. 연결 오류

```
❌ 오류 발생: Connection refused
API 서버가 실행 중인지 확인하세요.
```

**해결 방법:**
- API 서버가 실행 중인지 확인
- 올바른 URL과 포트 사용
- 방화벽 설정 확인

### 2. 인증 오류

```
❌ 실험 생성 실패: 401
```

**해결 방법:**
- 인증 토큰이 필요한 경우 헤더에 추가
- API 서버의 인증 설정 확인

### 3. 데이터 오류

```
❌ 데이터셋 생성 실패: 400
```

**해결 방법:**
- 요청 데이터 형식 확인
- 필수 필드 누락 여부 확인
- 데이터 타입 및 값 검증

## 🎥 ESP32 영상 스트림 테스트

ESP32에서 송출하는 영상 스트림을 테스트하고 모니터링할 수 있는 도구가 추가되었습니다.

### 기본 사용법
```bash
# ESP32 스트림 연결 테스트
python3 esp32_stream_test.py

# 스트림 품질 테스트 (10초)
python3 esp32_stream_test.py --test-quality 10

# 프레임 캡처 (5개 프레임)
python3 esp32_stream_test.py --capture-frames --max-frames 5

# 실시간 모니터링 (30초)
python3 esp32_stream_test.py --monitor 30
```

### 주요 기능
- ✅ **연결 테스트**: ESP32와의 네트워크 연결 상태 확인
- ✅ **품질 측정**: 실제 FPS, 해상도, 프레임 손실률 측정
- ✅ **프레임 캡처**: 스트림에서 이미지 프레임 저장
- ✅ **실시간 모니터링**: OpenCV 창에서 실시간 스트림 확인
- ✅ **네트워크 진단**: TCP/HTTP 연결 상태 진단

자세한 사용법은 `../ESP32_STREAM_GUIDE.md`를 참조하세요.

## 📚 추가 정보

- **API 문서**: `server/app_server/docs/apis/` 디렉토리 참조
- **공통 클라이언트**: `../common_api.py` 파일 참조
- **ESP32 스트림 가이드**: `../ESP32_STREAM_GUIDE.md` 파일 참조
- **서버 설정**: `server/app_server/` 디렉토리 참조

## 🤝 기여하기

새로운 예제나 개선사항이 있다면 언제든지 기여해주세요!

1. 새로운 예제 파일 생성
2. 기존 예제 개선
3. 문서 업데이트
4. 버그 리포트 및 수정
