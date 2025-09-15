# 개발 가이드

## 🚀 빠른 시작

### 1. 저장소 클론 및 설정

```bash
# 저장소 클론
git clone <repository-url>
cd deeplearning-repo-1

# Git 메시지 템플릿 설정
cd server/app_server
chmod +x scripts/setup_git_template.sh
./scripts/setup_git_template.sh
```

### 2. Server/API 모듈 실행

```bash
cd server/app_server

# 환경 변수 파일 복사
cp secret/.env.local .env.local

# SSH 터널 자동 설정 및 Docker Compose 실행
chmod +x scripts/docker_compose_manager.sh
./scripts/docker_compose_manager.sh

# 또는 수동 실행
docker compose -f docker/compose.base.yml -f docker/compose.local.yml --env-file .env.local up -d --build
```

### 3. AI/DL 모듈 실행

```bash
cd AI/DL

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -e .

# 모듈 실행
python -m fall_detection.infer.yolo_detector
```

## 🔧 개발 환경 설정

### 필수 요구사항

- **Python 3.12+**
- **Docker & Docker Compose**
- **PostgreSQL** (원격 또는 로컬)
- **Redis**
- **Git**

### 권장 개발 도구

- **IDE**: VS Code, PyCharm
- **데이터베이스**: pgAdmin, DBeaver
- **API 테스트**: Postman, Insomnia
- **컨테이너**: Docker Desktop

## 📁 프로젝트 구조 이해

### 모노레포 구조

```
deeplearning-repo-1/
├── AI/DL/                    # AI/DL 모듈
│   ├── fall_detection/      # 낙상 감지
│   ├── yolo_detection_and_pose/  # YOLO + 포즈
│   └── pyproject.toml      # AI/DL 의존성
├── server/app_server/       # Server/API 모듈
│   ├── app/                # FastAPI 애플리케이션
│   ├── docker/             # Docker 설정
│   ├── docs/               # 프로젝트 문서
│   └── pyproject.toml     # Server 의존성
└── docs/                   # 프로젝트 전체 문서
```

### 헥사고날 아키텍처

```
app/
├── domain/                  # 도메인 레이어 (비즈니스 로직)
│   ├── entities/           # 엔티티
│   ├── value_objects/      # 값 객체
│   ├── services/           # 도메인 서비스
│   └── ports/              # 포트 (인터페이스)
├── application/            # 애플리케이션 레이어 (유즈케이스)
│   ├── use_cases/         # 유즈케이스
│   └── dto/               # DTO
├── adapters/              # 어댑터 레이어 (외부 연동)
│   ├── http/              # HTTP 어댑터
│   ├── repositories/      # 리포지토리 어댑터
│   ├── scheduler/         # 스케줄러 어댑터
│   └── ...                # 기타 어댑터들
└── infrastructure/        # 인프라 레이어 (기술 구현)
    ├── db/                # 데이터베이스
    ├── cache/             # 캐시
    └── di/                # 의존성 주입
```

## 🛠️ 개발 워크플로우

### 1. 브랜치 전략

```bash
# 기능 개발
git checkout -b feat/feature-name

# 버그 수정
git checkout -b fix/bug-description

# 문서 업데이트
git checkout -b docs/update-documentation
```

### 2. 커밋 메시지 규칙

프로젝트는 표준화된 커밋 메시지 형식을 사용합니다:

```
<type>(<scope>): <action>, <description>

# 예시
feat(api): ADD, User Authentication API
fix(scheduler): EDIT, Job Execution Logic
docs(readme): UPDATE, Project Status
```

**타입**: `feat`, `fix`, `docs`, `refactor`, `test`, `config`
**스코프**: `api`, `scheduler`, `admin`, `docker`, `docs`
**액션**: `ADD`, `EDIT`, `UPDATE`, `DELETE`, `FIX`

### 3. 코드 리뷰 프로세스

1. **로컬 테스트**: 모든 테스트 통과 확인
2. **Docker 테스트**: 컨테이너 환경에서 테스트
3. **Pull Request 생성**: 상세한 설명과 함께
4. **코드 리뷰**: 팀원 리뷰 후 머지

## 🧪 테스트 가이드

### 1. 단위 테스트

```bash
cd server/app_server
pytest tests/unit/ -v
```

### 2. 통합 테스트

```bash
pytest tests/integration/ -v
```

### 3. E2E 테스트

```bash
pytest tests/e2e/ -v
```

### 4. API 테스트

```bash
# 서버 실행 후
curl http://localhost:8000/health
curl http://localhost/api/v1/scheduled-jobs
```

## 🐳 Docker 개발 환경

### 1. 컨테이너 상태 확인

```bash
docker compose ps
```

### 2. 로그 확인

```bash
# 모든 서비스 로그
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f api
docker compose logs -f nginx
```

### 3. 컨테이너 재시작

```bash
# 특정 서비스 재시작
docker compose restart api

# 모든 서비스 재시작
docker compose restart
```

### 4. 컨테이너 내부 접속

```bash
# API 컨테이너 접속
docker compose exec api bash

# 데이터베이스 접속
docker compose exec db psql -U app_user -d app_db
```

## 📊 모니터링 및 디버깅

### 1. 헬스체크

```bash
# API 서버
curl http://localhost:8000/health

# Nginx 프록시
curl http://localhost/healthz

# 데이터베이스 연결
curl http://localhost/api/v1/scheduled-jobs
```

### 2. 로그 레벨 설정

```bash
# .env.local 파일에서
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### 3. 성능 모니터링

```bash
# 컨테이너 리소스 사용량
docker stats

# 데이터베이스 연결 상태
docker compose exec api python -c "from app.infrastructure.db.session import get_app_engine; print('DB Connected')"
```

## 🔐 보안 가이드

### 1. 환경 변수 관리

- **민감한 정보**: `.env.local` 파일에 저장
- **공개 정보**: `.env.example` 파일에 템플릿 제공
- **Git 무시**: `.gitignore`에 `.env.local` 추가

### 2. SSH 키 관리

```bash
# SSH 키 권한 설정
chmod 600 secret/iot_db_key_pair.pem

# SSH 터널 테스트
ssh -i secret/iot_db_key_pair.pem -L 15432:localhost:5432 ubuntu@<bastion-ip>
```

### 3. 데이터베이스 보안

- **비밀번호**: 강력한 비밀번호 사용
- **접근 제한**: IP 화이트리스트 설정
- **암호화**: SSL/TLS 연결 사용

## 📚 추가 리소스

### 1. 문서 링크

- [프로젝트 개요](project_overview.md)
- [AI/DL 모듈 현황](ai_dl_status.md)
- [Server/API 모듈 현황](server_api_status.md)
- [Git 메시지 템플릿 가이드](../server/app_server/docs/git_message_template_guide.md)

### 2. 외부 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Docker Compose 가이드](https://docs.docker.com/compose/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [Redis 문서](https://redis.io/documentation)

### 3. 문제 해결

- **일반적인 문제**: [FAQ](faq.md)
- **버그 리포트**: GitHub Issues
- **기능 요청**: GitHub Discussions

---

*최종 업데이트: 2025-09-13*


