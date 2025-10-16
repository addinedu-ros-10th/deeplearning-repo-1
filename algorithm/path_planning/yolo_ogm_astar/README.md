# 🧭 YOLO-OGM-A* Path-Planning
이 폴더는 "PersonA" 프로젝트의 Path Planning 부분으로,
실내 환경 내 장애물 회피 및 이동 경로 생성 연구를 위한 데모 코드로 구성되어 있다.


### 📄 Overview
YOLO 객체 인식 결과를 기반으로 Occupancy Grid Map(OGM)을 생성하고,
A* 알고리즘을 이용해 출발점(방문)에서 도착점(화장실문)까지의 최적 경로를 계산하는 프로젝트이다.

> 천장 4대 카메라(Web cam, ESP32 등)로부터 얻은 영상 프레임을 기반으로 하며,
**multiview_calib** 툴을 이용해 각 카메라의 **내/외부 파라미터를 보정** 한 후
YOLO 객체 인식 결과를 실제 바닥 좌표계를 투영(homography 변환)하여
실내 장애물 분포를 OGM(Occupancy Grid Map) 형태로 표현한다.

---

### ⚙️ Core Pipeline
1️⃣ Frame Input
    - 입력 : Test_frames/TCxx/frame_####.jpg
    - 출력 : 각 프레임별 homography 변환 좌표

2️⃣ YOLO Object Detection
    - 입력 : 원본 프레임
    - 출력 : 객체 감지 결과 (class, bbox 좌표)

3️⃣ World Coordinate Projection
    - 입력 : YOLO bbox + camera calibration
    - 출력 : 실세계 바닥 좌표 (mm 단위)

4️⃣ OGM Generation
    - 입력 : 장애물 world 좌표
    - 출력 : 2D occupancy grid (nmpy array or image)

5️⃣ Path Planning (A*)
    - 입력 : grid map + start/end points
    - 출력 : 최단 경로 좌표 및 시각화 이미지

---

### 🧩 Folder Structure
```
algorithm/path_planning/yolo_ogm_astar
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

### 📦 Requirements
```
imageio==2.37.0
matplotlib==3.10.6
numpy==2.2.6
opencv-python==4.12.0.88
scipy==1.16.2
ultralytics (YOLOv10)
```

### 🚀 실행 예시
```
# Test Case 01 실행
python pathplanning/pathplanning_final_TC01.py

# 결과 확인
open PathPlanning_outputs/TC01_outputs/path_outputs/final_astar_result.png
```