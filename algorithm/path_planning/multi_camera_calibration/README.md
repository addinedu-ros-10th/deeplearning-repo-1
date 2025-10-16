# 🧭Multi-Camera Calibration
### 📄 Credits
- 해당 프로젝트에서 사용한 multi-camera calibration은 [multiview_calib](https://github.com/cvlab-epfl/multiview_calib)를 이용하였다.
- `multiview_calib`의 코드는 포함되어 있지 않으며, 아래의 Repository 주소를 통해 원본을 참고할 수 있다.


### 🧩 Original Repository
- Repository : [https://github.com/cvlab-epfl/multiview_calib](https://github.com/cvlab-epfl/multiview_calib)
- Author : Leonardo Citraro

---


### 🚀 Project Overview
> 본 폴더는 PersonA 프로젝트의 **멀티 카메라 캘리브레이션 파이프라인**을 구성하며,
4대의 천장 카메라 (Web Cam, ESP32-CAM 등)로부터 획득한 영상을 기반으로
**intrinsics (내부 파라미터)** 및 **extrinsics (외부 파라미터)** 를 계산한다.
계산된 결과는 이후 YOLO-OGM-A* 모듈에서 **실세계 바닥 좌표계 변환** 에 사용된다.


#### 🧩 Folder Structure
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
└── landmarks_click.ipynb/        # multiview_calib의 landmark 클릭 기능을 Jupyter 환경에서 실행 가능하도록 수정한 노트북
```