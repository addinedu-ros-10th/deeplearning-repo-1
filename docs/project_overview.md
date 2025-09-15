# 프로젝트 개요

## 🎯 프로젝트 목표
**노인공경 (R.F.T.E) - 딥러닝 기반 낙상 감지 시스템**

실시간 비디오 스트림을 통해 노인의 낙상 상황을 자동으로 감지하고 알림을 제공하는 AI 시스템을 개발합니다.

## 🏗️ 프로젝트 구조

### 1. AI/DL 모듈
- **YOLO 기반 객체 감지**: 사람과 낙상 상황 감지
- **MediaPipe 포즈 추정**: 실시간 포즈 키포인트 추출
- **낙상 감지 알고리즘**: 포즈 변화 패턴 분석을 통한 낙상 판단

### 2. Server/API 모듈
- **FastAPI 기반 REST API**: 실시간 데이터 처리 및 관리
- **헥사고날 아키텍처**: 확장 가능한 모듈형 구조
- **스케줄러 시스템**: 정기적인 데이터 처리 및 분석 작업
- **관리자 대시보드**: SQLAdmin 기반 웹 관리 인터페이스

## 🚀 주요 기능

### AI/DL 기능
- 실시간 비디오 스트림 처리
- YOLO 모델을 통한 사람 감지
- MediaPipe를 통한 포즈 키포인트 추출
- 낙상 상황 자동 감지 및 분류
- CSV 기반 데이터 로깅 및 분석

### Server/API 기능
- RESTful API 엔드포인트
- 실시간 데이터 수집 및 저장
- 스케줄된 작업 관리
- 웹 기반 관리자 인터페이스
- Docker 기반 컨테이너화

## 🛠️ 기술 스택

### AI/DL
- **Python 3.12**
- **YOLO**: 객체 감지
- **MediaPipe**: 포즈 추정
- **OpenCV**: 비디오 처리
- **Pandas**: 데이터 처리

### Server/API
- **FastAPI**: 웹 프레임워크
- **PostgreSQL**: 데이터베이스
- **Redis**: 캐시 및 세션 관리
- **APScheduler**: 작업 스케줄링
- **SQLAdmin**: 관리자 인터페이스
- **Docker**: 컨테이너화
- **Nginx**: 리버스 프록시

## 📊 현재 개발 현황

### ✅ 완료된 작업
1. **기본 인프라 구축**
   - Python 3.12 환경 설정
   - Docker Compose 환경 구축
   - PostgreSQL 데이터베이스 연결
   - Redis 캐시 서버 구성

2. **스케줄러 시스템**
   - APScheduler 기반 스케줄러 구현
   - SQLAdmin 관리자 화면 구축
   - 스케줄 작업 CRUD API 구현

3. **데이터베이스 관리**
   - Alembic 마이그레이션 시스템
   - scheduled_jobs 테이블 생성
   - 다중 데이터베이스 바인딩

4. **웹 서버 구성**
   - Nginx 프록시 서버 설정
   - FastAPI 애플리케이션 연동
   - Swagger UI 문서화

### 🔄 현재 상태
- **API 서버**: ✅ 정상 동작 (http://localhost:8000)
- **데이터베이스**: ✅ 연결 성공 (SSH 터널)
- **스케줄러**: ✅ 완전 정상 동작
- **관리자 화면**: ✅ SQLAdmin 완전 정상
- **Nginx 프록시**: ✅ 정상 동작 (http://localhost:80)
- **Docker Compose**: ✅ 모든 서비스 Up(healthy)

## 🎯 향후 계획

### Phase 1: AI/DL 모듈 통합
- YOLO 모델 학습 및 최적화
- MediaPipe 포즈 추정 정확도 향상
- 낙상 감지 알고리즘 개선

### Phase 2: 실시간 처리 시스템
- 비디오 스트림 실시간 처리
- 낙상 감지 결과 실시간 전송
- 알림 시스템 구축

### Phase 3: 모니터링 및 최적화
- 성능 모니터링 시스템
- 로깅 및 분석 도구
- 사용자 인터페이스 개선

## 📁 프로젝트 구조

```
deeplearning-repo-1/
├── AI/DL/                          # AI/DL 모듈
│   ├── fall_detection/            # 낙상 감지 모듈
│   ├── yolo_detection_and_pose/   # YOLO + 포즈 추정
│   └── pyproject.toml            # AI/DL 의존성
├── server/app_server/             # Server/API 모듈
│   ├── app/                      # FastAPI 애플리케이션
│   ├── docker/                   # Docker 설정
│   ├── docs/                     # 프로젝트 문서
│   └── pyproject.toml           # Server 의존성
└── docs/                         # 프로젝트 전체 문서
```

## 🔧 개발 환경 설정

### 필수 요구사항
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (원격 또는 로컬)
- Redis

### 빠른 시작
```bash
# 1. 저장소 클론
git clone <repository-url>
cd deeplearning-repo-1

# 2. Server 모듈 실행
cd server/app_server
docker compose -f docker/compose.base.yml -f docker/compose.local.yml up -d

# 3. AI/DL 모듈 실행
cd ../../AI/DL
pip install -e .
```

## 📞 연락처 및 지원

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해주세요.

---

*최종 업데이트: 2025-09-13*


