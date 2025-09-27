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

## 환경 구축 상태 (2025-09-27)
- Flutter: 3.32.8 stable (Dart 3.8.1)
- 플랫폼 지원: Web, Linux desktop 활성화 완료
- Android Studio/SDK: 설치 및 구성 완료 (SDK 36, build-tools 36.0.0, 라이선스 수락)
- AVD(Device Manager): `pixel7api34` (Android 14 Google APIs x86_64) 생성 완료
- JAVA_HOME: `/opt/android-studio/jbr` 로 설정 및 `~/.bashrc` 반영
- flutter doctor: No issues found!

## 개발 현황 업데이트 (2025-09-27)
- dotenv 안전화: 테스트 환경에서 `NotInitializedError` 방지 (`env.dart` 안전 접근)
- STT API 마이그레이션: `SpeechListenOptions` 적용으로 deprecated 제거 및 분석기 경고 0
- 테스트: 기본 위젯 테스트를 현재 UI(`Voice Interface`)에 맞게 갱신, 통과 확인
- 문서: 실행/환경/테스트 가이드 보강, 환경 구축 결과 기록
- 자산: `assets/env/.env.dev`, `.env.prod` 플레이스홀더 생성 (토큰 빈 값)
 - 한국어 TTS 통합: Piper/Mimic3/OpenTTS 백엔드 선택 및 보이스 선택 UI/로직 추가, audioplayers로 WAV 재생
 - 환경 변수 확장: `TTS_BACKEND`, `TTS_BASE_URL`, `TTS_DEFAULT_VOICE` 지원 및 `.env` 반영
 - TTS 서버 상태 표시/재시도 버튼 추가(`/healthz`)
 - 분석기/테스트: 의존성 추가 후 분석기 0 issue, 위젯 테스트 통과 유지

## 향후 진행
- 네트워크 STT 및 오디오 업로드 경로 연동(서버 지원 시) 및 재생 품질 검증
- WS 스트리밍 초안 연결 및 이벤트 핸들링(선택)
- 에뮬레이터/실기기(Android) 마이크 권한/동작 검증 플로우 문서화
- CI 통합: `flutter analyze`, `flutter test` 파이프라인 추가
- 프로덕션 프로파일링: TTS 음성/속도/피치 프리셋 및 UX 보완
 - Piper 서버 샘플 배포/연동 가이드 문서화 및 실 리스닝 테스트 진행

## 구축 달성 단계 (Milestones)
- [x] Flutter 스캐폴딩 및 필수 의존성 구성
- [x] Web/Linux 데스크톱 타깃 활성화 및 구동 확인
- [x] Provider 상태관리/파형 UI/녹음 제어 초안 구현
- [x] OpenAI Assistant 호출 + TTS 재생 플로우 구현 (토큰 필요 시 동작)
- [x] dotenv 안전화 및 테스트 안정화
- [x] Analyzer 경고 제거(0), 위젯 테스트 통과
- [x] Android SDK/AVD/JAVA 환경 구축 및 flutter doctor 정상화
- [ ] 서버 STT/오디오 업로드 API 연동 및 응답 파싱 정제
- [ ] WebSocket 스트리밍 초안 연결 및 이벤트 모델 정의
- [ ] CI 파이프라인 연동 및 브랜치 보호 규칙 반영

## 현재 단계 (2025-09-27)
- 앱 기능은 로컬에서 Web/Linux 데스크톱 대상으로 안정 구동
- Android 에뮬레이터 환경 구성이 완료되어, 기기 테스트 준비 상태
- 서버 연동(STT/Streaming)은 사양 확정 대기; dotenv/define로 운영 변수 분리 완료

## 다음 액션 아이템 (우선순위)
1. 서버 STT/Assistant 실제 엔드포인트 연동 및 예외 처리 정제
2. 마이크 권한/오디오 경로(Android/Web)의 권한 안내/실패 복구 UX 보완
3. WS 스트리밍(선택): 연결 수명주기/재연결/버퍼링 정책 설계 및 초안 구현
4. CI: `flutter analyze`/`flutter test` GitHub Actions 추가, 배지 노출
5. 문서화: Android/웹 권한 가이드, 문제 해결(네트워크/권한/에뮬레이터) 섹션 확장

## Android 실행/검증 가이드 (요약)
- AVD 실행:
```
$ANDROID_SDK_ROOT/emulator/emulator -avd pixel7api34 -netdelay none -netspeed full &
```
- 앱 실행 예시(Android):
```
cd app/user_app
flutter run -d emulator-5554 \
  --dart-define=APP_ENV=dev \
  --dart-define=API_BASE_URL=https://api.openai.com \
  --dart-define=WS_URL=wss://example.dev/ws \
  --dart-define=AUTH_TOKEN=sk-... \
  --dart-define=USE_DOTENV=false
```

## 한국어 TTS 옵션 및 결정
- 후보:
  - Piper (권장, 경량/실시간, ko_KR-pml_high/low)
  - Mimic3 (다양한 음색, REST API, 다소 무거움)
  - OpenTTS (통합, Piper/Mimic3 백엔드 선택 가능)
  - System TTS (기기 엔진 사용: Google/Samsung 등)
- 앱 제공 기능:
  - Backend 선택: system / piper / mimic3 / opentts
  - Piper 음성: ko_KR-pml_high / ko_KR-pml_low 선택 가능
  - 엔진/음성/STT 특성 안내 텍스트 표시
  - `.env`: `TTS_BACKEND`, `TTS_BASE_URL`, `TTS_DEFAULT_VOICE`
- 기본값(개발): Piper + `ko_KR-pml_high` + `http://localhost:5002`

### 체크리스트 (Korean TTS)
- [x] UI에 Backend/Voice 선택 추가 및 안내 텍스트 노출
- [x] Provider에 HTTP TTS 서비스 통합(Piper/Mimic3/OpenTTS)
- [x] `.env.dev/.env.prod`에 TTS 변수 추가
- [ ] Piper 서버 샘플 배포/연동 가이드 추가(FastAPI/OpenTTS 등)
- [ ] 실제 샘플 한국어 문장들로 음질/자연스러움 리스닝 테스트
- [ ] 사용자 선호 기본값(여/남, 속도/피치) 저장/복원
