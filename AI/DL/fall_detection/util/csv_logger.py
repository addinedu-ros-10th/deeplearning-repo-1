import csv
import os
import uuid
from datetime import datetime

def make_logfile_path(base_name="frames_log", ext="csv", folder="."):
    """
    로그 파일 경로를 날짜+UUID suffix로 생성합니다.
    예: frames_log_20250904_193012_ab12cd34.csv
    """
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid_str = str(uuid.uuid4())[:8]  # UUID4 앞 8자리만 사용
    filename = f"{base_name}_{now_str}_{uid_str}.{ext}"
    return os.path.join(folder, filename)

def setup_csv_logger(base_name="frames_log", ext="csv", folder="."):
    """
    새로운 CSV 로그 파일을 생성하고, writer 객체를 반환합니다.
    """
    csv_path = make_logfile_path(base_name, ext, folder)
    csv_file = open(csv_path, mode="w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)

    # 헤더 기록
    csv_writer.writerow([
        "frame_index", "pos_msec", "pos_hhmmss", "fps_meta",
        "width", "height", "read_ok"
    ])
    print(f"[정보] 새로운 로그 파일 생성됨: {csv_path}")
    return csv_writer, csv_file, csv_path

# === 사용 예시 ===
if __name__ == "__main__":
    # CSV 로거 초기화
    writer, file, path = setup_csv_logger()

    # 샘플 데이터 기록
    writer.writerow([0, "0.0", "00:00:00.000", "30.0", 640, 480, 1])
    writer.writerow([1, "33.3", "00:00:00.033", "30.0", 640, 480, 1])

    # 파일 닫기
    file.close()
