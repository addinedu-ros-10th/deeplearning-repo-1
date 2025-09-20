import cv2
import mediapipe as mp # 자세인식용 모듈
import numpy as np
import torch
from ultralytics import YOLO # 객체인식용 모듈
import ultralytics
import gc
import time
import uuid
from util import common_api

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

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# url = "http://192.168.0.61:81/stream"
url = "http://100.65.221.86:3010/receiver?camera_id=cam4"

# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("http://100.65.221.86:3010/receiver?camera_id=cam4")
cap = cv2.VideoCapture(url)
# cap = cv2.VideoCapture("/home/dj/dev_ws/EDA/data/LSTM_test/test/test.mp4")
"""0번: 노트북 카메라, 1번~: 기타 카메라. 카메라 포트 확인 시에는 터미널에 "ls -l /dev/video*" 커맨드를 입력하여 확인. """

model_path = "./data_511_380_yb_sdj_v1.0.pt" # 학습모델 적용하는 위치
model = torch.jit.load(model_path)
model.eval()

model_yolo = YOLO("yolo11n.pt")
model_yolo.predict(classes = 0)

items = []

# session_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
session_id = str(uuid.uuid4())
experiment_id = "12bd0c67-a10c-4e01-adec-871010e49031"

server_url = "http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com"

labels_map = {0: "Normal", 1: "Warning", 2: "Fall"}

is_collecting = True
keypoints_list = []
yolo_activate_switch = False
yolo_activate_count = 0

index_number = 0
confidence_bool = False

client = common_api.CommonApiClient(base_url= server_url)

while cap.isOpened():

    keypoints = []

    ret, frame = cap.read()

    if not ret:
        print("Cannot open video or video is terminated")
        break

    frame = cv2.resize(frame, (1024, 768)) # 이미지 사이즈 조정

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = pose.process(image)

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

        keypoints_list = []

        if confidence_percent > 80:
            confidence_bool = True
        else:
            confidence_bool = False

        # if yolo_activate_switch == True: # yolo 연산 횟수를 절반으로 줄이는 코드
        #     if yolo_activate_count < 1:
        #         yolo_activate_count += 1
        #     else:
        #         yolo_activate_count = 0
        #         result_yolo = model_yolo(frame)
        #         frame = list(result_yolo)[0].plot()

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
            "label_pred": predicted_label.lower(),
            "ts_rel_ms": int(time.time()),
            "confidence": confidence,
            "passed": confidence_bool,
            "threshold_name": "yolo_threshold",
            "threshold_snapshot": {
                "threshold": 0.5
            }
        }

        items.append(item)
        index_number += 1
        print(len(items))

    if len(items) == 60:
        items_dict = {"items": items}
        print(f"items_dict: {items_dict}")
        status, body = client.post("/frame-predictions/batch", json = items_dict)
        print(status, body)
        items = []
        # index_number = 0

    if yolo_activate_switch == True:
        result_yolo = model_yolo(frame)
        frame = list(result_yolo)[0].plot()

    cv2.imshow("video streaming", frame)

    key_input = cv2.waitKey(1)

    if key_input == ord('q'):
        gc.collect()
        break
    elif key_input == ord('a'):
        if yolo_activate_switch == False:
            yolo_activate_switch = True
        else:
            yolo_activate_switch = False

cap.release()
cv2.destroyAllWindows()