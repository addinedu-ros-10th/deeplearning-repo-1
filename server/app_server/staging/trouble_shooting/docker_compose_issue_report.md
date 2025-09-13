# Docker Compose 실행 이슈 처리내역
_작성일: 2025-09-13_

본 문서는 `docker compose` 기동 과정에서 발생한 문제들을 **문제점 → 원인 → 해결책** 순으로 정리한 처리내역입니다. 각 항목에는 실무에서 바로 재현/검증 가능한 **명령어와 설정 스니펫**을 포함했습니다.

---

## 환경 요약
- Docker Compose: v2.24.6
- 베이스 이미지: `python:3.12-slim`, `nginx:1.27-alpine`, `redis:7-alpine`
- 주요 서비스: `api`, `nginx`, `redis`

---

## 1) `invalid mount path: '.'` (볼륨 타겟이 상대경로)
**증상**
```
Cannot create container for service api: invalid volume specification: 'docker_files-data:.:rw'
```
**원인**
- `files-data:${{FILES_BASE_DIR}}` 에서 **`${{FILES_BASE_DIR}}`가 비어** 타겟 경로가 `.`(상대)로 해석됨
- Compose 변수 치환은 **환경변수/.env**만 사용하고, `env_file:` 값은 **치환에 미사용**

**해결**
```yaml
# compose.base.yml
services:
  api:
    volumes:
      - ../app:/app/app
      - files-data:${{FILES_BASE_DIR:-/app/files}}   # 기본값으로 방어
      - ../secret:/app/secret:ro
```
또는 실행 시
```bash
docker compose --env-file ./secret/.env.local -f ./docker/compose.base.yml -f ./docker/compose.local.yml up --build
```

**검증**
```bash
docker compose -f ./docker/compose.base.yml -f ./docker/compose.local.yml   --env-file ./secret/.env.local config | sed -n '1,200p'
```

---

## 2) 8000 포트 충돌
**증상**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```
**원인**
- `api`가 `8000:8000`, `nginx`도 `8000:80`로 퍼블리시하면 **호스트 8000 중복**

**해결 패턴**
- **A. Nginx만 외부 공개(권장)**  
  - `api`: `ports` 제거, `expose: ["8000"]`만
  - `nginx`: dev=`8080:80`, prod=`80:80`(+`443:443`)
- **B. 개발 중 API 직접 호출 필요**  
  - `api`: `8000:8000` 유지
  - `nginx`: `8080:80` 등 **다른 포트** 사용

**확인**
```bash
sudo ss -ltnp | grep :8000 || true
docker ps --format 'table {{ .Names }}	{{ .Ports }}' | grep 8000 || true
```

---

## 3) Nginx `getpwnam("www-data") failed`
**증상**
```
nginx: [emerg] getpwnam("www-data") failed in /etc/nginx/nginx.conf:3
```
**원인**
- `nginx:alpine`에는 기본 계정이 **`nginx`**, `www-data`는 없음
- 컨테이너 내에 반영된 conf가 `user www-data;` 였음

**해결**
- conf 최상단을 **`user nginx;`**
- dev에선 conf **바인드 마운트**로 즉시 반영
```yaml
services:
  nginx:
    volumes:
      - ../nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```
- 운영에선 Dockerfile `COPY` 경로 재확인 후 `--no-cache` 빌드

---

## 4) `nginx -T`: `no configuration file provided: not found`
**원인**
- 기본 conf를 백업만 하고, 신규 conf `COPY`가 **경로 불일치/캐시**로 실패

**해결**
- dev: conf 바인드 마운트 사용(위와 동일)
- prod: Dockerfile의 `COPY nginx/nginx.conf /etc/nginx/nginx.conf`가 **build context=`..`** 기준으로
  `server/app_server/nginx/nginx.conf`를 가리키는지 확인 후 재빌드
```bash
docker compose build --no-cache nginx && docker compose up -d
```

---

## 5) 업스트림을 `127.0.0.1:8000`로 사용
**원인**
- Nginx 컨테이너 내부 `127.0.0.1:8000`엔 FastAPI가 없음 → Docker 네트워크에선 **서비스명:포트**

**해결**
```nginx
upstream fastapi_backend {
    server api:8000;
    keepalive 32;
}
```

---

## 6) `resolving names at run time requires upstream ... to be in shared memory`
**원인**
- `server api:8000 resolve;` 사용 시 Nginx가 **zone(공유 메모리)** 필요

**해결 (택1)**
- 간단: `resolve` 제거
```nginx
upstream fastapi_backend { server api:8000; }
```
- 유지: `resolver` + `zone` 추가
```nginx
resolver 127.0.0.11 ipv6=off;
upstream fastapi_backend {
  zone fastapi_backend_zone 64k;
  server api:8000 resolve;
}
```

---

## 7) Healthcheck 경로 불일치
**원인**
- Dockerfile(nginx) `/health` vs conf `/healthz`

**해결**
- Nginx 자체 응답 헬스 추가
```nginx
location /healthz {
  access_log off;
  return 200 "ok\n";
  add_header Content-Type text/plain;
}
```
- Dockerfile도 `/healthz`로 통일
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3   CMD curl -f http://localhost/healthz || exit 1
```

---

## 8) 환경변수 경고(치환 미적용)
**원인**
- `${{VAR}}` 치환은 `.env`/환경변수만 사용, `env_file:` 값은 **치환 대상 아님**

**해결**
- 루트 `.env` 배치 또는 `--env-file` 사용
- 변수 기본값 문법으로 방어
```yaml
- files-data:${{FILES_BASE_DIR:-/app/files}}
```

---

## 9) Redis 경고 (비치명)
**증상**
```
Memory overcommit must be enabled!
```
**해결(선택)**
```bash
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## 최종 권장 설정(발췌)

**`nginx.conf` 핵심**
```nginx
user  nginx;
worker_processes  auto;

http {
  upstream fastapi_backend {
      server api:8000;   # Docker 서비스명
      keepalive 32;
  }

  server {
    listen 80;
    server_name localhost;

    # nginx 자체 헬스
    location /healthz {
      access_log off;
      return 200 "ok\n";
      add_header Content-Type text/plain;
    }

    # API 프록시
    location /api/ {
      proxy_pass http://fastapi_backend;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }
  }
}
```

**포트 구성(Dev 권장)**
- `api`: `8000:8000`(직접 호출 필요 시), 아니면 `expose: ["8000"]`만
- `nginx`: `8080:80`(충돌 방지), 운영은 `80:80`(+`443:443`)

---

## 빠른 검증 체크리스트
```bash
# 최종 머지 결과 점검
docker compose --env-file ./secret/.env.local   -f ./docker/compose.base.yml -f ./docker/compose.local.yml   config | sed -n '1,200p'

# 기동
docker compose --env-file ./secret/.env.local   -f ./docker/compose.base.yml -f ./docker/compose.local.yml   up -d --build

# Nginx 설정 검증
docker compose exec nginx sh -lc 'nginx -t && nginx -T | sed -n "1,80p"'

# 헬스/프록시 확인
curl -i http://localhost/healthz
curl -i http://localhost/docs
```
