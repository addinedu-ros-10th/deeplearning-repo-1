# 🗺️ A* Path Planning Algorithm Branch

## 📋 개요

이 브랜치는 **노인공경 (R.F.T.E) 스마트 케어 하우스 프로젝트**의 자율 주행 시스템을 위한 A* 경로 계획 알고리즘 구현을 담당합니다. YOLO 객체 탐지와 점유 격자 맵(Occupancy Grid Map)을 통합하여 실시간 경로 계획을 수행합니다.

## 🎯 주요 기능

### 🤖 AI 기반 환경 인식
- **YOLO 객체 탐지**: 실시간 장애물 탐지 및 분류
- **점유 격자 맵**: 2D/3D 공간 정보 표현
- **동적 장애물 처리**: 움직이는 객체에 대한 실시간 대응

### 🗺️ 경로 계획 알고리즘
- **A* 알고리즘**: 최적 경로 탐색
- **다중 목표점 지원**: 여러 목적지를 고려한 경로 계획
- **실시간 재계획**: 환경 변화에 따른 동적 경로 수정

### 📷 다중 카메라 시스템
- **카메라 보정**: 내부/외부 파라미터 자동 보정
- **다중 뷰 통합**: 여러 카메라 정보 융합
- **Bundle Adjustment**: 정밀한 포즈 추정

## 🏗️ 아키텍처

```
algorithm/path_planning/
├── core/                           # 핵심 알고리즘
│   ├── a_star.py                   # A* 경로 계획 알고리즘
│   ├── occupancy_grid.py          # 점유 격자 맵 처리
│   └── path_optimizer.py          # 경로 최적화
├── vision/                         # 컴퓨터 비전 모듈
│   ├── yolo_detector.py           # YOLO 객체 탐지
│   ├── camera_calibration.py      # 카메라 보정
│   └── spatial_mapper.py          # 공간 매핑
├── integration/                    # 통합 모듈
│   ├── yolo_ogm_integration.py    # YOLO-OGM 통합
│   ├── multi_camera_fusion.py     # 다중 카메라 융합
│   └── real_time_planner.py       # 실시간 계획기
├── utils/                          # 유틸리티
│   ├── geometry_utils.py          # 기하학적 계산
│   ├── visualization.py           # 시각화 도구
│   └── config.py                  # 설정 관리
├── tests/                          # 테스트
│   ├── test_a_star.py             # A* 알고리즘 테스트
│   ├── test_yolo_integration.py   # YOLO 통합 테스트
│   └── test_multi_camera.py      # 다중 카메라 테스트
├── examples/                       # 예제
│   ├── basic_path_planning.py     # 기본 경로 계획 예제
│   ├── yolo_integration_demo.py   # YOLO 통합 데모
│   └── multi_camera_demo.py      # 다중 카메라 데모
└── docs/                          # 문서
    ├── algorithm_design.md         # 알고리즘 설계 문서
    ├── api_reference.md           # API 참조
    └── integration_guide.md       # 통합 가이드
```

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv/path_planning
source venv/path_planning/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 기본 사용법
```python
from algorithm.path_planning.core.a_star import AStarPlanner
from algorithm.path_planning.vision.yolo_detector import YOLODetector
from algorithm.path_planning.integration.real_time_planner import RealTimePlanner

# YOLO 탐지기 초기화
detector = YOLODetector(model_path="yolo11n.pt")

# A* 계획기 초기화
planner = AStarPlanner(grid_size=0.1, heuristic_weight=1.0)

# 실시간 계획기 초기화
rt_planner = RealTimePlanner(detector, planner)

# 경로 계획 실행
start = (0, 0)
goal = (10, 10)
path = rt_planner.plan_path(start, goal)
```

### 3. 다중 카메라 설정
```python
from algorithm.path_planning.vision.camera_calibration import MultiCameraCalibrator

# 다중 카메라 보정
calibrator = MultiCameraCalibrator()
calibrator.calibrate_cameras(camera_configs)
```

## 🔧 핵심 구성 요소

### 1. A* 알고리즘 (`a_star.py`)
- **휴리스틱 함수**: 유클리드 거리 기반
- **비용 함수**: 거리 + 장애물 회피 비용
- **동적 재계획**: 환경 변화 감지 시 자동 재계획

### 2. YOLO 통합 (`yolo_detector.py`)
- **실시간 탐지**: 30fps 이상 처리 성능
- **클래스 필터링**: 사람, 가구, 장애물 등 분류
- **신뢰도 임계값**: 탐지 정확도 조절

