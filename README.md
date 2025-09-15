# deeplearning-repo-1

**노인공경 (R.F.T.E) - 스마트 케어 하우스 프로젝트**

LLM, Deep Learning, Machine Learning 등 인공지능 기술을 활용해서 독거노인으로 대표되는 취약계층 1인 가구를 위한 스마트 케어 하우스를 개발하는 프로젝트입니다.

이번 프로젝트는 Deep Learning을 중점적으로 다루면서 제반 기술들을 포함시켜서 진행됩니다.

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [모노레포 구조](#-모노레포-구조)
- [팀원 소개](#-팀원-소개)
- [빠른 시작](#-빠른-시작)
- [현재 개발 현황](#-현재-개발-현황)
- [프로젝트 구조](#-프로젝트-구조)
- [기술 스택](#-기술-스택)
- [문서](#-문서)
- [향후 계획](#-향후-계획)
- [기여하기](#-기여하기)
- [연락처](#-연락처)

## 🎯 프로젝트 개요

모노레포 방식으로 관리되는 이 리포지토리에서는 **AI**, **Server**, **App**, **Utils** 카테고리 아래의 각 프로젝트들을 통합 관리합니다.

- **AI**: 딥러닝 모델 개발, 훈련, 추론
- **Server**: 백엔드 API 서버, 데이터베이스, 인프라
- **App**: 프론트엔드 애플리케이션, 모바일 앱
- **Utils**: 공통 유틸리티, 도구, 스크립트

자세한 내용은 [프로젝트 개요](docs/project_overview.md)를 참조하세요.

## 🏗️ 모노레포 구조

```
deeplearning-repo-1/
├── AI/                    # AI 프로젝트들
│   ├── DL/               # Deep Learning 프로젝트
│   └── LLM/              # Large Language Model 프로젝트 (향후 추가)
├── Server/               # Server 프로젝트들
│   ├── app_server/       # FastAPI 기반 API 서버
│   └── ai_server/        # AI 추론 서버 (향후 추가)
├── App/                  # App 프로젝트들
│   ├── web/              # 웹 애플리케이션 (향후 추가)
│   └── mobile/           # 모바일 애플리케이션 (향후 추가)
└── docs/                 # 프로젝트 전체 문서
```

*앞으로 모노레포 카테고리 아래에 프로젝트가 추가될 때마다 해당 정보를 업데이트합니다.*

## 👥 팀원 소개

| 역할 | 이름 | 담당 업무 |
|------|------|-----------|
| **팀장** | 박수현 | 인프라 세팅, 인공지능 서버, 유틸, 인공지능 훈련 등 개발, 기획, 설계문서 작성, 팀 관리 |
| **팀원** | 서지민 | 귀염둥이, 인공지능 훈련, 인공지능 개발, 패쓰 플래닝 개발 |
| **팀원** | 신동진 | 인공지능 훈련 모듈 개발(테스트, 훈련, 분석 등), 엠베드 개발 |
| **팀원** | 정광민 | 귀염둥이2, 인공지능 훈련, 인공지능 개발, 자율 주행 개발, 하드웨어 개발, 엠베드 개발 |
| **팀원** | 정규호 | 인프라 세팅, 어플리케이션 서버, GUI, 유틸, 인공지능 훈련 등 개발, 기획, 설계문서 작성 |

*팀원 정보는 앞으로도 업데이트될 예정입니다.*

## 🚀 빠른 시작

### Server/API 모듈 실행

```bash
cd server/app_server
docker compose -f docker/compose.base.yml -f docker/compose.local.yml up -d
```

### AI/DL 모듈 실행

```bash
cd AI/DL
pip install -e .
python -m fall_detection.infer.yolo_detector
```

자세한 설정 방법은 [개발 가이드](docs/development_guide.md)를 참조하세요.

## 📊 현재 개발 현황

### ✅ 완료된 작업

#### AI/DL 모듈
- YOLO 데이터셋 구축 완료
- 낙상 감지 모듈 구현
- MediaPipe 포즈 추정 데이터 수집
- 데이터 처리 도구 개발

#### Server/API 모듈
- FastAPI 기반 REST API 구축
- 헥사고날 아키텍처 구현
- 스케줄러 시스템 완성
- SQLAdmin 관리자 화면 구축
- Docker Compose 환경 구축
- PostgreSQL + Redis 데이터베이스 연동

### 🔄 현재 상태

- **API 서버**: ✅ 정상 동작 (http://localhost:8000)
- **관리자 화면**: ✅ 정상 동작 (http://localhost/admin)
- **데이터베이스**: ✅ 연결 성공 (SSH 터널)
- **Docker 환경**: ✅ 모든 서비스 정상 작동

자세한 현황은 [AI/DL 모듈 현황](docs/ai_dl_status.md)과 [Server/API 모듈 현황](docs/server_api_status.md)을 참조하세요.

## 🏗️ 프로젝트 구조

### 현재 구현된 프로젝트

```
deeplearning-repo-1/
├── AI/
│   └── DL/                       # Deep Learning 프로젝트
│       ├── fall_detection/       # 낙상 감지 모듈
│       ├── yolo_detection_and_pose/  # YOLO + 포즈 추정
│       └── pyproject.toml        # AI/DL 의존성
├── Server/
│   └── app_server/               # FastAPI 기반 API 서버
│       ├── app/                  # FastAPI 애플리케이션
│       ├── docker/               # Docker 설정
│       ├── docs/                 # 프로젝트 문서
│       └── pyproject.toml        # Server 의존성
└── docs/                         # 프로젝트 전체 문서
```

### 향후 추가 예정인 프로젝트

- **AI/LLM/**: Large Language Model 프로젝트
- **Server/ai_server/**: AI 추론 서버
- **App/web/**: 웹 애플리케이션
- **App/mobile/**: 모바일 애플리케이션

## 🛠️ 기술 스택

### AI (Deep Learning)
- **Python 3.12**: 메인 프로그래밍 언어
- **YOLO**: 객체 감지 모델
- **MediaPipe**: 포즈 추정 및 비전 처리
- **OpenCV**: 컴퓨터 비전 라이브러리
- **Pandas**: 데이터 처리 및 분석

### Server (Backend)
- **FastAPI**: 비동기 웹 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **Redis**: 인메모리 데이터 저장소
- **APScheduler**: 작업 스케줄링
- **SQLAdmin**: 관리자 인터페이스
- **Docker**: 컨테이너화
- **Nginx**: 리버스 프록시

### App (Frontend) - 향후 추가 예정
- **Web**: React, Vue.js, Next.js
- **Mobile**: React Native, Flutter

## 📚 문서

- [프로젝트 개요](docs/project_overview.md) - 프로젝트 전체 개요
- [AI/DL 모듈 현황](docs/ai_dl_status.md) - AI/DL 개발 현황
- [Server/API 모듈 현황](docs/server_api_status.md) - Server/API 개발 현황
- [개발 가이드](docs/development_guide.md) - 개발 환경 설정 및 가이드

## 🎯 향후 계획

**스마트 케어 하우스 완성을 위한 4단계 개발 청사진**

1. **AI 모듈 확장** (1-2개월): YOLO 모델 최적화 및 LLM 통합으로 지능형 감지 시스템 구축
2. **Server 인프라 강화** (2-3개월): AI 추론 서버 구축 및 실시간 처리 시스템 개발
3. **App 개발** (3-4개월): 웹/모바일 애플리케이션으로 사용자 인터페이스 제공
4. **시스템 통합** (4-5개월): 하드웨어 연동 및 실시간 모니터링으로 완전한 스마트 케어 하우스 구현

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feat/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'feat(api): ADD, amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feat/amazing-feature`)
5. Pull Request를 생성합니다

## 📞 연락처

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해주세요.

---

*최종 업데이트: 2025-09-13*
