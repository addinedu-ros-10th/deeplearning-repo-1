# 🎤 Voice Interface App (Flutter)

## 📱 개요
**Flutter 기반 종합 음성 인터페이스 솔루션**

### ✨ 주요 기능
- 🎤 **STT (Speech-to-Text)**: 실시간 음성 인식
- 🔊 **TTS (Text-to-Speech)**: 자연스러운 음성 합성
- 🤖 **AI 대화**: OpenAI GPT 연동
- 🔔 **실시간 알림**: WebSocket 기반 즉시 알림
- 👥 **사용자 관리**: 인적 자원 네트워크 시각화
- 🎨 **직관적 UI**: 음파형 시각화 및 터치 인터페이스

### 🏗️ 아키텍처
- **Frontend**: Flutter 3.24+ / Dart 3.5+
- **Backend**: REST API + WebSocket
- **AI**: OpenAI GPT API
- **State**: Provider 패턴

## 🚀 빠른 시작

### 📋 요구사항
- Flutter 3.24+
- Dart 3.5+
- Web/Android/iOS 지원

### ⚡ 설치 및 실행
```bash
# 1. 의존성 설치
flutter pub get

# 2. Web에서 실행 (권장)
flutter run -d chrome --web-port 8081

# 3. 환경변수 설정 (선택사항)
flutter run -d chrome \
  --dart-define=USE_DOTENV=true \
  --dart-define=APP_ENV=dev
```

## 🔧 환경 설정

### 환경변수 파일
```
assets/env/
├── .env.dev     # 개발 환경
└── .env.prod    # 운영 환경
```

### 주요 설정값
```env
# OpenAI API
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com
OPENAI_MODEL=gpt-3.5-turbo

# 서버 API
IOT_BASE_URL=http://ec2-13-125-249-77.ap-northeast-2.compute.amazonaws.com
DL_BASE_URL=http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com

# 알림 설정
NOTIFY_ENABLED=true
```

## 🏗️ 프로젝트 구조

```
lib/
├── core/                    # 핵심 유틸리티
│   ├── env/                # 환경변수 관리
│   └── http/               # HTTP 클라이언트
├── features/
│   ├── auth/               # 인증 시스템
│   ├── voice/              # 음성 인터페이스
│   ├── users/              # 사용자 관리
│   └── notification/       # 알림 시스템
└── main.dart               # 앱 진입점
```

## 🧪 테스트

### 단위 테스트 실행
```bash
# 전체 테스트
flutter test

# 특정 테스트
flutter test test/features/voice/ui/button_click_test.dart
```

### 테스트 커버리지
- ✅ 버튼 클릭 이벤트: 100%
- ✅ UI 구조 검증: 100%
- ✅ 상태 변경 로직: 100%
- ✅ 터치 이벤트 처리: 100%

## 📚 문서

- [개발 현황](./docs/development_status.md)
- [TDD 개발 가이드](./docs/tdd_button_development_guide.md)
- [API 문서](./docs/api_reference.md)

## 🎯 주요 기능

### 1. 음성 인터페이스
- 실시간 음성 인식 (STT)
- 자연스러운 음성 합성 (TTS)
- 음파형 시각화
- AI 대화 시스템

### 2. 사용자 관리
- 사용자 목록 및 상세 정보
- 인적 자원 네트워크 시각화
- 관계자 정보 조회

### 3. 알림 시스템
- 실시간 알림 수신
- 사용자별 알림 필터링
- 알림 다이얼로그 표시

### 4. UI/UX
- 직관적인 터치 인터페이스
- 반응형 디자인
- 애니메이션 효과

## 🔄 개발 프로세스

### TDD (Test-Driven Development)
1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트 통과하는 최소 코드 작성
3. **Refactor**: 코드 품질 개선

### Git 워크플로우
- 기능별 브랜치 생성
- 의미있는 커밋 메시지
- 정기적인 코드 리뷰

## 🐛 문제 해결

### 자주 발생하는 문제
1. **버튼 클릭 안됨**: Stack 구조 및 터치 이벤트 확인
2. **STT/TTS 충돌**: _isTtsPlaying 상태 관리 확인
3. **알림 수신 안됨**: WebSocket 연결 상태 확인

### 디버깅 팁
- 콘솔 로그 확인
- Flutter Inspector 사용
- 테스트 실행으로 문제 격리

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **문서**: `/docs` 디렉토리
- **테스트**: `flutter test` 명령어

---

**버전**: v1.0.0  
**마지막 업데이트**: 2025-01-27  
**상태**: 🟢 활발한 개발 중
