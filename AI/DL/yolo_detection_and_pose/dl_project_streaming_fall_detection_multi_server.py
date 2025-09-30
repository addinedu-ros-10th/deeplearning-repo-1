import cv2
import mediapipe as mp # 자세인식용 모듈
import numpy as np
import torch
from ultralytics import YOLO # 객체인식용 모듈
import ultralytics
import gc
import os
from notification_client import NotificationClient, NotificationSender
from datetime import datetime
from util import common_api
import time

ultralytics.checks()

"""
============================== 버튼 안내 ==============================
 * q : 종료
 * a : yolo 활성화 / 비활성화
"""

def standardize_data(data):

    mean = data.mean(axis = (1, 2), keepdims = True)

    std = data.std(axis = (1, 2), keepdims = True)

    standardized_data = (data - mean) / (std + 1e-8)

    return standardized_data

FALL_DETECTION_MESSAGE = "Fall detected."

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

"""=========================== 모듈 설정 ============================="""

model_path = "./dataN2_1321_ynb_sdj_v1.0.pt" # 학습모델 적용하는 위치
# model_path = "./dataN_635_yb_sdj_v1.3.pt" # 학습모델 적용하는 위치
# model_path = "./dataN_635_yb_sdj_v1.0.pt" # 학습모델 적용하는 위치
# model_path = "./data_511_380_yb_sdj_v1.3.pt" # 학습모델 적용하는 위치

video_output_code = ""


model = torch.jit.load(model_path)
model.eval()

labels_map = {0: "Normal", 1: "Warning", 2: "Fall"}

is_collecting = True
message_sent = False
fall_detection_count = 0
not_fall_count = 0

keypoints_list = []

items = []

session_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
# session_id = str(uuid.uuid4())
experiment_id = "12bd0c67-a10c-4e01-adec-871010e49031"

server_url = "http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com"
confidence_bool = False

"""----------------------------- 비디오 폴더 경로 입력 --------------------------------"""

video_folder_path = "/home/dj/Videos/Screencasts/test/mkv"
video_file_list = os.listdir(video_folder_path)
video_type = ".mp4"

video_save_path = os.path.join(video_folder_path, "dl_project_save")

start_number = 0

os.makedirs(video_save_path, exist_ok = True)
"""--------------------------------------------------------------------------------"""

for video_idx in video_file_list:
    video_file_path = os.path.join(video_folder_path, video_idx)

    url = video_file_path

    cap = cv2.VideoCapture(video_file_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    period = 1/fps

    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    save_file = video_save_path + "/" + str(start_number) + video_idx.split(".")[0] + "_edit" + video_type

    cap_out = cv2.VideoWriter(save_file, fourcc, fps, (1280, 960))

    while cap.isOpened():

        keypoints = []

        ret, frame = cap.read()

        if not ret:
            print("Cannot open video or video is terminated")
            break

        frame = cv2.resize(frame, (1280, 960)) # 이미지 사이즈 조정

        result = pose.process(frame)

        if result.pose_landmarks: #화면에 탐지되는 사람이 없을 경우 데이터가 누락되어 자세 그리기를 진행할 수 없음.

            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color = (255, 0, 0), thickness = 2),
                                    mp_drawing.DrawingSpec(color = (255, 255, 255), thickness = 2))
            
            kp = [[lmk.x, lmk.y, lmk.z] for lmk in result.pose_landmarks.landmark]

            for key in kp:
                for k in key:
                    keypoints.append(k)

            keypoints_list.append(keypoints)

            if keypoints_list:

                keypoints_array = np.array(keypoints_list)

                keypoints_standardized = standardize_data(np.expand_dims(keypoints_array, axis = 0))[0]

                input_data = torch.tensor(keypoints_standardized).float()
                input_data = input_data.view(1, keypoints_standardized.shape[0], -1)

                with torch.no_grad():
                    outputs = model(input_data)
                    probabilities = torch.softmax(outputs, dim = 1)

                    predicted_class = torch.argmax(probabilities, dim=1).item()

                    confidence = probabilities[0, predicted_class].item()

            predicted_label = labels_map[predicted_class]
            confidence_percent = confidence * 100
            cv2.putText(frame, f"Pred.: {predicted_label}, Conf.: {confidence_percent:.2f}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 64, 0), 2)

            cv2.putText(frame, "N: " + f"{round(float(probabilities[0][0]), 2)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 64, 64), 2)
            cv2.putText(frame, "W: " + f"{round(float(probabilities[0][1]), 2)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 64, 64), 2)
            cv2.putText(frame, "F: " + f"{round(float(probabilities[0][2]), 2)}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 64, 64), 2)
            
            if confidence > 0.6:
                confidence_bool = True
            else:
                confidence_bool = False

            item = {
                "session_id": session_id,
                "experiment_id": experiment_id,
                "input_uri": url,
                "frame_index": index_number,
                "probabilities": {
                    "normal": float(probabilities[0][0]),
                    "warning": float(probabilities[0][1]),
                    "fall": float(probabilities[0][2]),
                },
                "label_pred": predicted_label,
                "ts_rel_ms": int(time.time()),
                "confidence": confidence,
                "passed": confidence_bool,
                "threshold_name": "yolo_threshold",
                "threshold_snapshot": {
                    "threshold": 0.45
                }
            }

            items.append(item)
            index_number += 1
            print(len(items))
            """--------------------------------------------------- 넘어짐 알림 파트 ---------------------------------------------------"""
            if predicted_label == "Fall" and round(float(probabilities[0][2]), 2) > 0.6:
                fall_detection_count += 1

                # if fall_detection_count >= (fps):
                #     cv2.putText(frame, FALL_DETECTION_MESSAGE, (250, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 64, 64), 2)
                #     if message_sent == True:
                #         continue
                #     else:
                #         message_sent = True

            # else:
            #     not_fall_count += 1

            #     if not_fall_count >= (fps):
            #         not_fall_count = 0
            #         fall_detection_count = 0
            #         message_sent = False

            """----------------------------- 낙상 감지 알림 모듈 ----------------------------------"""
            # if fall_detection_count == (fps * 2):
            #     sender = NotificationSender('ws://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com')
            #     result_fall_detection = sender.send_notification(
            #         recipients=['10fa45f2-f375-41c9-a62a-093efcd01bd3'],
            #         title='낙상 감지',
            #         body='응급 상황',
            #         kind='system',
            #         severity='red',
            #         data={
            #             'sender': '10fa45f2-f375-41c9-a62a-093efcd01bd3',
            #             'disk_usage': 85,
            #             'server': 'python-test-server',
            #             'timestamp': datetime.now().isoformat(),
            #             'kind': 'system',
            #             'severity': 'red',
            #             'webcam_id': 'webcam53'
            #         },
            #         # scheduled_at: "2025-09-29T12:14:51.614Z", # 지금 저희 상황에선 필요없는 필드입니다.
            #         # expires_at: "2025-09-29T12:14:51.614Z"    # 지금 저희 상황에선 필요없는 필드입니다.
            #     )
                # print("낙상 감지")
                
            """---------------------------------------------------------------------------------"""
            
            
            """---------------------------------------------------------------------------------------------------------------------"""

            keypoints_list = []

        cap_out.write(frame)

        cv2.imshow("video streaming", frame)

        key_input = cv2.waitKey(1)

        if key_input == ord('q'):
            gc.collect()
            break

    cap.release()
    cv2.destroyAllWindows()
    not_fall_count = 0
    fall_detection_count = 0
    message_sent = False
    start_number += 1