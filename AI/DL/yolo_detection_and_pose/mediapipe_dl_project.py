from IPython.display import Image, display, clear_output
import cv2
import mediapipe as mp
import time
import gc
from pytubefix import YouTube
from pytubefix.cli import on_progress

"""
영상 조절 key 일람

q : 종료
s : 일시정지(다른 기능들 모두 정지됨)
w : 재생 재개
a : 2초 이전 시점으로 이동
d : 2초 이후 시점으로 이동
z : 0.5초 이전 시점으로 이동
c : 0.5초 이후 시점으로 이동

"""

url_mode = False #url 재생원 사용 여부 설정. False는 오프라인, True는 url 사용

def video_show(frame, width = 640):
    _, buffer = cv2.imencode(".jpg", frame)
    clear_output(wait = True)
    display(Image(data = buffer, width = width))

def video_pose_estimation_all_time(video_path): # 풀타임 재생용
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose(static_image_mode = False, min_detection_confidence = 0.5, min_tracking_confidence = 0.5)


    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS) # 영상의 초당 프레임 수 구하기 
    
    period_fps = 1/fps # 초당 프레임수의 역수. 재생시간간격

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Video frame is empty or video processing has been successfully completed")
            break

        frame = cv2.resize(frame, (1280, 720))

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = cv2.putText(image, "Time: " + str(round(cap.get(cv2.CAP_PROP_POS_MSEC)/1000, 2)), 
                            (10, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (200, 200, 200), 2) # 영상의 재생시간
        image = cv2.putText(image, "Frame: " + str(cap.get(cv2.CAP_PROP_POS_FRAMES)), 
                            (10, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (200, 200, 200), 2) # 영상의 프레임
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS) # mediapipe 자세 그리기

        cv2.imshow("mediapipe results", image)

        waitkey1 = cv2.waitKey(1)

        if waitkey1 == ord("q"): # 'q' 키를 눌러 종료
            gc.collect()
            break

        elif waitkey1 == ord("s"): # 's' 키를 눌러 일시정지. 재생 전까지는 다른 커맨드를 사용할 수 없음.
            while True:
                waitkey2 = cv2.waitKey()
                if waitkey2 == ord("w"): # 'w' 키를 눌러 재생
                    break

        elif waitkey1 == ord("a"): # 'a' 키를 눌러 2초 이전으로 이동.
            cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) - 2000)

        elif waitkey1 == ord("d"): # 'd' 키를 눌러 2초 이후로 이동.
            cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) + 2000)

        elif waitkey1 == ord("z"): # 'z' 키를 눌러 0.5초 이전으로 이동.
            cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) - 500)

        elif waitkey1 == ord("c"): # 'c' 키를 눌러 0.5초 이후로 이동.
            cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) + 500)

        # if (loop_end - loop_start) < period_fps:
        #     time.sleep(period_fps - (loop_end - loop_start)) # 영상의 실제 재생에 가까운 조건으로 루프 진행

    cap.release()
    cv2.destroyAllWindows()
    gc.collect()

if url_mode == False:
    video = "./00015_H_A_SY_C1.mp4" #오프라인 파일 경로는 이곳에 지정.

else:
    video_url = "https://www.youtube.com/watch?v=eBhOX1UN37A" #유튜브 다운로드를 이용할 경우

    yt = YouTube(video_url, on_progress_callback = on_progress)

    ys = yt.streams.get_highest_resolution()
    ys.download()

    video_title = yt.title

    video = yt.title + ".mp4"

video_pose_estimation_all_time(video)