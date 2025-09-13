# Git Message Template 가이드

## 📋 개요

이 프로젝트는 모노레포 구조로 관리되며, 일관된 Git 커밋 메시지 작성을 위해 커스텀 템플릿을 사용합니다.

## 🚀 초기 설정

### 1. 자동 설정 (권장)

```bash
# 서버 프로젝트 디렉토리에서 실행
cd server/app_server
./scripts/setup_git_template.sh
```

### 2. 수동 설정

```bash
# 모노레포 루트에서 실행
git config --global commit.template .gitmessage
git config commit.template .gitmessage
```

## 📝 커밋 메시지 형식

### 기본 형식
```
<type>(<scope>): <action>, <description>

<body>

<footer>
```

### Type (필수)
커밋의 성격을 나타내는 접두사:

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 변경 (README, API 문서, 주석 등)
- `style`: 코드 스타일 변경 (포맷팅, 세미콜론, 들여쓰기 등)
- `refactor`: 코드 리팩토링 (기능 변경 없이 코드 구조 개선)
- `test`: 테스트 코드 추가/수정
- `chore`: 빌드, 설정 파일, 패키지 관리 등
- `ci`: CI/CD 설정 변경
- `build`: 빌드 시스템 변경
- `revert`: 이전 커밋 되돌리기

### Scope (필수)
변경된 영역을 명시:

**프로젝트 레벨:**
- `server`: 서버 프로젝트
- `client`: 클라이언트 프로젝트
- `docs`: 문서
- `docker`: Docker 관련
- `scripts`: 스크립트

**서버 프로젝트 세부 영역:**
- `api`: API 엔드포인트
- `admin`: 관리자 패널
- `scheduler`: 스케줄러
- `db`: 데이터베이스
- `nginx`: 웹 서버
- `auth`: 인증/권한
- `config`: 설정 파일

### Action (필수)
수행한 작업을 동사로 명시:

- `ADD`: 새로운 기능/파일 추가
- `EDIT`: 기존 기능/파일 수정
- `DELETE`: 기능/파일 삭제
- `UPDATE`: 업데이트/개선
- `FIX`: 버그 수정
- `REFACTOR`: 리팩토링
- `REMOVE`: 제거
- `CREATE`: 생성
- `IMPLEMENT`: 구현
- `CONFIGURE`: 설정
- `OPTIMIZE`: 최적화

### Description (필수)
변경사항을 간결하게 설명:

- 50자 이내로 작성
- 첫 글자는 대문자
- 마침표로 끝내지 않음
- 명령형 어조 사용
- 구체적이고 명확하게 작성

### Body (선택사항)
- 변경사항의 상세 설명
- 왜 변경했는지 설명
- 어떻게 변경했는지 설명

### Footer (선택사항)
- Breaking Changes
- 관련 이슈 번호
- 리뷰어 정보

## 💡 사용 예시

### 좋은 예시
```bash
# 기능 추가
feat(api): ADD, User Authentication API
feat(admin): CREATE, SQLAdmin Management Panel
feat(scheduler): IMPLEMENT, Job Scheduling System

# 버그 수정
fix(api): FIX, Database Connection Error
fix(scheduler): FIX, Serialization Issue
fix(admin): FIX, Internal Server Error

# 문서 업데이트
docs(api): UPDATE, API Documentation
docs(server): ADD, Development Guide
docs(docker): UPDATE, Setup Instructions

# 리팩토링
refactor(api): REFACTOR, Database Connection Logic
refactor(admin): OPTIMIZE, SQLAdmin Configuration
refactor(scheduler): IMPROVE, Job Execution Flow

# 설정 변경
chore(docker): UPDATE, Docker Compose Configuration
chore(scripts): ADD, Deployment Automation Script
chore(config): CONFIGURE, Environment Variables

# 테스트
test(api): ADD, Unit Tests for User API
test(scheduler): UPDATE, Integration Tests
test(admin): ADD, SQLAdmin Test Cases
```

