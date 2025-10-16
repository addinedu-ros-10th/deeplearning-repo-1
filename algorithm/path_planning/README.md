# 🗺️ A* Path Planning Algorithm Branch

## 📋 개요

이 브랜치는 **노인공경 (R.F.T.E) 스마트 케어 하우스 프로젝트**의 **실내 이동 경로 계획 데모**를 다룹니다.
멀티카메라 캘리브레이션 결과 (내/외부 파라미터, homography)를 이용해 **YOLO 객체 탐지 결과를 바닥 평면(world floor plane)으로 투영**하고,
이를 **2D 점유 격자 맵(OGM)**으로 만들어 **A\* 알고리즘**으로 **방문(시작) -> 화장실문(목표)** 경로를 계산합니다.

---

## 🎯 주요 기능

### 🤖 환경 인식
- **YOLO 객체 탐지 (YOLOv10)** : 각 카메라 프레임에서 객체의 바운딩박스 감지
- **바닥 평면 투영(Homography 변환)** : 멀티카메라 캘리브레이션으로 얻은 homography 행렬을 이용해, 감지된 **bbox 하단 중심점**을 **월드 좌표(mm)**로 변환
- **2D Occupancy Grid Map (OGM) 생성** : 변환된 월드 좌표를 **격자 공간(Grid)**에 투영하여 다음과 같이 표현함
  - 장애물 (Occupied) = 1
  - 빈공간 (Free) = 0
  - "내부 `matrix`는 True = Free, False = Obstacle을 사용하지만, 저장/시각화 시 OGM 스펙(Free=0, Occ=1)으로 변환한다."

### 🗺️ 경로 계획 (Path Planning)
- **A \* 알고리즘**: 2D Occupancy Grid Map 상에서 **최단 경로 탐색** 수행
- **고정 출/도착점** :
  - **시작(Start)** : 방문 (거실 문 근처)
  - **목표(Goal)**  : 화장실 문
- **결과 시각화** :
  - 경로 탐색 결과를 `PathPlanning_outputs/TCxx_outputs/` 경로에 **이미지(final_astar_result.png)** 로 저장
  - CSV/JSON 파일(`final_path.csv`,`final_path.json`)로도 경로 좌표 기록


## 🏗️ 아키텍처

```
algorithm/path_planning/multi_camera_calibration
├── calibration_retouch/           # intrinsics와 extrinsics 해상도 차이 보정
│   ├── intrinsics_rescaled.py     # intrinsics와 extrinsics의 해상도 차이를 보정하기 위한 rescale 스크립트
│   ├── landmarks_global_01.py
│   └── landmarks_rescaled.py
├── frames/                        # intrinsics에 사용된 frames
│   ├── cam51_up
│   ├── cam52_up
│   ├── cam53_up
│   └── cam54_up
├── input_files/                   # multiview_calib용 설정 파일들
│   ├── ba_config.json
│   ├── filenames.json
│   ├── intrinsics_scaled.json     # intrinsics.json에 calibration_retouch 적용한 버전
│   ├── intrinsics.json
│   ├── landmarks_global.json
│   ├── landmarks_scaled.json      # landmarks.json에 calibration_retouch 적용한 버전
│   ├── landmarks.json
│   └── setup.json
├── intrinsics_outputs/            # intrinsics 결과물
│   ├── output_51_update
│   ├── output_52_update
│   ├── output_53_update
│   └── output_54_update
├── outputs/                       # extrinsics 및 bundle adjustment 결과물
│   ├── bundle_adjustment
│   ├── global_registration        #bundle adjustment 이후 Umeyama alignment를 통해 mm 단위 전역 정합 수행 결과
│   └── relative_poses
├── videos/                        # calibration용 영상 및 frame 단위 추출본
│   ├── frames
│   ├── 51_videos.webm
│   ├── 52_videos.webm
│   ├── 53_videos.webm
│   └── 54_videos.webm
├── landmarks_click.ipynb/        # multiview_calib의 landmark 클릭 기능을 Jupyter 환경에서 실행 가능하도록 수정한 노트북
├── pathplanning/                           # YOLO + OGM + A* 알고리즘 핵심 코드
│   ├── pathplanning_final.py               # 전체 파이프라인 통합 코드
│   ├── pathplanning_final_TC01.py          # Test Case 01 적용 코드
│   ├── pathplanning_final_TC02.py          # Test Case 02 적용 코드
│   └── pathplanning_final_TC03.py          # Test Case 03 적용 코드
├── PathPlanning_outputs/                   # YOLO + Homography + A* 출력 결과물
│   ├── TC01_outputs
│   ├── TC02_outputs
│   └── TC03_outputs
└── Test_frames/                            # Test Case별 입력 프레임 데이터
    ├── TC01
    ├── TC02
    ├── TC03
    └── TC04
```
> **참고** : `multiview_calib` 코드는 포함하지 않으며, 별도 저장소를 통해 참조합니다. (`multi_camera_calibration/README.md`)



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
```
python pathplanning/pathplanning_final.py
```
- 이 스크립트는 **저장된 프레임**을 입력 받아, YOLO 감지 -> 바닥 평면 투영(homography) -> 2D OGM 생성 -> A* 경로 계산 -> 결과 시각화를 수행합니다.
- 실시간(웹캠/RTSP) 처리, 동적 재계획, 다중 목표점은 현재 범위에 포함되지 않습니다.

---

## 🔧 핵심 구성 요소

### 1. A* 경로 계획
- 입력 : 2D OGM (장애물 = 1, 빈공간 = 0), start/goal (world -> grid 변환)
- 휴리스틱 : Octile distance (8방향 이동 고려)
- 출력 : grid 경로 + world 좌표 경로, 시각화 이미지

### 2. YOLO 감지
- 프레임 단위 객체 감지
- 바운딩박스 하단 중앙점을 **바닥 평면 homography**로 world 좌표로 투영
- 클래스 필터 (사람/가구 등)는 스크립트 내 파라미터로 제어

### 3. OGM 생성
- world 좌표 -> 격자화 (기본 셀 크기 : 450mm)


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

- [multiview_calib](https://github.com/cvlab-epfl/multiview_calib)
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
