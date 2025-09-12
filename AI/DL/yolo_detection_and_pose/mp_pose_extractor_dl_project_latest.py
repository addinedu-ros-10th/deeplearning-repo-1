import cv2
import mediapipe as mp
import os
import gc
import numpy as np
import pandas as pd
import datetime

"""
========== 사용 안내 ==========
0. 반드시 현재 위치를 AI/DL/yolo_detection_and_pose 로 설정하고 실행할 것.
1. 데이터 추출에 사용될 영상은 두자리 알파벳 코드로 된 폴더와 분류 기록이 저장된 csv 파일을 AI/DL/yolo_detection_and_pose 에 넣을 것.

2. local_base_link = "" 구문에는 영상이 들어있는 폴더명을 입력할 것. 

3. detection_training_data = pd.read_csv("") 구문에는 데이터셋 이름을 입력할 것.

4. 처리속도 향상을 꾀하고자 한다면 cv2.imshow("image extracting", image) 구문을 삭제하거나 각주처리하고 사용할 것. 단, 이 경우에는 중간 종료가 안 되므로 주의.

5. 작업 도중에 모종의 이유로 중단된 경우에는 images 폴더의 마지막 번호가 적힌 하위 폴더만 삭제하고 작업을 재개할 것.

6. 작업을 처음부터 다시 시작하고자 하는 경우에는 extract_record.csv 파일과 images 폴더, coordinate 폴더를 모두 삭제하고 실행할 것.

번외. detection_training_data = detection_training_data.drop([0, 1, 2]) 코드는 프로토타입 영상의 오류 정정용 코드이므로 삭제 또는 각주처리하고 사용할 것.
"""

local_base_link = "FY"                                                                # 영상 모음 폴더
detection_training_data = pd.read_csv("Fall Detectoin Training Data Set - 정규호.csv") # 데이터셋

# ========================================================================================================================================
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

BASE_PATH = "./"
IMAGE_FOLDER_NAME = "images"
COORD_FOLDER_NAME = "coordinate"
VIDEO_TYPE = ".mp4"
os.makedirs(BASE_PATH, exist_ok = True)

# detection_training_data = detection_training_data.drop([0, 1, 2]) # 테스트용 코드.
detection_training_data_list = detection_training_data.values.tolist()

detection_training_data_list_transformed = []

for line in range(0, len(detection_training_data_list), 3):
    detection_training_data_list_transformed_line = []

    detection_training_data_list_transformed_line.append(detection_training_data_list[line][0].split(".")[0])
    detection_training_data_list_transformed_line.append(detection_training_data_list[line+1][1])
    detection_training_data_list_transformed_line.append(detection_training_data_list[line+1][3])
    detection_training_data_list_transformed_line.append(detection_training_data_list[line+2][1])
    detection_training_data_list_transformed_line.append(detection_training_data_list[line+2][3])

    detection_training_data_list_transformed.append(detection_training_data_list_transformed_line)

def createNewImageFolder(base_path):
    folder_path = os.path.join(base_path, IMAGE_FOLDER_NAME)
    os.makedirs(folder_path, exist_ok = True)

    existing_folders = [int(name) for name in os.listdir(folder_path) if name.isdigit()]

    next_number = max(existing_folders) + 1 if existing_folders else 1
    sub_folder_path = os.path.join(folder_path, str(next_number))

    os.makedirs(sub_folder_path, exist_ok = True)

    return sub_folder_path, next_number

def drawLandmarksOnBlack(image, pose_landmarks):
    black_image = np.zeros_like(image)
    mp_drawing.draw_landmarks(
        black_image, pose_landmarks, mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color = (0, 255, 0), thickness = 2, circle_radius = 2),
        mp_drawing.DrawingSpec(color = (0, 0, 255), thickness = 2, circle_radius = 2)
    )

    return black_image