### 나쁜 예시
```bash
# ❌ 너무 간단함
fix: bug fix
feat: new feature

# ❌ 스코프 없음
feat: add user api
fix: database error

# ❌ 액션 없음
feat(api): user authentication
fix(scheduler): serialization

# ❌ 대문자 사용 (액션 제외)
Feat(api): ADD, User API
fix(API): FIX, Database Error

# ❌ 마침표 사용
feat(api): ADD, User API.
fix(scheduler): FIX, Serialization Issue.

# ❌ 너무 길거나 모호함
feat(api): ADD, A very long description that exceeds the recommended length
fix: something
```

## ⚡ 빠른 시작 가이드

### 1. 가장 간단한 사용법

#### 템플릿 사용 (권장)
```bash
# 1. 파일 스테이징
git add .

# 2. 커밋 (템플릿 자동 로드)
git commit

# 3. 편집기에서 첫 번째 줄 수정
# # feat(api): ADD, User Authentication API
# ↓ (첫 번째 # 제거)
# feat(api): ADD, User Authentication API

# 4. 저장 및 종료
```

#### 직접 메시지 작성
```bash
git commit -m "feat(api): ADD, User Authentication API"
```

### 2. 자주 사용하는 패턴

```bash
# 새 기능 추가
feat(api): ADD, User Authentication API
feat(admin): CREATE, SQLAdmin Management Panel

# 버그 수정
fix(scheduler): FIX, Serialization Issue
fix(api): FIX, Database Connection Error

# 문서 업데이트
docs(server): UPDATE, API Documentation
docs(docker): ADD, Setup Guide

# 리팩토링
refactor(admin): OPTIMIZE, SQLAdmin Configuration
refactor(api): REFACTOR, Database Connection Logic

# 설정 변경
chore(docker): UPDATE, Docker Compose Configuration
chore(scripts): ADD, Deployment Script
```

## 🔧 상세한 Git 사용법

### 1. 기본 Git 워크플로우

#### 브랜치 생성 및 전환
```bash
# 새 기능 브랜치 생성
git checkout -b feature/user-authentication

# 기존 브랜치로 전환
git checkout main
git checkout develop
```

#### 파일 스테이징
```bash
# 특정 파일만 스테이징
git add app/main.py
git add docs/git_message_template_guide.md

# 모든 변경사항 스테이징
git add .

# 변경된 파일만 스테이징 (삭제된 파일 제외)
git add -u

# 대화형 스테이징 (파일별로 선택)
git add -i
```

#### 커밋 생성
```bash
# 템플릿 사용 (권장)
git commit

# 직접 메시지 작성
git commit -m "feat(api): ADD, User Authentication API"

# 여러 파일을 개별적으로 커밋
git add app/api/users.py
git commit -m "feat(api): ADD, User Registration Endpoint"

git add app/api/auth.py
git commit -m "feat(api): ADD, JWT Authentication Logic"
```

### 2. 템플릿 사용법

#### 템플릿이 로드된 편집기에서 작업
```bash
git commit
# 기본 편집기(Vim/Nano)가 열리고 템플릿이 로드됨
```

**📝 커밋 메시지 작성 위치:**
```
# <type>(<scope>): <action>, <description>  ← 여기에 커밋 메시지 작성
#
# <body>  ← 상세 설명 (선택사항)
#
# <footer>  ← 추가 정보 (선택사항)
```

