import sys
import cv2
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
from PyQt6 import uic


from_class = uic.loadUiType("/home/addinedu/dev_ws/deeplearning-repo-1/IOT/PyQt/ESP32_Test/test01.ui")[0]

class CameraWidget(QWidget):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.label = QLabel("Camera Feed")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # OpenCV VideoCapture (ESP32-CAM 스트림 URL)
        self.cap = cv2.VideoCapture(self.url)

        # ESP32-CAM 해상도 설정
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # 타이머로 주기적으로 프레임 갱신
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        #self.timer.start(30)  # 30ms 간격 (약 33fps)
        fps_time = self.cap.get(cv2.CAP_PROP_FPS)
        self.timer.start(int(1000 / fps_time))

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # ESP32-CAM 스트림 URL
    url = "http://192.168.0.61:81/stream"  # 실제 ESP32-CAM IP와 포트 사용
    win = CameraWidget(url)
    win.show()
    sys.exit(app.exec())