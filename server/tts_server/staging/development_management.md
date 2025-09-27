# TTS Server Development Management

## 목표
- FastAPI 기반 TTS 프록시 서버 제공 (Piper/Mimic3/OpenTTS)
- Flutter `user_app` 및 `app_server`와 연동 가능한 안정적 API (`/api/tts`)
- 모노레포 정책 준수: `server/tts_server` 외 다른 프로젝트 수정 금지

## 체크리스트
- [x] 프로젝트 스캐폴딩 (FastAPI, settings, tests)
- [x] Dockerfile/Compose 구성 (Piper 백엔드 포함)
- [x] 문서화: `docs/tts_backend_setup.md`
- [ ] TDD: `/api/tts` happy-path 테스트(통합) 추가
- [ ] 운영/개발 환경 변수 샘플 `.env` 제공
- [ ] Piper/Mimic3/OpenTTS 간 전환 테스트 및 에러 핸들링 강화
- [ ] 성능/타임아웃/재시도 정책 문서화

## 개발 지침 (Monorepo Policy)
- `server/tts_server` 하위에서만 코드 변경
- 공용 설정 명명은 `server/app_server`의 스타일을 최대한 준수 (`DB_APP_URL` 등)
- PR 시 `analyze/test` 통과 로그 첨부

## 현황 (2025-09-27)
- FastAPI 서버 `/healthz`, `/api/tts` 라우트 제공
- 업스트림 OpenTTS(HTTP 5500)로 전환, GET 우선/POST 폴백 지원
- Settings 평탄화로 환경변수 신뢰성 향상(`TTS_BACKEND`, `TTS_BASE_URL`, `TTS_DEFAULT_VOICE`)
- 기본 단위 테스트 추가: 헬스체크, 잘못된 입력 검증 + env 반영 테스트
- Docker Compose로 OpenTTS + TTS Server + (옵션) Nginx 프록시 구동 가능
- Dockerfile(poetry) 정리 및 포트 노출(5502)

## 다음 일정
1. 통합 테스트: 실제 Piper 컨테이너와 end-to-end WAV 생성/재생 확인
2. 실패 시 재시도/백오프, 요청 로깅/메트릭 추가
3. 운영 구성 샘플(.env, env 파일 템플릿) 제공
4. `app_server`와 연동 가이드 및 헬스체크/장애 처리 흐름 문서화

## 수동 테스트 가이드 (로컬)
```bash
cd server/tts_server/docker
docker compose up --build -d
curl -sS "http://localhost:5502/api/tts?text=hello" --output test.wav
aplay test.wav # 또는 시스템 재생기
```

### 수동 테스트(마이크 사용, Flutter user_app 연동)
1) TTS 서버 기동
```bash
cd server/tts_server/docker
docker compose up --build -d
```

2) 사용자 앱 환경 변수 설정(`app/user_app/assets/env/.env.dev`)
```env
TTS_BACKEND=opentts
TTS_BASE_URL=http://localhost:5502
TTS_DEFAULT_VOICE=en_US-lessac-high
```

3) Flutter 앱 실행(데스크톱 또는 Android 권장)
```bash
cd app/user_app
flutter pub get
# Linux 데스크톱
flutter run -d linux --dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev
# 또는 Android 에뮬레이터
flutter run -d emulator-5554 --dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev
# Web(옵션): 마이크 권한 허용, CORS 이슈 시 동일 출처 또는 프록시 권장
flutter run -d chrome --dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev
```

4) 앱 내 테스트 절차
- 상단 안내에서 Backend가 OpenTTS인지 확인
- Voice: `en_US-lessac-high` 선택(한국어 모델 준비 시 ko-KR로 교체)
- Listen 버튼으로 마이크 녹음을 시작하여 한국어 문장을 말하기
- Ask + Speak 버튼으로 합성된 한국어 음성 재생 확인(자연스러움 체크)

5) 트러블슈팅
- 오디오 미출력: 시스템 볼륨/출력 장치 확인, `docker compose logs -f tts-backend tts-server`
- 마이크 권한: OS/Chrome 권한 허용 여부 확인, Android는 에뮬레이터/실기기 권한 허용
- Web CORS: 서로 다른 origin일 경우 FastAPI에 CORS 미들웨어 추가 또는 리버스 프록시로 동일 출처 구성
