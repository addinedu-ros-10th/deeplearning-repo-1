from ultralytics import YOLO
import ultralytics
import os
import yaml
import math
import cv2
import numpy as np
import gc
import time

ultralytics.checks()

colorMap = {
    "leftEye": (0, 0, 255),
    "rightEye": (0, 0, 255),
    "leftNose": (0, 255, 0),
    "rightNose": (0, 255, 0),
    "leftNeck": (255, 0, 0),
    "rightNeck": (0, 0, 255),
    "neck":(0, 0, 255),
    "leftUpperArm": (205, 90, 106),
    "rightUpperArm": (200, 200, 200),
    "leftLowerArm": (200, 200, 200),
    "rightLowerArm": (100, 100, 100),
    "leftBody": (100, 100, 100),
    "rightBody": (200, 200, 200),
    "pelvis": (20, 205, 20),
    "lefrUpperLeg": (255, 0, 255),
    "rightUpperLeg": (128, 0, 0),
    "leftLowerLeg": (190, 128, 205),
    "rightLowerLeg": (140, 60, 70)
}

partDict = {
    "leftEye": (1, 3),
    "rightEye": (2, 4),
    "leftNose": (1, 0),
    "rightNose": (2, 0),
    "leftNeck": (3, 5),
    "rightNeck": (4, 6),
    "neck":(5, 6),
    "leftUpperArm": (5, 7),
    "rightUpperArm": (6, 8),
    "leftLowerArm": (7, 9),
    "rightLowerArm": (8, 10),
    "leftBody": (5, 11),
    "rightBody": (6, 12),
    "pelvis": (11, 12),
    "lefrUpperLeg": (11, 13),
    "rightUpperLeg": (12, 14),
    "leftLowerLeg": (13, 15),
    "rightLowerLeg": (14, 16)
}

def distance(x1, y1, x2, y2):
    result = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    return int(result)

def drawLine(frame, name, org, dst):
    if (org.any() == 0 or dst.any() == 0):
        return frame
    frame = cv2.line(frame, org, dst, colorMap[name], 2)
    return frame

model = YOLO("yolo11n-pose.pt")
model_detect = YOLO("yolo11n.pt")
cap = cv2.VideoCapture("./kbo_highlight_kt_vs_sl.mp4")
# cap = cv2.VideoCapture("./ytn_news_solitare_elder.mp4")

pose_print_switch = 0

time_start = time.time()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Video frame is empty or video processing has been successfully completed")
        break

    frame = cv2.resize(frame, (1280, 720))
    results = model_detect(frame)

    frame2 = list(results)[0].plot()

    if pose_print_switch < 2:
        pose_print_switch += 1

        cv2.imshow("result preview", frame2)

    else:
        pose_print_switch = 0

        results_pose = model(frame, stream = True)

        for r in results_pose:
            keypoints = r.keypoints

            for ks in keypoints:

                for ks in keypoints:
                    k = np.array(ks.xy[0].cpu(), dtype = int)

                    # cv2.circle(frame, k[0],
                    #               distance(k[0][0], k[0][1], k[3][0], k[3][1]),
                    #               (255, 255, 255),
                    #               5)

                    try:
                        for idx, (name, (org, dst)) in enumerate(partDict.items()):

                            frame2 = drawLine(frame2, name, k[org], k[dst])

                    except Exception as e:
                        print(e)
    
        cv2.imshow("result preview", frame2)

    if cv2.waitKey(1) == ord("q"):
        gc.collect()
        break

cap.release()
cv2.destroyAllWindows()

time_end = time.time()

print(time_end - time_start)