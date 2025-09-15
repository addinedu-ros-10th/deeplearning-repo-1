# Server/API 모듈 개발 현황

## 📊 현재 상태

### ✅ 완료된 작업

#### 1. 기본 인프라 구축
- **Python 3.12 환경**: 최신 Python 버전으로 설정
- **Docker Compose 환경**: 멀티 컨테이너 환경 구축
  - `compose.base.yml`: 공통 설정
  - `compose.local.yml`: 로컬 개발 환경
  - `compose.prod.yml`: 프로덕션 환경
- **PostgreSQL 데이터베이스**: SSH 터널을 통한 원격 연결
- **Redis 캐시 서버**: 세션 및 캐시 관리

#### 2. 헥사고날 아키텍처 구현
- **도메인 레이어**: 엔티티, 값 객체, 도메인 서비스, 포트 정의
- **애플리케이션 레이어**: 유즈케이스, DTO, 트랜잭션 경계 설정
- **어댑터 레이어**: HTTP, 리포지토리, 스케줄러 어댑터 구현
- **인프라 레이어**: 데이터베이스, 캐시, DI 컨테이너 설정

#### 3. 스케줄러 시스템
- **APScheduler 기반**: 비동기 스케줄러 구현
- **SQLAdmin 관리자 화면**: 웹 기반 관리 인터페이스
- **스케줄 작업 CRUD API**: RESTful API 엔드포인트
- **수동 작업 실행**: 관리자 화면에서 즉시 실행 가능

#### 4. 데이터베이스 관리
- **Alembic 마이그레이션**: 데이터베이스 스키마 버전 관리
- **scheduled_jobs 테이블**: 스케줄 작업 저장
- **다중 데이터베이스 바인딩**: legacy, app 엔진 분리
- **비삭제 정책**: 기존 데이터 보호

#### 5. 웹 서버 구성
- **Nginx 프록시 서버**: 리버스 프록시 설정
- **FastAPI 애플리케이션**: 비동기 웹 프레임워크
- **Swagger UI**: API 문서 자동 생성
- **CORS 설정**: 크로스 오리진 요청 처리

#### 6. 환경 관리
- **환경별 설정 파일**: `.env.local`, `.env.prod`
- **Docker Compose 환경별 구성**: 로컬/프로덕션 분리
- **보안 파일 관리**: SSH 키, 환경 변수 보호

### 🔄 현재 상태 (2025-09-13)

#### ✅ 완전 정상 작동 중인 기능들

1. **API 서버 (FastAPI)**
   - Health Check: `http://localhost:8000/health` → "healthy" 응답
   - 스케줄러 API: `http://localhost/api/v1/scheduled-jobs` → 2개 작업 로드
   - Swagger UI: `http://localhost/docs` → 정상 접근

2. **SQLAdmin 관리자 패널**
   - 메인 페이지: `http://localhost/admin/` → 200 OK
   - 스케줄 작업 목록: `http://localhost/admin/scheduled-job/list` → 200 OK
   - 데이터 표시: 2개 스케줄 작업 정상 표시
   - 검색/정렬/페이지네이션: 모든 기능 정상 작동

3. **Nginx 프록시 서버**
   - Health Check: `http://localhost/healthz` → "ok" 응답
   - API 프록시: 모든 API 엔드포인트 정상 프록시
   - 정적 파일 서빙: CSS/JS 리소스 정상 로드

4. **데이터베이스 연결**
   - SSH 터널: 포트 15432 정상 활성화
   - PostgreSQL: `iot_care` 데이터베이스 연결 성공
   - 스케줄 작업: 2개 작업 정상 로드 및 관리

5. **Docker Compose 환경**
   - 모든 서비스: Up(healthy) 상태
   - API 컨테이너: 정상 실행, 오류 없음
   - Nginx 컨테이너: 정상 실행, 헬스체크 통과
   - Redis 컨테이너: 정상 실행, 헬스체크 통과

### 🛠️ 해결된 주요 문제들

#### 1. Docker Compose 실행 문제들
- **볼륨 마운트 오류**: `invalid mount path: '.'` → 환경변수 기본값 설정으로 해결
- **포트 충돌**: 8000 포트 중복 사용 → 포트 분리 구성으로 해결
- **Nginx www-data 사용자 오류**: Alpine Linux 호환성 문제 → `user nginx;` 설정으로 해결
- **환경변수 치환 미적용**: `--env-file` 옵션 사용으로 해결

