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

## 현황 (2025-09-28)
- FastAPI 서버 `/healthz`, `/api/tts`, `/api/voices` 제공(업스트림 OpenTTS 프록시)
- 업스트림 OpenTTS(HTTP 5500)로 전환 완료; 요청은 GET 우선/POST 폴백 지원
- Settings 평탄화 적용(`TTS_BACKEND`, `TTS_BASE_URL`, `TTS_DEFAULT_VOICE`)
  - 기본 보이스 표기 통일: `ko-KR-pml-high` (하이픈 표기)
  - OpenTTS 실제 보이스 ID는 `/api/voices` 응답을 기준으로 선택 권장(언더스코어 변형 존재)
- 기본 단위 테스트 유지: 헬스체크, 잘못된 입력 검증, env 오버라이드 반영
- Docker Compose로 OpenTTS + TTS Server + (옵션) Nginx 프록시 구동 가능
- 옵션 구성: `voices-fetcher`로 Piper 한국어 보이스(예: `ko_KR-kss_high`) 자동 다운로드/마운트

## 다음 일정
1. 통합 테스트: 실제 Piper 컨테이너와 end-to-end WAV 생성/재생 확인
2. 실패 시 재시도/백오프, 요청 로깅/메트릭 추가
3. 운영 구성 샘플(.env, env 파일 템플릿) 제공
4. `app_server`와 연동 가이드 및 헬스체크/장애 처리 흐름 문서화

## 자동 보이스 다운로드(옵션)
- 파일: `server/tts_server/docker/compose.fixed2.yml`
- 목적: Piper 한국어 보이스(`ko_KR-kss_high`)를 사전 다운로드하여 OpenTTS가 즉시 인식
- 방법 요약:
  1) `voices-fetcher` 컨테이너가 Hugging Face 경로에서 보이스(.onnx, .json) 다운로드
  2) 영구 볼륨 `voices`에 저장 후 `tts-backend`(OpenTTS)에 `/data/local/voices:ro`로 마운트
  3) `depends_on`(service_completed_successfully)로 보이스 준비 후 백엔드 기동

## 수동 테스트 가이드 (로컬)
```bash
cd server/tts_server/docker
# 기본 구동(업스트림 OpenTTS + TTS Server)
docker compose -f docker/compose.yml up -d --build
# (옵션) 보이스 자동 다운로드 구성 사용 시
docker compose -f docker/compose.fixed2.yml up -d --build
curl -sS "http://localhost:5502/api/tts?text=hello" --output test.wav
aplay test.wav # 또는 시스템 재생기
```

### 한국어 보이스 사용 방법(OpenTTS)
1) 사용 가능한 보이스 조회(호스트 → OpenTTS):
```bash
curl -sS http://localhost:5500/api/voices | jq '.' | less
```
또는 프록시 경유:
```bash
curl -sS http://localhost:5502/api/voices | python -m json.tool
```
2) 목록에서 Piper 한국어 보이스 ID를 선택(예: `ko_KR-kss-low`, `piper-kss-korean`)
3) 프록시 경유 테스트(보이스 파라미터 지정, URL 인코딩 안전):
```bash
curl -G "http://localhost:5502/api/tts" \
  --data-urlencode "voice=piper:ko_KR-kss-low" \
  --data-urlencode "text=안녕하세요, 테스트입니다" \
  -o ko.wav
```
4) 기본 보이스로 고정하려면 환경변수 조정:
 - `server/tts_server/docker/compose.yml`(또는 `compose.fixed2.yml`)의 `TTS_DEFAULT_VOICE` 값을 한국어 보이스 ID로 변경
 - Flutter `.env.dev`의 `TTS_DEFAULT_VOICE`도 동일 값으로 변경 후 앱에서 환경 리로드

## 현황 업데이트 (2025-09-28)
- Piper 한국어 모델 온보딩 상태 개선 및 스크립트/마운트 정리 완료
  - `server/tts_server/docker/compose.fixed3.yml`
    - `voices-fetcher` 권한 오류 해결: `user: "0:0"`로 실행하여 `/voices` 볼륨에 쓰기 보장
    - 다운로드 URL을 모델 카드와 일치하도록 수정(`piper-kss-korean.onnx(.json)`)
    - `tts-backend` 마운트 정리:
      - `voices:/data/local/voices` (상위는 rw 권장)
      - `../models/piper-onnx-kss-korean:/data/local/voices/piper/piper-kss-korean:ro`
  - 정규화 스크립트 추가: `server/tts_server/script/normalize_piper_models.sh`
    - 로컬/볼륨 내 파일명을 `model.onnx`, `model.onnx.json`으로 통일
    - Piper 스캔 경로(`/voices/piper/<voice-id>/`)에 복사하여 인식 보장
    - 실제 Compose 볼륨명 자동 탐지(`*_voices`, 컨테이너 마운트, 환경변수 `VOLUME_NAME` 우선)
  - 문제 원인과 대책
    - 보이스 미노출 원인: 경로가 `/data/local/voices/piper/<id>/`가 아님, 파일명이 `model.*` 아님, 상위 마운트가 `:ro`라 바인드 타깃 생성 실패
    - 대책: 정규화 스크립트 실행 → 상위 rw 또는 볼륨 내 디렉터리 사전 생성 → 재기동 후 `/api/voices` 확인

### 빠른 점검/테스트
```bash
# 정규화 실행(볼륨명 자동탐지)
bash server/tts_server/script/normalize_piper_models.sh

# 재기동
docker compose -f server/tts_server/docker/compose.fixed3.yml up -d tts-backend

# 보이스 확인
curl -sS http://localhost:5500/api/voices | python -m json.tool | grep -i piper | cat

# 합성
curl -G "http://localhost:5500/api/tts" \
  --data-urlencode "voice=piper:ko_KR-kss-low" \
  --data-urlencode "text=안녕하세요, 테스트입니다" \
  -o out.wav
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
# 예: 한국어 보이스 ID로 교체(아래 조회 절차 참고)
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
