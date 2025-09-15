# 환경 변수 가이드

## 📋 환경 변수 목록

### 🔧 기본 애플리케이션 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `APP_ENV` | 애플리케이션 환경 | `local` | `production` |
| `PYTHON_VERSION` | Python 버전 | `3.12` | `3.12` |
| `PROJECT_NAME` | 프로젝트 이름 | `App Server` | `App Server` |
| `API_V1_STR` | API 버전 경로 | `/api/v1` | `/api/v1` |
| `DEBUG` | 디버그 모드 | `true` | `false` |

### 🗄️ 데이터베이스 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `DB_MODE` | DB 접속 모드 | `local_ssh` | `aws_internal` |
| `DB_APP_URL` | 신규 DB URL | SSH 터널 | AWS 내부망 |
| `DB_LEGACY_URL` | 레거시 DB URL | SSH 터널 | AWS 내부망 |

### 🔐 SSH 터널 설정 (로컬만)
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SSH_TUNNEL_ENABLE` | SSH 터널 활성화 | `true` |
| `SSH_TUNNEL_LOCAL_PORT` | 로컬 포트 | `15432` |
| `SSH_TUNNEL_REMOTE_HOST` | RDS 호스트 | `<rds-host>` |
| `SSH_TUNNEL_REMOTE_PORT` | RDS 포트 | `5432` |
| `SSH_TUNNEL_BASTION_HOST` | Bastion 호스트 | `<bastion-ip>` |
| `SSH_TUNNEL_USER` | SSH 사용자 | `ubuntu` |
| `SSH_TUNNEL_KEY_PATH` | SSH 키 경로 | `~/.ssh/id_rsa` |

### 🗃️ Redis 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` | `redis://redis:6379/0` |
| `REDIS_PASSWORD` | Redis 비밀번호 | `` | `<set-redis-password>` |
| `REDIS_DB` | Redis DB 번호 | `0` | `0` |

### 📁 파일 저장소 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `FILES_BASE_DIR` | 파일 저장 경로 | `/app/data/files` | `/app/data/files` |
| `FILES_MAX_SIZE` | 최대 파일 크기 | `10485760` (10MB) | `52428800` (50MB) |
| `FILES_ALLOWED_TYPES` | 허용 파일 타입 | 기본 이미지/문서 | 확장된 타입 |

### 👤 관리자 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `ADMIN_USERNAME` | 관리자 사용자명 | `admin` | `admin` |
| `ADMIN_PASSWORD` | 관리자 비밀번호 | `admin123` | `<set-strong-password>` |
| `ADMIN_EMAIL` | 관리자 이메일 | `admin@localhost` | `admin@yourdomain.com` |

### 🔗 Google Drive 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GDRIVE_ENABLE` | Google Drive 활성화 | `false` |
| `GDRIVE_CLIENT_SECRETS` | 클라이언트 시크릿 경로 | `/app/secrets/client_secrets.json` |
| `GDRIVE_CREDENTIALS` | 자격증명 경로 | `/app/secrets/credentials.json` |

### 📝 로깅 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `LOG_LEVEL` | 로그 레벨 | `DEBUG` | `INFO` |
| `LOG_FORMAT` | 로그 포맷 | `json` | `json` |
| `LOG_FILE` | 로그 파일 경로 | `/app/logs/app.log` | `/app/logs/app.log` |

### 🌐 CORS 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `CORS_ORIGINS` | 허용 오리진 | `["http://localhost:3000", ...]` | `["https://yourdomain.com", ...]` |
| `CORS_ALLOW_CREDENTIALS` | 자격증명 허용 | `true` | `true` |
| `CORS_ALLOW_METHODS` | 허용 메서드 | `["GET", "POST", ...]` | `["GET", "POST", ...]` |
| `CORS_ALLOW_HEADERS` | 허용 헤더 | `["*"]` | `["*"]` |

### 🔑 JWT 인증 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `JWT_SECRET_KEY` | JWT 시크릿 키 | `your-super-secret-jwt-key...` | `<set-strong-jwt-secret-key>` |
| `JWT_ALGORITHM` | JWT 알고리즘 | `HS256` | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 액세스 토큰 만료 시간 | `30` | `60` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 리프레시 토큰 만료 시간 | `7` | `30` |

