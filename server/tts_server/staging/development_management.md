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
- FastAPI 서버 `/healthz`, `/api/tts` 라우트 추가
- Piper/Mimic3/OpenTTS 업스트림 프록시 지원 (WAV 스트림 반환)
- Docker compose로 Piper+TTS 서버 로컬 기동 가능

## 다음 일정
1. 통합 테스트: 실제 Piper 컨테이너와 end-to-end WAV 생성/재생 확인
2. 실패 시 재시도/백오프, 요청 로깅/메트릭 추가
3. 운영 구성 샘플(.env, env 파일 템플릿) 제공
4. `app_server`와 연동 가이드 및 헬스체크/장애 처리 흐름 문서화

## 수동 테스트 가이드 (로컬)
```bash
cd server/tts_server/docker
docker compose up --build -d
curl -sS "http://localhost:5502/api/tts?text=테스트" --output test.wav
aplay test.wav # 또는 시스템 재생기
```
