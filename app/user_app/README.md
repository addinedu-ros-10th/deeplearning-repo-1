# User App (Flutter) - Voice Interface

## 개요
- Flutter 기반 음성 인터페이스 클라이언트
- 기능: STT(음성→텍스트), LLM 응답 수신, TTS(텍스트→오디오 재생), 파형 UI(흑/회색)
- 백엔드: Voice API(REST/WS), vLLM 또는 OpenAI API (서버 측 설정에 따름)

## 요구사항
- Flutter 3.22+
- Dart 3.4+
- Android/iOS/Desktop(개발 편의)

## 설치/실행
```bash
# Flutter 환경 준비 후
flutter pub get
# 개발(ENV=dev)
flutter run --dart-define=APP_ENV=dev
# 운영(ENV=prod)
flutter run --dart-define=APP_ENV=prod
```

## 환경변수(.env)
- `assets/env/.env.dev`, `assets/env/.env.prod`
- 예시 키: `API_BASE_URL`, `WS_URL`, `AUTH_TOKEN`

## 아키텍처
- core: env/http/ws 유틸
- features/voice: provider 상태, 파형 UI, 녹음 제어
- 단순 라우팅(필요 시 go_router 도입)

## 엔드포인트(예)
- POST /voice/stt (multipart)
- POST /voice/assistant (multipart → audio/wav)
- WS  /voice/stream (향후)

## 상태관리
- provider + ChangeNotifier (간결/안정)

## 테스트
- 수동: 마이크 입력→파형 반응, 버튼으로 STT/Assistant 호출→오디오 재생
- 추후: widget/unit 테스트 추가
