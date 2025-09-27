# ESP32 영상 스트림 테스트 가이드

ESP32에서 송출하는 영상 스트림을 테스트하고 모니터링하는 도구입니다.

## 🚀 빠른 시작

### 기본 연결 테스트
```bash
python3 esp32_stream_test.py
```

### 특정 URL 테스트
```bash
python3 esp32_stream_test.py --url http://192.168.0.61:81/stream
```

## 📋 사용 가능한 옵션

### 1. 연결 테스트
ESP32와의 기본 연결 상태를 확인합니다.
```bash
python3 esp32_stream_test.py --test-connection
```

### 2. 스트림 품질 테스트
지정된 시간 동안 스트림의 품질을 측정합니다.
```bash
# 10초간 품질 테스트
python3 esp32_stream_test.py --test-quality 10

# 30초간 품질 테스트
python3 esp32_stream_test.py --test-quality 30
```

### 3. 프레임 캡처
스트림에서 프레임을 캡처하여 이미지 파일로 저장합니다.
```bash
# 기본 설정으로 10개 프레임 캡처
python3 esp32_stream_test.py --capture-frames

# 20개 프레임을 특정 디렉토리에 저장
python3 esp32_stream_test.py --capture-frames --max-frames 20 --output-dir ./my_frames
```

### 4. 실시간 모니터링
OpenCV 창에서 실시간으로 스트림을 확인합니다.
```bash
# 60초간 실시간 모니터링
python3 esp32_stream_test.py --monitor 60

# 'q' 키를 눌러 조기 종료 가능
```

### 5. 네트워크 진단
네트워크 연결 상태를 진단합니다.
```bash
python3 esp32_stream_test.py --diagnosis
```

## 🔧 종합 테스트

모든 기능을 한 번에 테스트하려면:
```bash
python3 esp32_stream_test.py --diagnosis --test-quality 15 --capture-frames --max-frames 5 --monitor 30
```

## 📊 출력 정보

### 연결 테스트 결과
- HTTP 응답 코드
- Content-Type
- Content-Length

### 품질 테스트 결과
- 해상도 (width x height)
- 보고된 FPS vs 실제 FPS
- 총 프레임 수
- 프레임 손실률

### 네트워크 진단 결과
- TCP 연결 상태
- HTTP 응답 시간
- 연결 성공/실패 여부

## 🛠️ 문제 해결

### 연결 실패 시
1. **ESP32가 실행 중인지 확인**
   ```bash
   ping 192.168.0.61
   ```

2. **포트가 열려있는지 확인**
   ```bash
   telnet 192.168.0.61 81
   ```

3. **방화벽 설정 확인**
   - ESP32의 포트 81이 열려있는지 확인
   - 로컬 방화벽에서 해당 포트를 허용하는지 확인

### 스트림 품질 문제 시
1. **네트워크 대역폭 확인**
   - WiFi 신호 강도 확인
   - 다른 네트워크 사용량 확인

2. **ESP32 설정 확인**
   - 해상도 설정이 너무 높지 않은지 확인
   - FPS 설정이 적절한지 확인

### 프레임 캡처 실패 시
1. **저장 공간 확인**
   - 디스크 용량이 충분한지 확인

2. **권한 확인**
   - 출력 디렉토리에 쓰기 권한이 있는지 확인

## 📁 파일 구조

```
Util/
├── esp32_stream_test.py          # 메인 테스트 스크립트
├── ESP32_STREAM_GUIDE.md         # 이 가이드 파일
└── captured_frames/              # 캡처된 프레임 저장 디렉토리
    ├── esp32_frame_20250919_155830_001_000.jpg
    ├── esp32_frame_20250919_155830_501_001.jpg
    └── ...
```

## 🔍 예제 출력

### 성공적인 연결 테스트
```
🔍 스트림 연결 테스트: http://192.168.0.61:81/stream
  ✅ HTTP 응답: 200
  📋 Content-Type: multipart/x-mixed-replace; boundary=1234567890
  📏 Content-Length: Unknown
```

### 품질 테스트 결과
```
📊 스트림 품질 테스트 (10초)
  📐 해상도: 640x480
  🎬 FPS: 30.0
  ⏱️  10초간 프레임 수집 중...
    📈 현재 FPS: 29.8
    📈 현재 FPS: 30.1
    📈 현재 FPS: 29.9
  ✅ 테스트 완료:
    📊 실제 FPS: 29.9
    📈 총 프레임: 299
    ⏱️  총 시간: 10.00초
    📉 프레임 손실률: 0.33%
```

## 💡 팁

1. **실시간 모니터링**에서 'q' 키를 눌러 언제든지 종료할 수 있습니다.
2. **프레임 캡처**는 0.5초 간격으로 실행되어 너무 빠른 캡처를 방지합니다.
3. **네트워크 진단**을 먼저 실행하여 연결 문제를 파악하는 것이 좋습니다.
4. **스트림 품질 테스트**는 최소 10초 이상 실행하는 것을 권장합니다.

## 🚨 주의사항

- ESP32가 실행 중이어야 합니다.
- 네트워크 연결이 안정적이어야 합니다.
- OpenCV가 설치되어 있어야 합니다 (`pip install opencv-python`).
- requests 라이브러리가 필요합니다 (`pip install requests`).