### 3. 점유 격자 맵 (`occupancy_grid.py`)
- **해상도**: 0.1m 격자 크기
- **확률적 업데이트**: 베이지안 필터링
- **동적 업데이트**: 실시간 환경 변화 반영

### 4. 다중 카메라 융합 (`multi_camera_fusion.py`)
- **시점 통합**: 여러 카메라 정보 융합
- **깊이 추정**: 스테레오 비전 기반
- **3D 매핑**: 점유 격자 맵 3D 확장

## 📊 성능 지표

### 🎯 정확도
- **경로 최적성**: 최적 경로 대비 95% 이상
- **탐지 정확도**: YOLO mAP@0.5 > 0.8
- **재계획 속도**: < 100ms

### ⚡ 속도
- **계획 시간**: 평균 50ms
- **탐지 속도**: 30fps
- **메모리 사용량**: < 2GB

### 🔄 실시간성
- **지연 시간**: < 200ms
- **프레임 드롭**: < 5%
- **CPU 사용률**: < 80%

## 🧪 테스트

### 단위 테스트
```bash
# A* 알고리즘 테스트
python -m pytest tests/test_a_star.py -v

# YOLO 통합 테스트
python -m pytest tests/test_yolo_integration.py -v

# 다중 카메라 테스트
python -m pytest tests/test_multi_camera.py -v
```

### 통합 테스트
```bash
# 전체 시스템 테스트
python -m pytest tests/ -v --cov=algorithm.path_planning
```

### 성능 테스트
```bash
# 성능 벤치마크
python examples/performance_benchmark.py
```

## 📈 사용 예제

### 1. 기본 경로 계획
```python
# 단순한 A* 경로 계획
from algorithm.path_planning.core.a_star import AStarPlanner

planner = AStarPlanner()
path = planner.find_path(start=(0, 0), goal=(10, 10), obstacles=[])
print(f"계획된 경로: {path}")
```

### 2. YOLO 통합 경로 계획
```python
# YOLO와 통합된 실시간 경로 계획
from algorithm.path_planning.integration.real_time_planner import RealTimePlanner

planner = RealTimePlanner()
planner.start_planning(camera_source=0)  # 웹캠 사용
```

### 3. 다중 카메라 시스템
```python
# 다중 카메라 환경에서의 경로 계획
from algorithm.path_planning.vision.multi_camera_fusion import MultiCameraFusion

fusion = MultiCameraFusion(camera_configs)
fusion.start_fusion()
```

## 🔧 설정

### 환경 변수
```bash
# YOLO 모델 경로
export YOLO_MODEL_PATH="models/yolo11n.pt"

# 카메라 설정
export CAMERA_WIDTH=640
export CAMERA_HEIGHT=480

# 계획 설정
export GRID_SIZE=0.1
export HEURISTIC_WEIGHT=1.0
```

### 설정 파일 (`config.yaml`)
```yaml
# A* 알고리즘 설정
a_star:
  grid_size: 0.1
  heuristic_weight: 1.0
  max_iterations: 10000

# YOLO 설정
yolo:
  model_path: "models/yolo11n.pt"
  confidence_threshold: 0.5
  nms_threshold: 0.4

# 카메라 설정
cameras:
  - id: 0
    width: 640
    height: 480
    fps: 30
  - id: 1
    width: 640
    height: 480
    fps: 30
```

## 🐛 문제 해결

### 일반적인 문제들

1. **YOLO 모델 로딩 실패**
   ```bash
   # 모델 파일 확인
   ls -la models/
   # 모델 다운로드
   python scripts/download_models.py
   ```

2. **카메라 접근 권한 문제**
   ```bash
   # 카메라 권한 확인
   ls -la /dev/video*
   # 사용자 그룹 추가
   sudo usermod -a -G video $USER
   ```

3. **메모리 부족**
   ```python
   # 배치 크기 조정
   detector = YOLODetector(batch_size=1)
   ```

## 📚 참고 자료

- [A* 알고리즘 위키](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [YOLO 논문](https://arxiv.org/abs/1506.02640)
- [점유 격자 맵](https://en.wikipedia.org/wiki/Occupancy_grid_mapping)
- [다중 카메라 보정](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)

## 🤝 기여 방법

1. **이슈 생성**: 버그 리포트 또는 기능 제안
2. **브랜치 생성**: `feat/path-planning--기능명` 형식
3. **코드 작성**: 기존 아키텍처 패턴 준수
4. **테스트**: 단위 테스트 및 통합 테스트 작성
5. **PR 생성**: 상세한 변경사항 설명 포함

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**노인공경 (R.F.T.E)** - Respect For The Elderly

> 이 모듈은 독거노인을 위한 스마트 케어 하우스의 자율 주행 시스템을 지원합니다.
