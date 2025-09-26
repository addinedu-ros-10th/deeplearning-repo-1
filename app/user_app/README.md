# User App (Flutter) - Voice Interface

## 개요
- Flutter 기반 음성 인터페이스 클라이언트
- 기능: STT(음성→텍스트), LLM 응답 수신, TTS(텍스트→오디오 재생), 파형 UI(흑/회색)
- 백엔드: Voice API(REST/WS), vLLM 또는 OpenAI API (서버 측 설정에 따름)

## 요구사항
- Flutter 3.22+
- Dart 3.4+
- Android/iOS/Desktop(개발 편의)

## 설치/실행 (Web 권장)
```bash
# 의존성 설치
flutter pub get

# .env 방식 (권장: PowerShell/CMD)
flutter run -d chrome ^
  --dart-define=USE_DOTENV=true ^
  --dart-define=APP_ENV=dev

# 또는 dart-define로 직접 지정
flutter run -d chrome ^
  --dart-define=APP_ENV=dev ^
  --dart-define=API_BASE_URL=https://api.openai.com ^
  --dart-define=WS_URL=wss://example.dev/ws ^
  --dart-define=AUTH_TOKEN=sk-... ^
  --dart-define=USE_DOTENV=false
```

## 환경변수(.env)
- 파일: `assets/env/.env.dev`, `assets/env/.env.prod`
- 키: `API_BASE_URL`, `WS_URL`, `AUTH_TOKEN`
- 실행 시 `--dart-define=USE_DOTENV=true` + `--dart-define=APP_ENV=dev|prod`

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
- Listen: 마이크 권한 허용 후 파형 확인(실레벨 또는 폴백 애니메이션)
- Ask + Speak: 전사 텍스트로 OpenAI 질의→응답을 즉시 TTS 재생
- Voice 선택/Rate/Pitch 조정 가능
  
자세한 테스트 절차는 `staging/testing_guide.md` 참고
