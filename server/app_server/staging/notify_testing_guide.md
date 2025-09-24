# Notify 기능 테스트 가이드

## 1) 사전 조건
- 환경 변수(플래그)를 켭니다:
  - `NOTIFY_ENABLE=true`
  - `NOTIFY_DISPATCH_ENABLE=true`
  - `NOTIFY_WS_ENABLE=true`
- Docker 실행 시 env 파일을 지정해 주입합니다.
  - 예: `docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml up -d`

## 2) Nginx 프록시(WebSocket) 확인
- 설정 경로: `docker/nginx/nginx.conf`
- 지원 경로:
  - `/api/*` → API 프록시
  - `/ws` → WebSocket 업그레이드
- 헬스체크: `http://localhost/healthz`

## 3) 수동 WebSocket 테스트 페이지
- 경로: `staging/tools/notify_ws_client.html`
- 사용법:
  - BASE_URL: `http://localhost` (또는 `http://localhost:8080` / `http://localhost:8000`)
  - user_id(UUID): 예) `11111111-1111-1111-1111-111111111111`
  - Connect → 브라우저 로그 창에서 수신 확인

## 4) 큐잉 API 호출
- 엔드포인트: `POST /api/v1/notify/queue`
- 예시(curl, Git Bash):
```
curl -X POST "$BASE_URL/api/v1/notify/queue" -H "Content-Type: application/json" -d '{"kind":"info","severity":"green","title":"Hello","body":"From curl","data":{"k":1},"recipients":["11111111-1111-1111-1111-111111111111"],"channel":"websocket"}'
```
- 전송 후: 디스패처가 `queued→sent→delivered` 전이를 수행하고, WebSocket 클라이언트로 메시지가 전달됩니다.

## 5) 읽음/확인 처리
- 딜리버리 ID가 있을 때:
  - `POST /api/v1/notify/deliveries/{delivery_id}/read`
  - `POST /api/v1/notify/deliveries/{delivery_id}/ack`

## 6) 문제 해결 체크
- BASE_URL은 프로토콜+호스트:포트만 입력(/api, /ws 추가 금지)
- Nginx 없이 직접 API 접근 시: `http://localhost:8000`를 BASE_URL로 입력
- 플래그 미설정 시 전송되지 않음 → env 파일 확인
- DB 연결/ENUM 오류 시: 로그(`[ENV] Startup config`, ORM ENUM 설정) 확인

## 7) 환경 변수 관리(현황/제안)
- 현황
  - Compose(base)에서 `.env.local` 기본, 실제 실행은 `--env-file`로 덮어씀
  - prod는 `compose.prod.yml`에서 `env_file: ../secret/.env.prod`로 강제
  - DB/Redis/로그/CORS/JWT 등은 이미 변수화됨
- 제안(통합 관리)
  - `server/app_server/secret/.env.example`에 Notify 플래그와 BASE_URL 예시 추가
  - `.env.local`(로컬), `.env.prod`(운영) 모두에 `NOTIFY_*` 플래그 명시
  - 문서(`staging/notify_testing_guide.md`)에 “어느 파일을 쓰는지”를 명시하고, `docker/docker-compose-manager.sh`에 `--env-file` 전달 옵션 고정

## 8) 빠른 점검 명령
```
# Nginx 건강 상태
curl -f http://localhost/healthz

# WS 접속(브라우저에서)
# Windows는 파일 탐색기에서 더블클릭
# Linux/Mac: xdg-open/open 명령으로 오픈

# Queue API
BASE_URL=http://localhost \
curl -X POST "$BASE_URL/api/v1/notify/queue" -H "Content-Type: application/json" -d '{"kind":"info","severity":"green","title":"Hello","body":"From curl","data":{"k":1},"recipients":["11111111-1111-1111-1111-111111111111"],"channel":"websocket"}'
```