#### 2. SSH 터널 자동화
- **Docker 컨테이너 내 SSH 터널 문제**: 호스트 기반 스크립트로 변경
- **포트 진단 및 자동 복구**: 포트 사용 상태 확인 후 적절한 조치 수행

#### 3. SQLAdmin 관리자 패널 문제들
- **이벤트 루프 충돌**: `asyncio.run()` 호출 문제 → 동기 `get_sync_engine()` 사용으로 해결
- **Internal Server Error**: 필터 설정 및 검색 플레이스홀더 오류 → 설정 수정으로 해결
- **관리자 패널 접근 불가**: `/admin` 경로 500 오류 → 완전 해결됨

#### 4. 스케줄러 시스템 문제들
- **데이터베이스 연결 실패**: `0.0.0.0` → `host.docker.internal` 변경으로 해결
- **스케줄러 직렬화 오류**: `Schedulers cannot be serialized` → 정적 메서드 사용으로 해결
- **작업 로드 실패**: Connection refused 오류 → Docker 네트워킹 설정으로 해결
- **데이터베이스 연결 검증**: Python 기반 연결 테스트로 안정성 확보

### 📁 프로젝트 구조

```
server/app_server/
├── app/                          # FastAPI 애플리케이션
│   ├── domain/                   # 도메인 레이어
│   │   ├── entities/            # 엔티티
│   │   ├── value_objects/       # 값 객체
│   │   ├── services/            # 도메인 서비스
│   │   └── ports/               # 포트 인터페이스
│   ├── application/             # 애플리케이션 레이어
│   │   ├── use_cases/          # 유즈케이스
│   │   └── dto/                # DTO
│   ├── adapters/               # 어댑터 레이어
│   │   ├── http/               # HTTP 어댑터
│   │   ├── repositories/       # 리포지토리 어댑터
│   │   ├── scheduler/          # 스케줄러 어댑터
│   │   ├── ai/                 # AI 어댑터
│   │   ├── file/               # 파일 어댑터
│   │   ├── tcp/                # TCP 어댑터
│   │   └── streaming/          # 스트리밍 어댑터
│   ├── infrastructure/         # 인프라 레이어
│   │   ├── db/                 # 데이터베이스
│   │   ├── cache/              # 캐시
│   │   └── di/                 # 의존성 주입
│   ├── admin/                  # 관리자 인터페이스
│   ├── jobs/                   # 스케줄 작업
│   ├── services/               # 서비스
│   └── main.py                 # 애플리케이션 진입점
├── docker/                     # Docker 설정
│   ├── compose.base.yml        # 공통 설정
│   ├── compose.local.yml       # 로컬 환경
│   ├── compose.prod.yml        # 프로덕션 환경
│   ├── python.Dockerfile       # Python 컨테이너
│   ├── nginx.Dockerfile        # Nginx 컨테이너
│   └── nginx/                  # Nginx 설정
├── docs/                       # 프로젝트 문서
├── scripts/                    # 유틸리티 스크립트
├── tests/                      # 테스트
└── pyproject.toml             # 의존성 관리
```

### 🎯 다음 단계

#### 1. AI/DL 모듈 통합
- YOLO 모델 API 엔드포인트 개발
- MediaPipe 포즈 추정 API 구현
- 실시간 비디오 스트림 처리

#### 2. 실시간 처리 시스템
- WebSocket 연결 관리
- 실시간 데이터 전송
- 낙상 감지 결과 처리

#### 3. 모니터링 및 로깅
- 구조화된 로깅 시스템
- 성능 메트릭 수집
- 알림 시스템 구축

### 📊 시스템 메트릭

- **서비스 상태**: 100% 정상 (3/3 서비스 Up)
- **API 응답**: 100% 성공 (모든 엔드포인트 200 OK)
- **데이터베이스**: 정상 연결 (SSH 터널 활성화)
- **스케줄러**: 정상 작동 (2개 작업 로드)
- **관리자 패널**: 완전 정상 (모든 기능 작동)

### 🔧 기술 스택

- **FastAPI**: 비동기 웹 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **Redis**: 인메모리 데이터 저장소
- **APScheduler**: 작업 스케줄링
- **SQLAdmin**: 관리자 인터페이스
- **Docker**: 컨테이너화
- **Nginx**: 리버스 프록시
- **Alembic**: 데이터베이스 마이그레이션

---

*최종 업데이트: 2025-09-13*


