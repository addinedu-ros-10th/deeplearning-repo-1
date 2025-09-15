# AI/DL 모듈 개발 현황

## 📊 현재 상태

### ✅ 완료된 작업

#### 1. 데이터셋 구축
- **YOLO 데이터셋**: 낙상 감지를 위한 이미지 및 라벨 데이터 수집
  - `AI/DL/fall_dataset/yolo/images/`: 학습/검증 이미지
  - `AI/DL/fall_dataset/yolo/labels/`: YOLO 형식 라벨 파일
  - 테스트/검증 데이터셋 분리 완료

#### 2. 낙상 감지 모듈
- **YOLO 감지기**: `AI/DL/fall_detection/infer/yolo_detector.py`
  - 객체 감지 및 분류 기능
  - 실시간 비디오 처리 지원

#### 3. 데이터 처리 도구
- **프레임 추출**: `AI/DL/fall_detection/train/frame_by_opencv.py`
  - 비디오에서 프레임 추출
  - 학습 데이터 전처리

- **CSV 로거**: `AI/DL/fall_detection/util/csv_logger.py`
  - 데이터 로깅 및 분석
  - 프레임별 메타데이터 저장

#### 4. 포즈 추정 데이터
- **키포인트 데이터**: `AI/DL/yolo_detection_and_pose/coordinate/`
  - MediaPipe 포즈 추정 결과
  - 5개 키포인트 데이터셋 완성
  - CSV 형식으로 저장된 좌표 데이터

#### 5. 학습 데이터 관리
- **데이터셋 메타데이터**: 
  - `complete_list.csv`: 전체 데이터셋 목록
  - `extract_record.csv`: 추출 기록
  - `Fall Detectoin Training Data Set - 정규호.csv`: 학습 데이터셋

### 🔄 현재 진행 중

#### 1. YOLO 모델 학습
- 데이터셋 준비 완료
- 모델 학습 파이프라인 구축 중
- 하이퍼파라미터 튜닝 진행

#### 2. MediaPipe 통합
- 포즈 추정 모듈 개발
- 실시간 처리 최적화
- YOLO와의 통합 작업

### 📁 데이터 구조

```
AI/DL/
├── fall_dataset/
│   └── yolo/
│       ├── images/
│       │   ├── test/          # 테스트 이미지
│       │   └── val/           # 검증 이미지
│       └── labels/
│           ├── test/          # 테스트 라벨
│           └── val/           # 검증 라벨
├── fall_detection/
│   ├── infer/
│   │   └── yolo_detector.py   # YOLO 감지기
│   ├── train/
│   │   ├── frame_by_opencv.py # 프레임 추출
│   │   └── log/               # 학습 로그
│   └── util/
│       └── csv_logger.py      # 데이터 로거
├── yolo_detection_and_pose/
│   ├── coordinate/            # 포즈 키포인트 데이터
│   ├── images/               # 처리된 이미지
│   └── FY/                   # 원본 비디오 데이터
└── pyproject.toml            # 의존성 관리
```

### 🎯 다음 단계

#### 1. 모델 학습 완료
- YOLO 모델 학습 및 검증
- 성능 메트릭 평가
- 모델 최적화

#### 2. 실시간 처리 시스템
- 비디오 스트림 처리 파이프라인
- 낙상 감지 알고리즘 구현
- 실시간 알림 시스템

#### 3. Server 모듈과의 통합
- API 엔드포인트 개발
- 실시간 데이터 전송
- 결과 저장 및 관리

### 📊 데이터 현황

- **이미지 데이터**: 학습/검증용 이미지 수집 완료
- **라벨 데이터**: YOLO 형식 라벨링 완료
- **포즈 데이터**: 5개 키포인트 데이터셋 완성
- **비디오 데이터**: 원본 비디오 파일 보관 중

### 🔧 기술 스택

- **Python 3.12**
- **YOLO**: 객체 감지
- **MediaPipe**: 포즈 추정
- **OpenCV**: 비디오 처리
- **Pandas**: 데이터 처리
- **NumPy**: 수치 계산

### 📈 성능 목표

- **정확도**: 낙상 감지 정확도 > 90%
- **실시간성**: 30fps 비디오 스트림 처리
- **지연시간**: 감지 지연 < 100ms
- **안정성**: 24시간 연속 운영 가능

---

*최종 업데이트: 2025-09-13*


