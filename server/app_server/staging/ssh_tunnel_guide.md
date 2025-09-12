# SSH 터널 설정 가이드

## 🔧 SSH 터널 설정 개요

### 기본 명령어
```bash
ssh -i "iot_db_key_pair.pem" -L 0.0.0.0:15432:localhost:5432 ubuntu@ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com
```

### 환경 변수 설정
| 변수명 | 값 | 설명 |
|--------|----|----|
| `SSH_TUNNEL_ENABLE` | `true` | SSH 터널 활성화 |
| `SSH_TUNNEL_LOCAL_PORT` | `15432` | 로컬 포트 |
| `SSH_TUNNEL_REMOTE_HOST` | `localhost` | 원격 호스트 (EC2 내부) |
| `SSH_TUNNEL_REMOTE_PORT` | `5432` | 원격 포트 (PostgreSQL) |
| `SSH_TUNNEL_BASTION_HOST` | `ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com` | Bastion 호스트 |
| `SSH_TUNNEL_USER` | `ubuntu` | SSH 사용자 |
| `SSH_TUNNEL_KEY_PATH` | `/app/secret/iot_db_key_pair.pem` | SSH 키 파일 경로 |

## 🚀 자동 실행 방법

### 1. Docker Compose로 실행
```bash
# 로컬 개발 환경
docker compose -f docker/compose.base.yml -f docker/compose.local.yml --env-file secret/.env.local up -d

# 프로덕션 환경
docker compose -f docker/compose.base.yml -f docker/compose.prod.yml --env-file secret/.env.prod up -d
```

### 2. 수동 실행
```bash
# SSH 터널만 실행
python scripts/ssh_tunnel.py

# 연결 테스트
python scripts/test_ssh_tunnel.py
```

## 🔍 연결 테스트

### 1. SSH 터널 상태 확인
```bash
# 포트 사용 확인
netstat -an | grep 15432

# 프로세스 확인
ps aux | grep ssh
```

### 2. 데이터베이스 연결 테스트
```bash
# 테스트 스크립트 실행
python scripts/test_ssh_tunnel.py

# 직접 연결 테스트
psql "postgresql://svc_dev:IOT_dev_123!@#@0.0.0.0:15432/iot_care"
```

## 🛠️ 문제 해결

### 1. SSH 키 권한 오류
```bash
chmod 600 secret/iot_db_key_pair.pem
```

### 2. 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :15432

# 프로세스 종료
kill -9 <PID>
```

### 3. SSH 연결 실패
```bash
# SSH 연결 테스트
ssh -i secret/iot_db_key_pair.pem ubuntu@ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com

# 상세 로그로 SSH 터널 실행
ssh -i secret/iot_db_key_pair.pem -v -L 0.0.0.0:15432:localhost:5432 ubuntu@ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com
```

## 📊 모니터링

### 1. SSH 터널 로그 확인
```bash
# Docker 로그 확인
docker logs <ssh-tunnel-container-id>

# 실시간 로그 확인
docker logs -f <ssh-tunnel-container-id>
```

### 2. 헬스체크
```bash
# Docker 헬스체크
docker inspect <ssh-tunnel-container-id> | grep Health

# 포트 연결 테스트
telnet 0.0.0.0 15432
```

## 🔒 보안 고려사항

1. **SSH 키 파일 권한**: 600으로 설정
2. **네트워크 접근**: 0.0.0.0 바인딩으로 모든 인터페이스에서 접근 가능
3. **방화벽 설정**: 필요시 15432 포트만 허용
4. **로그 모니터링**: SSH 연결 실패 시 알림 설정

## 📝 사용 예시

### 다른 프로그램에서 DB 접근
```python
import asyncpg

# SSH 터널을 통한 DB 연결
conn = await asyncpg.connect(
    "postgresql://svc_dev:IOT_dev_123!@#@0.0.0.0:15432/iot_care"
)
```

### 환경 변수 사용
```python
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_APP_URL')
conn = await asyncpg.connect(db_url)
```
