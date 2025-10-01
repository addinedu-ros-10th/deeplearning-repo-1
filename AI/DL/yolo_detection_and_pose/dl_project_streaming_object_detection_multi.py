import cv2
from ultralytics import YOLO
import os

"""----------------------------- 비디오 폴더 경로 입력 --------------------------------"""

video_folder_path = "/home/dj/Videos/Screencasts/test/items_videos"
video_file_list = os.listdir(video_folder_path)
video_type = ".mp4"

video_save_path = os.path.join(video_folder_path, "dl_project_save")

start_number = 0

os.makedirs(video_save_path, exist_ok = True)
"""--------------------------------------------------------------------------------"""

model = YOLO("./runs/detect/json_ai_2057_5items_sdj_v1.0/weights/best.pt")
# model = YOLO("./runs/detect/json_ai_1046_5items_sdj_v2.0/weights/best.pt")
# model = YOLO("./runs/detect/json_ai_1046_5items_sdj_v1.0/weights/best.pt")

for video_idx in video_file_list:
    video_file_path = os.path.join(video_folder_path, video_idx)

    cap = cv2.VideoCapture(video_file_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    period = 1/fps

    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    save_file = video_save_path + "/" + video_idx.split(".")[0] + "_edit" + video_type

    cap_out = cv2.VideoWriter(save_file, fourcc, fps, (1280, 960))

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.resize(frame, (1280, 960))

        result = model(frame, classes = [0, 80, 81, 82, 83, 84], conf = 0.45)

        image = list(result)[0].plot()

        cap_out.write(image)

        cv2.imshow("test", image)

        key_input = cv2.waitKey(1)

        if key_input == ord('q') &0xff:
            break

    cap.release()
    cv2.destroyAllWindows()