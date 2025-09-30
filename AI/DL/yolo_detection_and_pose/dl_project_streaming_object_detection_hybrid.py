import cv2
from ultralytics import YOLO
import os

"""----------------------------- 비디오 폴더 경로 입력 --------------------------------"""

video_folder_path = "/home/dj/Videos/Screencasts"
video_file_list = os.listdir(video_folder_path)
video_type = ".mp4"

video_save_path = os.path.join(video_folder_path, "dl_project_save")

start_number = 0

os.makedirs(video_save_path, exist_ok = True)
"""--------------------------------------------------------------------------------"""

model1 = YOLO("./runs/detect/json_ai_1046_5items_sdj_v2.0/weights/best.pt")
model2 = YOLO("./runs/detect/json_ai_2057_5items_sdj_v1.0/weights/best.pt")

for video_idx in video_file_list:
    video_file_path = os.path.join(video_folder_path, video_idx)

    cap = cv2.VideoCapture(video_file_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    period = 1/fps

    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    save_file = video_save_path + "/" + str(start_number) + video_idx.split(".")[0] + "_edit" + video_type

    cap_out = cv2.VideoWriter(save_file, fourcc, fps, (1280, 960))

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        result = model1(frame, classes = [0, 82, 84], conf = 0.45)

        image = list(result)[0].plot()

        result2 = model2(frame, classes = [80, 81, 83], conf = 0.45)

        image2 = list(result2)[0].plot()

        image3 = cv2.addWeighted(image, 0.5, image2, 0.5, 0)
        
        image = list(result)[0].plot()

        cv2.imshow("test", image)

        cap_out.write(frame)

        key_input = cv2.waitKey(1)

        if key_input == ord('q') &0xff:
            break

    cap.release()
    cv2.destroyAllWindows()