**⚠️ 중요 안내:**
- **첫 번째 줄**에서 `#`을 제거하고 커밋 메시지를 작성하세요
- **주석(#으로 시작하는 줄)은 커밋 메시지에 포함되지 않습니다**
- 템플릿의 가이드 라인은 참고용이며, 실제 커밋에는 포함되지 않습니다

**Vim 사용 시:**
1. `i` 키를 눌러 편집 모드 진입
2. **첫 번째 줄**에서 `#`을 제거하고 커밋 메시지 작성 (예: `feat(api): ADD, User Authentication API`)
3. `Esc` 키를 눌러 명령 모드로 전환
4. `:wq` 입력 후 Enter로 저장 및 종료

**Nano 사용 시:**
1. **첫 번째 줄**에서 `#`을 제거하고 커밋 메시지 작성 (예: `feat(api): ADD, User Authentication API`)
2. `Ctrl + X`로 종료
3. `Y`로 저장 확인
4. Enter로 파일명 확인

#### 커밋 메시지 작성 팁
```bash
# 1. Type과 Scope 선택
feat(api): 

# 2. Action과 Description 추가
feat(api): ADD, User Authentication API

# 3. Body 추가 (선택사항)
feat(api): ADD, User Authentication API

- JWT 토큰 기반 인증 구현
- 로그인/로그아웃 엔드포인트 추가
- 사용자 권한 검증 로직 포함

# 4. Footer 추가 (선택사항)
feat(api): ADD, User Authentication API

- JWT 토큰 기반 인증 구현
- 로그인/로그아웃 엔드포인트 추가
- 사용자 권한 검증 로직 포함

Closes #123
Co-authored-by: John Doe <john@example.com>
```

### 3. 고급 Git 사용법

#### 커밋 수정
```bash
# 마지막 커밋 메시지 수정
git commit --amend

# 마지막 커밋에 파일 추가
git add forgotten_file.py
git commit --amend --no-edit

# 여러 커밋을 하나로 합치기 (Interactive Rebase)
git rebase -i HEAD~3
```

#### 커밋 히스토리 확인
```bash
# 커밋 히스토리 보기
git log --oneline
git log --graph --pretty=format:'%h -%d %s (%cr) <%an>'

# 특정 파일의 커밋 히스토리
git log --follow app/main.py

# 커밋 상세 정보 보기
git show <commit-hash>
```

#### 브랜치 관리
```bash
# 브랜치 목록 보기
git branch -a

# 원격 브랜치와 동기화
git fetch origin
git checkout -b feature/new-feature origin/feature/new-feature

# 브랜치 삭제
git branch -d feature/old-feature
git branch -D feature/force-delete
```

### 4. 모노레포 특화 사용법

#### 특정 프로젝트만 커밋
```bash
# 서버 프로젝트만 커밋
git add server/
git commit -m "feat(server): ADD, New API Endpoints"

# 문서만 커밋
git add docs/
git commit -m "docs(server): UPDATE, API Documentation"
```

#### 여러 프로젝트 동시 커밋
```bash
# 여러 프로젝트 변경사항을 하나의 커밋으로
git add server/ client/
git commit -m "feat(server,client): ADD, User Management System"

# 또는 개별적으로 커밋
git add server/
git commit -m "feat(server): ADD, User API Backend"

git add client/
git commit -m "feat(client): ADD, User Management UI"
```

### 5. 커밋 메시지 검증

#### 커밋 전 검토
```bash
# 스테이징된 파일 확인
git status

# 변경사항 미리보기
git diff --cached

# 커밋 메시지 형식 검증
# (프로젝트에 pre-commit hook 설정 시 자동 검증)
```

#### 커밋 후 검토
```bash
# 마지막 커밋 확인
git log -1

# 커밋 상세 정보 확인
git show HEAD

# 커밋 통계 확인
git show --stat HEAD
```

## 📚 추가 정보

### 모노레포 구조
```
/
├── .gitmessage          # Git 메시지 템플릿
├── server/              # 서버 프로젝트
│   └── app_server/
│       ├── scripts/
│       │   └── setup_git_template.sh
│       └── docs/
│           └── git_message_template_guide.md
├── client/              # 클라이언트 프로젝트 (예시)
└── docs/                # 공통 문서
```

### 설정 확인
```bash
# 현재 설정 확인
git config --global commit.template
git config commit.template

# 템플릿 파일 위치 확인
ls -la .gitmessage
```

## 🆘 문제 해결

### 템플릿이 로드되지 않는 경우
1. 파일 위치 확인: `ls -la .gitmessage`
2. Git 설정 확인: `git config commit.template`
3. 스크립트 재실행: `./scripts/setup_git_template.sh`

### 권한 오류
```bash
chmod +x scripts/setup_git_template.sh
```

### 템플릿 수정
모노레포 루트의 `.gitmessage` 파일을 직접 수정할 수 있습니다.

## 📖 참고 자료

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Commit Message Best Practices](https://chris.beams.io/posts/git-commit/)
- [Monorepo Best Practices](https://monorepo.tools/)
