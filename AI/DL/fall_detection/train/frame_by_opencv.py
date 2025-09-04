# -*- coding: utf-8 -*-
"""
낙상감지 데이터 파이프라인 1단계 (+YOLO 탐지 시각화)
- 입력: 웹캠(0/None=자동) 또는 파일 경로
- 출력: 콘솔 로그 + CSV(frames_log_YYYYMMDD_HHMMSS_UUID.csv) + 미리보기 창(옵션)
"""
import cv2
import os
import platform
import glob
from datetime import timedelta

# 내부 모듈 (상대 임포트)
from ..util.csv_logger import setup_csv_logger
from ..infer.yolo_detector import YoloDetector  # ★ 새로 추가

def get_default_camera_source():
    system_name = platform.system()
    if system_name == "Linux":
        devices = sorted(glob.glob("/dev/video*"))
        if devices:
            print(f"[정보] Linux 카메라 장치 감지: {devices}")
            return int(devices[0].replace("/dev/video", ""))
        print("[경고] Linux에서 카메라 장치를 찾지 못했습니다.")
        return None
    elif system_name in ["Windows", "Darwin"]:
        return 0
    else:
        print(f"[경고] 지원하지 않는 OS: {system_name}")
        return None

def open_capture(source=None):
    if source is None:
        source = get_default_camera_source()
        if source is None:
            print("[에러] 기본 카메라 소스를 찾지 못했습니다.")
            return None
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[에러] 비디오 소스를 열 수 없습니다: {source}")
        return None
    return cap

def read_video_properties(cap):
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return fps, frame_count, width, height

def ms_to_hhmmss(ms_float):
    td_sec = (ms_float or 0.0) / 1000.0
    hours = int(td_sec // 3600)
    minutes = int((td_sec % 3600) // 60)
    seconds = td_sec % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def draw_detections(frame_bgr, detections, show_score=True):
    """
    YOLO 탐지 결과를 프레임 위에 그리기
    - detections: List[Detection]
    """
    for det in detections:
        cv2.rectangle(frame_bgr, (det.x1, det.y1), (det.x2, det.y2), (0, 255, 0), 2)
        label = det.cls_name
        if show_score:
            label += f" {det.conf:.2f}"
        cv2.putText(frame_bgr, label, (det.x1, max(det.y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
    return frame_bgr

def ensure_folder(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def process_stream(source=0, show_preview=True, write_csv=True,
                   folder="./log", every_n=1,
                   yolo_model="yolov8n.pt", yolo_device=None,
                   yolo_conf=0.25, yolo_classes=None):
    """
    메인 루프:
    - 프레임 메타 로깅 + YOLO 탐지 시각화
    - yolo_* 인자로 모델/디바이스/임계값/필터 클래스 제어
    """
    ensure_folder(folder)

    # 1) 캡처
    cap = open_capture(source)
    if cap is None:
        return

    fps, frame_count, width, height = read_video_properties(cap)
    print("=== 비디오 속성 ===")
    print(f"소스: {source}")
    print(f"해상도: {width}x{height}")
    print(f"FPS(메타): {fps:.3f} | 총 프레임수: {frame_count if frame_count>0 else '알 수 없음'}")
    print("====================")

    # 2) YOLO 로더
    try:
        detector = YoloDetector(model_path=yolo_model,
                                device=yolo_device,
                                conf_thres=yolo_conf,
                                classes=yolo_classes)
        print(f"[정보] YOLO 모델 로드 완료: {yolo_model}")
    except Exception as e:
        print(f"[경고] YOLO 초기화 실패: {e}")
        detector = None

    # 3) CSV 로거
    csv_writer = None
    csv_file = None
    if write_csv:
        csv_writer, csv_file, csv_path = setup_csv_logger(
            base_name="frames_log", ext="csv", folder=folder
        )
        # 헤더 확장: 탐지 개수 열 추가
        # (setup_csv_logger가 기본 헤더를 already write 하므로, 여기선 필요 시 확장만)
        # 간단하게는 첫 데이터 기록 시 detection_count를 포함해 일관된 열 순서 유지
        print(f"[정보] CSV 로깅: {csv_path}")

    frame_idx = 0
    try:
        while True:
            read_ok, frame_bgr = cap.read()
            pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)  # 파일이면 정확 / 웹캠은 대략
            pos_hhmmss = ms_to_hhmmss(pos_msec)

            detections = []
            if detector is not None and read_ok:
                detections = detector.detect(frame_bgr)

            # 샘플링 로그/CSV
            if frame_idx % every_n == 0:
                print(f"[프레임 {frame_idx:6d}] ok={read_ok} t={pos_hhmmss} ms={pos_msec:.1f} "
                      f"| size={width}x{height} | det={len(detections)}")
                if write_csv and csv_writer is not None:
                    # 기본 헤더 순서를 유지하고 마지막에 detection_count 추가
                    csv_writer.writerow([
                        frame_idx, f"{pos_msec:.3f}", pos_hhmmss,
                        f"{fps:.3f}", width, height, int(read_ok),
                        len(detections)  # 추가 열
                    ])

            if not read_ok:
                print("[정보] EOF/읽기 실패. 종료합니다.")
                break

            # 시각화: 프레임 오버레이 (인덱스/타임 + YOLO 박스)
            overlay = frame_bgr
            overlay = draw_detections(overlay, detections, show_score=True)
            if show_preview:
                info = f"idx:{frame_idx} t:{pos_hhmmss} ({pos_msec:.1f}ms)"
                cv2.putText(overlay, info, (12, 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.imshow("preview - YOLO (q: quit)", overlay)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[정보] 사용자가 종료(q)했습니다.")
                    break

            frame_idx += 1

    finally:
        cap.release()
        if show_preview:
            cv2.destroyAllWindows()
        if csv_file is not None:
            csv_file.close()
        print("[완료] 캡처/탐지/로깅 종료")


if __name__ == "__main__":
    """
    실행 예시 (AI 디렉터리에서):
      1) 웹캠 자동감지: python -m DL.fall_detection.train.frame_by_opencv
      2) 파일 입력:   python -m DL.fall_detection.train.frame_by_opencv --source "/path/video.mp4"
      3) person만 탐지: --yolo-classes 0
      4) 다른 가중치:  --yolo-model "yolov8s.pt"
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default=None, help="0/None=웹캠 자동, 파일 경로 가능")
    parser.add_argument("--show-preview", action="store_true", default=True)
    parser.add_argument("--no-preview", dest="show_preview", action="store_false")
    parser.add_argument("--no-csv", dest="write_csv", action="store_false")
    parser.add_argument("--logdir", type=str, default="DL/fall_detection/train/log")
    parser.add_argument("--every-n", type=int, default=1)

    parser.add_argument("--yolo-model", type=str, default="yolov8n.pt")
    parser.add_argument("--yolo-device", type=str, default=None, help="cuda / cpu / None(auto)")
    parser.add_argument("--yolo-conf", type=float, default=0.25)
    parser.add_argument("--yolo-classes", type=int, nargs="*", default=None, help="예: 0(person)만")

    args = parser.parse_args()

    # source 해석: None이면 자동, 숫자 문자열이면 int로 변환
    src = None
    if args.source is None:
        src = None  # 자동
    else:
        if args.source.isdigit():
            src = int(args.source)
        else:
            src = args.source

    process_stream(
        source=src,
        show_preview=args.show_preview,
        write_csv=args.write_csv,
        folder=args.logdir,
        every_n=args.every_n,
        yolo_model=args.yolo_model,
        yolo_device=args.yolo_device,
        yolo_conf=args.yolo_conf,
        yolo_classes=args.yolo_classes
    )