### 🛡️ 보안 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `SECRET_KEY` | 애플리케이션 시크릿 키 | `your-super-secret-key...` | `<set-strong-secret-key>` |
| `BCRYPT_ROUNDS` | Bcrypt 라운드 수 | `12` | `14` |
| `SESSION_COOKIE_SECURE` | 보안 쿠키 | `false` | `true` |
| `SESSION_COOKIE_HTTPONLY` | HTTP 전용 쿠키 | `true` | `true` |
| `SESSION_COOKIE_SAMESITE` | SameSite 정책 | `lax` | `strict` |
| `HTTPS_ONLY` | HTTPS 전용 | `false` | `true` |

### 🚀 API 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `API_HOST` | API 호스트 | `0.0.0.0` | `0.0.0.0` |
| `API_PORT` | API 포트 | `8000` | `8000` |
| `API_WORKERS` | 워커 수 | `1` | `4` |
| `API_RELOAD` | 자동 리로드 | `true` | `false` |

### ⏰ 스케줄러 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SCHEDULER_TIMEZONE` | 시간대 | `Asia/Seoul` |
| `SCHEDULER_MAX_WORKERS` | 최대 워커 수 | `10` (로컬) / `20` (프로덕션) |
| `SCHEDULER_COALESCE` | 작업 병합 | `true` |

### 📊 모니터링 설정
| 변수명 | 설명 | 로컬 | 프로덕션 |
|--------|------|------|----------|
| `PROMETHEUS_ENABLE` | Prometheus 활성화 | `false` | `true` |
| `PROMETHEUS_PORT` | Prometheus 포트 | `9090` | `9090` |
| `GRAFANA_ENABLE` | Grafana 활성화 | `false` | `true` |
| `GRAFANA_PORT` | Grafana 포트 | `3000` | `3000` |
| `ELK_STACK_ENABLE` | ELK 스택 활성화 | `false` | `true` |

### ⚡ 성능 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DATABASE_POOL_SIZE` | DB 풀 크기 | `20` |
| `DATABASE_MAX_OVERFLOW` | DB 최대 오버플로우 | `30` |
| `REDIS_POOL_SIZE` | Redis 풀 크기 | `20` |

### 💾 백업 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `BACKUP_ENABLE` | 백업 활성화 | `true` |
| `BACKUP_SCHEDULE` | 백업 스케줄 | `0 2 * * *` (매일 새벽 2시) |
| `BACKUP_RETENTION_DAYS` | 백업 보관 일수 | `30` |

### 📧 알림 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SLACK_WEBHOOK_URL` | Slack 웹훅 URL | `<set-slack-webhook-url>` |
| `EMAIL_SMTP_HOST` | SMTP 호스트 | `<set-smtp-host>` |
| `EMAIL_SMTP_PORT` | SMTP 포트 | `587` |
| `EMAIL_SMTP_USER` | SMTP 사용자 | `<set-smtp-user>` |
| `EMAIL_SMTP_PASSWORD` | SMTP 비밀번호 | `<set-smtp-password>` |

### 🧪 테스트 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `TEST_DATABASE_URL` | 테스트 DB URL | `postgresql+asyncpg://test_user:test_pass@127.0.0.1:15432/test_db` |
| `TEST_REDIS_URL` | 테스트 Redis URL | `redis://redis:6379/1` |

### 🛠️ 개발 도구 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `PYTEST_ADDOPTS` | Pytest 옵션 | `-v --tb=short` |
| `BLACK_LINE_LENGTH` | Black 라인 길이 | `88` |
| `RUFF_LINE_LENGTH` | Ruff 라인 길이 | `88` |
| `MYPY_STRICT` | MyPy 엄격 모드 | `true` |

## 🔒 보안 주의사항

1. **민감한 정보는 절대 Git에 커밋하지 마세요**
2. **프로덕션 환경에서는 강력한 비밀번호 사용**
3. **JWT 시크릿 키는 충분히 복잡하게 설정**
4. **HTTPS 환경에서는 SESSION_COOKIE_SECURE=true 설정**
5. **데이터베이스 비밀번호는 정기적으로 변경**

## 📝 사용법

### 로컬 개발
```bash
cp secret/.env.local .env.local
# 필요한 값들을 실제 값으로 수정
docker compose -f docker/compose.base.yml -f docker/compose.local.yml --env-file .env.local up -d
```

### 프로덕션 배포
```bash
cp secret/.env.prod .env.prod
# 모든 <set-*> 값들을 실제 값으로 수정
docker compose -f docker/compose.base.yml -f docker/compose.prod.yml --env-file .env.prod up -d
```
