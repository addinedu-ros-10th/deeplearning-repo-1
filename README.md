# 노인공경 (R.F.T.E) - 스마트 케어 하우스 프로젝트

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [모노레포 구조](#모노레포-구조)
- [팀 구성](#팀-구성)
- [기술 스택](#기술-스택)
- [빠른 시작](#빠른-시작)
- [주요 기능](#주요-기능)
- [프로젝트 현황](#프로젝트-현황)
- [문서](#문서)
- [향후 계획](#향후-계획)

## 📋 프로젝트 개요

**노인공경 (R.F.T.E)**는 LLM, Deep Learning, Machine Learning 등 인공지능 기술을 활용하여 독거노인으로 대표되는 취약계층 1인 가구를 위한 스마트 케어 하우스를 개발하는 프로젝트입니다.

이번 프로젝트는 **Deep Learning을 중점적으로 다루면서** 제반 기술들을 포함시켜서 진행됩니다.

### 🎯 주요 목표
- **낙상 감지**: YOLO 기반 실시간 낙상 감지 시스템
- **자세 분석**: MediaPipe를 활용한 포즈 추정 및 분석
- **스마트 케어**: AI 기반 건강 상태 모니터링 및 알림 시스템
- **데이터 관리**: ML 모델 및 실험 데이터 관리 시스템
- **자율 주행**: 로봇/드론을 활용한 자율 이동 시스템
- **하드웨어 통합**: IoT 센서 및 임베디드 시스템 연동

## 🏗️ 모노레포 구조

모노레포 방식으로 관리되는 이 리포지토리에서는 **AI, Server, App, Utils** 카테고리 아래의 각 프로젝트들을 통합 관리합니다.

```
deeplearning-repo-1/
├── AI/                           # AI/DL 모듈
│   ├── DL/                      # 딥러닝 관련 코드
│   │   ├── fall_dataset/        # 낙상 감지 데이터셋
│   │   ├── fall_detection/      # 낙상 감지 모델
│   │   └── yolo_detection_and_pose/ # YOLO + MediaPipe 통합
│   └── LLM/                     # 대화형 AI 챗봇 (향후 추가)
├── Server/                       # 서버/API 모듈
│   ├── app_server/              # FastAPI 기반 백엔드
│   └── ai_server/               # AI 모델 서빙 전용 서버 (향후 추가)
├── App/                         # 애플리케이션 모듈
│   ├── web/                     # 웹 프론트엔드 (향후 추가)
│   └── mobile/                  # 모바일 앱 (향후 추가)
├── Utils/                       # 유틸리티 모듈 (향후 추가)
├── docs/                        # 프로젝트 문서
└── venv/                        # 가상환경
```

## 👥 팀 구성

| 이름 | 역할 | 담당 영역 |
|------|------|-----------|
| **박수현** | 팀장 | 인프라 세팅, 인공지능 서버, 유틸, 인공지능 훈련 등 개발, 기획, 설계문서 작성, 팀 관리 |
| **서지민** | 팀원 | 귀염둥이, 인공지능 훈련, 인공지능 개발, 패쓰 플래닝 개발 |
| **신동진** | 팀원 | 인공지능 훈련 모듈 개발(테스트, 훈련, 분석 등), 엠베드 개발 |
| **정광민** | 팀원 | 귀염둥이2, 인공지능 훈련, 인공지능 개발, 자율 주행 개발, 하드웨어 개발, 엠베드 개발 |
| **정규호** | 팀원 | 인프라 세팅, 어플리케이션 서버, GUI, 유틸, 인공지능 훈련 등 개발, 기획, 설계문서 작성 |

## 🔧 기술 스택

### Backend & Infrastructure
- **Backend**: FastAPI, SQLAlchemy, APScheduler
- **Database**: PostgreSQL (SSH 터널), Alembic 마이그레이션
- **Cache**: Redis
- **Infrastructure**: Docker, Nginx, Docker Compose
- **Architecture**: 헥사고날 아키텍처, 의존성 주입
- **Monitoring**: SQLAdmin, Health Checks, 로깅 시스템

### AI/ML
- **Deep Learning**: YOLO (Ultralytics), MediaPipe, OpenCV
- **Machine Learning**: scikit-learn, pandas, numpy
- **Computer Vision**: 실시간 객체 탐지, 포즈 추정
- **Data Processing**: CSV 로깅, 데이터셋 관리
- **LLM**: (향후 추가 예정)
- **Embedded**: (향후 추가 예정)

### Frontend & Mobile
- **Web**: (향후 추가 예정)
- **Mobile**: (향후 추가 예정)

## 🚀 빠른 시작

### Docker Compose로 실행
```bash
# 로컬 개발 환경
./docker/docker-compose-manager.sh local

# 운영 환경
./docker/docker-compose-manager.sh prod

# 상태 확인
./docker/docker-compose-manager.sh status

# API 테스트
./docker/docker-compose-manager.sh test
```

### 수동 실행
```bash
# 환경변수 설정
export DB_APP_URL="postgresql+asyncpg://svc_dev:IOT_dev_123%21%40%23@localhost:15432/iot_care"
export ML_DB_URL="postgresql+asyncpg://svc_dev:IOT_dev_123%21%40%23@localhost:15432/iot_care"

# 가상환경 활성화
source venv/app_server/bin/activate

# 서버 실행
cd server/app_server
python -m app.main
```

## 📚 주요 기능

### 🤖 AI/DL 모듈 (현재 구현됨)
- **낙상 감지 시스템**: YOLO 기반 실시간 낙상 감지 (`AI/DL/fall_detection/`)
  - Ultralytics YOLO 래퍼 클래스 (`YoloDetector`)
  - 실시간 프레임 처리 및 탐지 결과 반환
  - 웹캠/비디오 파일 입력 지원
- **자세 분석 시스템**: MediaPipe를 활용한 포즈 추정 (`AI/DL/yolo_detection_and_pose/`)
  - YOLO + MediaPipe 통합 프로젝트
  - 실시간 포즈 추정 및 분석
  - 186개 낙상 관련 비디오 데이터셋 보유
- **데이터셋 관리**: 낙상 감지용 YOLO 데이터셋 (`AI/DL/fall_dataset/`)
  - 훈련/검증 데이터 분할 (images, labels)
  - CSV 기반 로깅 시스템

### 🖥️ Server/API 모듈 (현재 구현됨)
- **FastAPI 백엔드**: 헥사고날 아키텍처 기반 (`server/app_server/`)
  - 통합된 메인 애플리케이션 (`app/main.py`)
  - 스케줄러, SQLAdmin, ML Registry 통합
- **ML Registry API**: 데이터셋 및 실험 관리 RESTful API
  - Dataset/Experiment CRUD API 완전 구현
  - 헥사고날 아키텍처 + 의존성 주입
  - PostgreSQL ML 스키마 기반
- **스케줄러 시스템**: APScheduler 기반 작업 스케줄링
  - 실시간 스케줄 관리 및 실행
  - 데이터베이스 기반 작업 저장
- **관리자 패널**: SQLAdmin 기반 데이터베이스 관리
  - 웹 기반 데이터베이스 관리 인터페이스
  - 스케줄 작업 모니터링
- **인프라 관리**: Docker Compose 환경
  - 환경별 설정 (local, prod)
  - Nginx 프록시, Redis 캐싱
  - SSH 터널 자동화

### 🔧 개발 도구 (현재 구현됨)
- **Docker Compose 관리**: 환경별 실행 스크립트
  - `./docker/docker-compose-manager.sh` 명령어 지원
  - 로컬/운영 환경 자동 관리
- **환경 관리**: 다중 환경 지원
  - `.env.local`, `.env.prod` 환경별 설정
  - 보안 파일 관리 (SSH 키, 환경 변수)

### 🚀 향후 구현 예정 기능
- **대화형 AI 챗봇**: LLM 기반 자연어 처리 (`AI/LLM/`)
- **자율 주행**: 로봇/드론 자율 이동 시스템
- **하드웨어 통합**: IoT 센서 및 임베디드 시스템 (`AI/Embedded/`)
- **웹/모바일 앱**: 사용자 인터페이스 (`App/web/`, `App/mobile/`)
- **AI 모델 서빙**: 전용 AI 서버 (`Server/ai_server/`)

## 📊 프로젝트 현황

### ✅ 완료된 작업 (2025-09-15 기준)
- [x] **기본 인프라 구축**: Docker, PostgreSQL, Redis, Nginx
- [x] **FastAPI 백엔드 서버**: 헥사고날 아키텍처 기반 통합 서버
- [x] **ML Registry API**: Dataset/Experiment CRUD API 완전 구현
- [x] **스케줄러 시스템**: APScheduler 기반 실시간 작업 관리
- [x] **관리자 패널**: SQLAdmin 기반 데이터베이스 관리 인터페이스
- [x] **낙상 감지 모델**: YOLO 기반 실시간 낙상 감지 시스템
- [x] **자세 분석 시스템**: MediaPipe를 활용한 포즈 추정
- [x] **데이터셋 관리**: 186개 낙상 관련 비디오 데이터셋 보유
- [x] **환경 관리**: Docker Compose 환경별 설정 및 자동화
- [x] **개발 도구**: 통합 관리 스크립트 및 문서화

### 🔄 진행 중인 작업
- [ ] **Alembic 마이그레이션**: ML 스키마 테이블 생성 마이그레이션
- [ ] **성능 최적화**: API 응답 속도 및 메모리 사용량 최적화
- [ ] **테스트 자동화**: 단위 테스트 및 통합 테스트 구축

### 📋 향후 계획 (Phase별)
- [ ] **Phase 1**: LLM 챗봇 개발 (`AI/LLM/`)
- [ ] **Phase 2**: 자율 주행 시스템 및 하드웨어 통합
- [ ] **Phase 3**: 웹/모바일 앱 개발 (`App/web/`, `App/mobile/`)
- [ ] **Phase 4**: AI 모델 서빙 서버 (`Server/ai_server/`)
- [ ] **Phase 5**: 임베디드 시스템 통합 (`AI/Embedded/`)

## 📖 문서

- [개발 가이드](docs/development_guide.md)
- [프로젝트 현황](docs/project_overview.md)
- [AI/DL 모듈 상태](docs/ai_dl_status.md)
- [서버/API 상태](docs/server_api_status.md)
- [팀 관리 문서](server/app_server/docs/app_server_build_action_items_20250912.md)

## 🎯 향후 계획

### Phase 1: AI/DL 모듈 확장 (2025 Q4)
- **AI/LLM/**: 대화형 AI 챗봇 개발
  - 자연어 처리 기반 독거노인 상담 시스템
  - 음성 인식 및 음성 합성 기능
- **AI/Embedded/**: 임베디드 시스템 통합
  - IoT 센서 데이터 수집 및 처리
  - 실시간 모니터링 시스템

### Phase 2: 서버 인프라 확장 (2026 Q1)
- **Server/ai_server/**: AI 모델 서빙 전용 서버
  - YOLO, MediaPipe 모델 서빙 API
  - 실시간 추론 서비스
- **Server/iot_server/**: IoT 센서 데이터 처리 서버
  - 센서 데이터 수집 및 분석
  - 실시간 알림 시스템

### Phase 3: 애플리케이션 개발 (2026 Q2)
- **App/web/**: 웹 프론트엔드 개발
  - 관리자 대시보드
  - 실시간 모니터링 인터페이스
- **App/mobile/**: 모바일 앱 개발
  - 가족/보호자용 알림 앱
  - 응급상황 신고 기능

### Phase 4: 유틸리티 및 도구 (2026 Q3)
- **Utils/**: 공통 유틸리티 및 도구 개발
  - 데이터 전처리 도구
  - 모델 성능 분석 도구
  - 배포 자동화 도구

## 🤝 기여 방법

### 개발 참여
1. **이슈 생성**: 버그 리포트 또는 기능 제안
2. **브랜치 생성**: `feat/모듈명--기능명` 형식
3. **코드 작성**: 기존 아키텍처 패턴 준수
4. **테스트**: 단위 테스트 및 통합 테스트 작성
5. **PR 생성**: 상세한 변경사항 설명 포함

### 모듈별 기여 영역
- **AI/DL**: 낙상 감지, 자세 분석, 데이터셋 관리
- **Server**: API 개발, 데이터베이스 설계, 인프라 구축
- **App**: 사용자 인터페이스, 사용자 경험 개선
- **Utils**: 공통 도구, 성능 최적화, 문서화

---

**노인공경 (R.F.T.E)** - Respect For The Elderly

> 이 프로젝트는 독거노인을 위한 스마트 케어 하우스 시스템을 통해 사회적 약자를 돌보는 기술적 솔루션을 제공합니다.
