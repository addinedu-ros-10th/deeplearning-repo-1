# User App 구축 계획 & 체크리스트 (Flutter)

## 목표
- 간단/안정/직관: STT→LLM→TTS 파이프라인 연동, 파형 UI(흑/회색)
- 환경별(dev/prod) 설정/실행이 쉬운 구조

## 체크리스트
- [x] 스캐폴딩 생성(pubspec.yaml, lib 구조, env 로더)
- [x] HTTP/WS 클라이언트 유틸 추가
- [x] Provider 상태(녹음, 전사 텍스트, 응답 오디오) 초안
- [x] 파형 UI(흑/회색 CustomPainter) 초안
 - [x] .env.dev/.env.prod 추가 및 dart-define 연계
- [ ] 네트워크: STT/Assistant 호출 및 오디오 재생
  - [x] Assistant(OpenAI) 호출 및 TTS 재생
- [ ] WS 초안 연결(향후)
- [ ] 문서/테스트 가이드

## 구조 제안
- lib/
  - core/env/env.dart
  - core/net/api_client.dart
  - core/net/ws_client.dart
  - features/voice/state/voice_provider.dart
  - features/voice/ui/voice_page.dart (파형 UI)
  - main.dart

## 개발/테스트 환경 (Web 우선)
- 권장 명령어(Windows PowerShell/터미널):
  - `flutter run -d chrome --dart-define=APP_ENV=dev --dart-define=API_BASE_URL=https://api.openai.com --dart-define=WS_URL=wss://example.dev/ws --dart-define=AUTH_TOKEN=sk-... --dart-define=USE_DOTENV=false`
- Git Bash 사용 시 PATH 문제 가능: `"/c/src/flutter/bin/flutter.bat" run ...`
- 핫 리로드: 저장 시 즉시 반영
- Chrome 마이크 권한 허용 필요 (STT 실제 연결 시)

## 파이프라인 (Flowchart)
```
User Mic → [STT: speech_to_text/Web Speech API] → Transcript
  → [HTTP: OpenAI/VLLM chat] → Assistant Reply
  → [TTS: flutter_tts/Web Speech] → Audio Out
  ↺ UI Waveform reflects mic level & speaking state
```

## 운영/개발 환경변수 관리
- 키: `API_BASE_URL`, `WS_URL`, `AUTH_TOKEN`
### 옵션 1) dart-define (권장)
- 실행 시 지정: `--dart-define=API_BASE_URL=... --dart-define=WS_URL=... --dart-define=AUTH_TOKEN=...`
- `.env` 파일 없이도 동작, Web 404 경고 없음
### 옵션 2) dotenv 자산 사용
- 파일: `app/user_app/assets/env/.env.dev`, `app/user_app/assets/env/.env.prod`
- `pubspec.yaml`의 assets에 두 파일을 등록
- 실행 시: `--dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev|prod`
- 예시(.env.dev):
```
API_BASE_URL=https://api.openai.com
WS_URL=wss://example.dev/ws
AUTH_TOKEN=sk-...your-openai-key...
```

## 실행 예시
```
flutter run -d chrome \
  --dart-define=APP_ENV=dev \
  --dart-define=API_BASE_URL=https://api.openai.com \
  --dart-define=WS_URL=wss://example.dev/ws \
  --dart-define=AUTH_TOKEN=sk-... \
  --dart-define=USE_DOTENV=false
```

## 보안/버전관리
- `.env*` 파일은 Git에 커밋하지 않도록 `.gitignore`에 추가 권장:
```
app/user_app/assets/env/.env*
```

## 진행 현황 로그
- 2025-09-26
  - 완료: Flutter Web 활성화 및 의존성 설치
  - 완료: 구조 스캐폴딩(`env.dart`, `api_client.dart`, `ws_client.dart`, `OpenAiService`, `VoiceProvider`, `VoicePage`, `go_router`)
  - 완료: 파형 UI 구현 및 렌더링 이슈 수정(CustomPaint child 덮어쓰임 제거)
  - 완료: 문서에 실행/트러블슈팅/환경변수 전략 추가
  - 보류: `.env.dev/.env.prod` 파일 생성(보안상 수동 생성 권장). 현재는 `dart-define` 우선 사용
 - 완료: `.env.dev/.env.prod` 플레이스홀더 생성 및 assets 등록, `flutter pub get` 반영
  - 완료: Web STT 통합(speech_to_text) + 전사/레벨 스트림 바인딩
  - 완료: 파형 폴백 애니메이션(레벨 미제공 시) 및 TTS 중 파형 표시
  - 완료: 보이스 선택/속도/피치 옵션 UI 추가
  - 완료: dotenv NotInitializedError 회피 (maybeGet 사용, tolerant load)

## 테스트 가이드 (요약)
- OpenAI 토큰 없이: UI 구동/파형 확인용. “Listen” 클릭 시 랜덤 레벨 파형 확인, “Ask + Speak”는 안내 문구 또는 빈 응답 처리
- OpenAI 토큰 사용: `.env.dev`에 `AUTH_TOKEN=sk-...` 설정 후 아래 실행
```
flutter pub get
flutter run -d chrome \
  --dart-define=USE_DOTENV=true \
  --dart-define=APP_ENV=dev
```
- 또는 dotenv 없이:
```
flutter run -d chrome \
  --dart-define=APP_ENV=dev \
  --dart-define=API_BASE_URL=https://api.openai.com \
  --dart-define=WS_URL=wss://example.dev/ws \
  --dart-define=AUTH_TOKEN=sk-... \
  --dart-define=USE_DOTENV=false
```