def poseDataExtractor(cap_link, warning_start_frame, fall_start_frame):

    pose = mp_pose.Pose()

    is_saving = True
    sw = False

    cap = cv2.VideoCapture(cap_link)

    pose_data = []
    image_folder_path, coord_folder_number = None, None

    if is_saving is True:
        image_folder_path, coord_folder_number = createNewImageFolder(BASE_PATH)
        pose_dataframe = pd.DataFrame(columns = ["frame_id","frame_path", "label", 
                                                 "kpt_0_x","kpt_0_y","kpt_0_z",
                                                 "kpt_1_x","kpt_1_y","kpt_1_z",
                                                 "kpt_2_x","kpt_2_y","kpt_2_z",
                                                 "kpt_3_x","kpt_3_y","kpt_3_z",
                                                 "kpt_4_x","kpt_4_y","kpt_4_z",
                                                 "kpt_5_x","kpt_5_y","kpt_5_z",
                                                 "kpt_6_x","kpt_6_y","kpt_6_z",
                                                 "kpt_7_x","kpt_7_y","kpt_7_z",
                                                 "kpt_8_x","kpt_8_y","kpt_8_z",
                                                 "kpt_9_x","kpt_9_y","kpt_9_z",
                                                 "kpt_10_x","kpt_10_y","kpt_10_z",
                                                 "kpt_11_x","kpt_11_y","kpt_11_z",
                                                 "kpt_12_x","kpt_12_y","kpt_12_z",
                                                 "kpt_13_x","kpt_13_y","kpt_13_z",
                                                 "kpt_14_x","kpt_14_y","kpt_14_z",
                                                 "kpt_15_x","kpt_15_y","kpt_15_z",
                                                 "kpt_16_x","kpt_16_y","kpt_16_z",
                                                 "kpt_17_x","kpt_17_y","kpt_17_z",
                                                 "kpt_18_x","kpt_18_y","kpt_18_z",
                                                 "kpt_19_x","kpt_19_y","kpt_19_z",
                                                 "kpt_20_x","kpt_20_y","kpt_20_z",
                                                 "kpt_21_x","kpt_21_y","kpt_21_z",
                                                 "kpt_22_x","kpt_22_y","kpt_22_z",
                                                 "kpt_23_x","kpt_23_y","kpt_23_z",
                                                 "kpt_24_x","kpt_24_y","kpt_24_z",
                                                 "kpt_25_x","kpt_25_y","kpt_25_z",
                                                 "kpt_26_x","kpt_26_y","kpt_26_z",
                                                 "kpt_27_x","kpt_27_y","kpt_27_z",
                                                 "kpt_28_x","kpt_28_y","kpt_28_z",
                                                 "kpt_29_x","kpt_29_y","kpt_29_z",
                                                 "kpt_30_x","kpt_30_y","kpt_30_z",
                                                 "kpt_31_x","kpt_31_y","kpt_31_z",
                                                 "kpt_32_x","kpt_32_y","kpt_32_z"])
        frame_count = 1 # cv2 프레임 번호와 일치



        print(f"Started saving to: {image_folder_path} and keypoints_{coord_folder_number}")

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Video frame is empty or video processing has been successfully completed")
            csv_file_name = f"keypoints_{coord_folder_number}.csv"
            coord_folder_path = os.path.join(BASE_PATH, COORD_FOLDER_NAME)
            os.makedirs(coord_folder_path, exist_ok = True)
            csv_file_path = os.path.join(coord_folder_path, csv_file_name)

            pose_dataframe.to_csv(csv_file_path, sep = ",", encoding = "utf-8", index = False)
            print("Coordinates saved to: {npy_file_path}")
            break

        image = cv2.resize(frame, (640, 360))
        results = pose.process(image)

        if results.pose_landmarks:

            if is_saving:
                keypoints = [[lmk.x, lmk.y, lmk.z] for lmk in results.pose_landmarks.landmark]

                img_file_name = f"frame_{frame_count:05d}.jpg"
                img_file_path = os.path.join(image_folder_path, img_file_name)
                black_background = drawLandmarksOnBlack(frame, results.pose_landmarks)

                if frame_count >= fall_start_frame:
                    label = "Fall"
                elif frame_count >= warning_start_frame:
                    label = "Warning"
                else:
                    label = "Normal"

                pose_data.append(f"{int(cap.get(cv2.CAP_PROP_POS_FRAMES)):04d}") # 프레임 번호
                pose_data.append(image_folder_path + "/" + img_file_name)       # 이미지 파일 주소
                pose_data.append(label)                                         # 레이블
                
                for key in keypoints:
                    for k in key:
                        pose_data.append(k)

                df_pose = pd.DataFrame([pose_data], columns = pose_dataframe.columns)

                pose_dataframe = pd.concat([pose_dataframe, df_pose], ignore_index=True)
                pose_data = []

                

                cv2.imwrite(img_file_path, black_background)
                
        frame_count +=1

        cv2.imshow("image extracting", image) # 이미지 출력

        key_input = cv2.waitKey(1)

        if key_input == ord('q'):
            gc.collect()
            sw = True
            break


    cap.release()
    cv2.destroyAllWindows()
    pose.close()

    is_saving = False

    if sw == True:
        return True
    else:
        return False

stop_switch = False
skip_switch = False
complete_count = 0

if os.path.exists("extract_record.csv"):
    data_record = pd.read_csv("extract_record.csv")
    skip_switch = True


for line in detection_training_data_list_transformed:

    extract_file_link = BASE_PATH + local_base_link + "/" + line[0] + "/" + line[0] + VIDEO_TYPE

    if os.path.exists("extract_record.csv") and extract_file_link == data_record.iloc[0, 1]:
        skip_switch = False
        continue
    elif skip_switch == True:
        continue

    print("\n\n@@@@@@@@@@[[ Pose Extracting... : " + extract_file_link + " ]]@@@@@@@@@@\n\n")

    stop_switch = poseDataExtractor(extract_file_link, line[1], line[3])

    if stop_switch == True:
        break

    else:
        complete_count += 1
        run_data_record = pd.DataFrame({"save_time": [datetime.datetime.now()],
                                        "latest_extracted_video_path": [extract_file_link],
                                        "complete_video_number": [complete_count]})
                                    # 추출 작업이 중단된 경우에는 반드시 images 폴더 내 마지막 번호의 폴더를 지우고 실행.
        run_data_record.to_csv("extract_record.csv", sep = ",", index=False)
    
    
