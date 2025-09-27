# 🔔 알림 시스템 클라이언트 및 테스트 도구

이 디렉토리에는 WebSocket 기반 실시간 알림 시스템과 상호작용할 수 있는 다양한 클라이언트 프로그램들과 테스트 도구들이 포함되어 있습니다.

## ✨ 주요 특징

- **🔄 동적 URL 변환**: WebSocket URL에서 HTTP API URL 자동 생성
- **📡 실시간 알림 수신**: WebSocket을 통한 실시간 알림 처리
- **📤 REST API 전송**: HTTP API를 통한 알림 전송
- **🎯 올바른 enum 값**: DB 스키마에 맞는 kind/severity 값 사용
- **🔌 자동 재연결**: 연결 끊김 시 자동 재연결 기능
- **🌐 다중 플랫폼**: Python, JavaScript, HTML 지원
- **🛠️ 다양한 테스트 도구**: 수동 테스트부터 자동화된 테스트까지

---

## 📁 디렉토리 구조

```
Util/notification/
├── client/                          # 클라이언트 라이브러리 및 테스트
│   ├── notification_client.py       # Python 클라이언트 & 전송자 라이브러리
│   ├── notification_client.js       # JavaScript/Node.js 클라이언트 라이브러리
│   ├── notification_client.html     # 브라우저용 완전한 테스트 도구
│   ├── live_notification_test.py    # 실시간 알림 테스트 도구
│   ├── final_test.py                # 최종 통합 테스트
│   ├── test_python_client.py        # Python 클라이언트 테스트
│   ├── test_js_client.js            # JavaScript 클라이언트 테스트
│   ├── simple_test.py               # 간단한 연결 테스트
│   ├── working_test.py              # 작동 테스트
│   ├── test_summary.md              # 테스트 결과 요약
│   └── README.md                    # 클라이언트별 상세 가이드
├── tools/                           # 수동 테스트 도구들
│   ├── notify_ws_client.html        # 메인 수동 테스트 도구
│   ├── notify_ws_client_gpt.html    # GPT 스타일 테스트 도구
│   └── notify_ws_client_gemini.html # Gemini 스타일 테스트 도구
└── README.md                        # 이 파일
```

---

## 🎯 알림 타입 및 enum 값

### 올바른 kind 값 (DB enum)
- `system`: 시스템 알림 (경고/오류 포함)
- `schedule`: 일정 알림 (복약, 진료 등)
- `info`: 정보성 알림
- `contact`: 연락 요청
- `marketing`: 마케팅 알림
- `inbound`: 사용자 기원 메시지

### 올바른 severity 값 (DB enum)
- `green`: 정상/성공
- `blue`: 권고/일반
- `yellow`: 주의/경고
- `orange`: 고위험
- `red`: 위급/오류

### 권장 조합
```json
// 시스템 정상
{"kind": "system", "severity": "green"}

// 시스템 경고 (예: 디스크 사용량 높음)
{"kind": "system", "severity": "yellow"}

// 시스템 오류 (예: 서비스 장애)
{"kind": "system", "severity": "red"}

// 일정 알림
{"kind": "schedule", "severity": "blue"}

// 긴급 연락
{"kind": "contact", "severity": "orange"}
```

---

## 🔄 동적 URL 변환 기능

모든 클라이언트는 WebSocket URL을 입력하면 HTTP API URL을 자동으로 생성합니다:

| 입력 URL | WebSocket URL | HTTP API URL |
|----------|---------------|--------------|
| `ws://localhost` | `ws://localhost/ws` | `http://localhost/api/v1/notify/queue` |
| `wss://example.com` | `wss://example.com/ws` | `https://example.com/api/v1/notify/queue` |
| `ws://server.com:8080/ws` | `ws://server.com:8080/ws` | `http://server.com:8080/api/v1/notify/queue` |
| `http://api-server.com` | `ws://api-server.com/ws` | `http://api-server.com/api/v1/notify/queue` |

**장점**: 서버 URL 하나만 설정하면 WebSocket 연결과 REST API 호출이 모두 올바른 주소로 전송됩니다.

---

## 🚀 빠른 시작

### 1️⃣ 사전 요구사항

- **서버 실행**: 알림 시스템 서버가 실행 중이어야 합니다
- **환경 변수**: `NOTIFY_ENABLE=true`, `NOTIFY_DISPATCH_ENABLE=true`, `NOTIFY_WS_ENABLE=true`

### 2️⃣ 서버 상태 확인

```bash
# 서버 상태 확인 (AWS 서버 예제)
curl http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/health

# 또는 로컬 서버
curl http://localhost/health
```

### 3️⃣ 가장 빠른 테스트 방법

**브라우저에서 즉시 테스트:**
1. `client/notification_client.html` 파일을 브라우저에서 열기
2. 서버 URL 입력 (기본값: AWS 서버)
3. 사용자 ID 입력 (기본값: UUID)
4. "연결" 버튼 클릭
5. 알림 전송 버튼들로 테스트

---

## 📖 사용 방법

### A. Python 클라이언트 사용법

#### 설치
```bash
pip install websockets requests aiohttp
```

#### 기본 사용법
```python
from client.notification_client import NotificationClient, NotificationSender

# 1. 알림 수신 (WebSocket)
client = NotificationClient('ws://your-server.com', 'your-user-id')

@client.on_notification('system')
async def handle_system(notification):
    severity = notification.get('severity', 'unknown')
    if severity == 'yellow':
        print(f"⚠️ 경고: {notification['title']}")
    elif severity == 'red':
        print(f"🚨 오류: {notification['title']}")

await client.connect()

# 2. 알림 전송 (REST API)
sender = NotificationSender('ws://your-server.com')  # 동적 URL 변환
result = sender.send_notification(
    recipients=['user-id'],
    title='테스트 알림',
    body='알림 내용',
    kind='system',
    severity='green'
)
```

### B. JavaScript 클라이언트 사용법

#### Node.js 환경
```bash
npm install ws
```

```javascript
const { NotificationClient } = require('./client/notification_client.js');

const client = new NotificationClient('ws://your-server.com', 'user-id');

client.onNotification('system', (notification) => {
    console.log('시스템 알림:', notification);
});

client.on('connect', () => console.log('연결됨'));
client.connect();
```

#### 브라우저 환경
```html
<script src="client/notification_client.js"></script>
<script>
    const client = new NotificationClient('ws://your-server.com', 'user-id');
    client.onNotification('system', (notification) => {
        console.log('알림:', notification);
    });
    client.connect();
</script>
```

### C. HTML 테스트 도구 사용법

1. **메인 테스트 도구**: `client/notification_client.html`
   - 완전한 기능을 가진 브라우저 기반 테스트 도구
   - WebSocket 연결, 알림 전송, 실시간 로그 확인

2. **수동 테스트 도구들**: `tools/` 디렉토리
   - `notify_ws_client.html`: 메인 수동 테스트 도구
   - `notify_ws_client_gpt.html`: GPT 스타일 UI
   - `notify_ws_client_gemini.html`: Gemini 스타일 UI

---

## 🧪 테스트 방법

### 1️⃣ 즉시 테스트 (권장)

**브라우저 테스트:**
```bash
# 브라우저에서 파일 열기
open client/notification_client.html
# 또는
open tools/notify_ws_client.html
```

### 2️⃣ Python 테스트

**실시간 테스트:**
```bash
cd client
python live_notification_test.py
```

**최종 통합 테스트:**
```bash
cd client
python final_test.py
```

**간단한 연결 테스트:**
```bash
cd client
python simple_test.py
```

### 3️⃣ JavaScript 테스트

**Node.js 테스트:**
```bash
cd client
node test_js_client.js
```

### 4️⃣ 단계별 테스트 가이드

#### Step 1: 서버 연결 확인
```bash
curl http://your-server.com/health
```

#### Step 2: WebSocket 연결 테스트
```bash
cd client
python simple_test.py
```

#### Step 3: 알림 전송 테스트
```bash
# 다른 터미널에서
curl -X POST 'http://your-server.com/api/v1/notify/queue' \
-H 'Content-Type: application/json' \
-d '{
  "kind": "system",
  "severity": "green",
  "title": "테스트 알림",
  "body": "연결 테스트 성공!",
  "recipients": ["your-user-id"],
  "channel": "websocket"
}'
```

#### Step 4: 실시간 테스트
```bash
cd client
python live_notification_test.py
```

### 5️⃣ 자동화된 테스트

**전체 기능 테스트:**
```bash
cd client
python test_python_client.py  # Python 클라이언트 테스트
node test_js_client.js         # JavaScript 클라이언트 테스트
python working_test.py         # 작동 테스트
```

---

## 🔧 고급 사용법

### 커스텀 설정

**Python:**
```python
client = NotificationClient(
    base_url='ws://your-server.com',
    user_id='user-123',
    auto_reconnect=True,
    reconnect_interval=5.0,
    max_reconnect_attempts=10,
    enable_logging=True
)
```

**JavaScript:**
```javascript
const client = new NotificationClient('ws://your-server.com', 'user-123', {
    autoReconnect: true,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    enableLogging: true
});
```

### 이벤트 핸들러

**Python:**
```python
@client.on('connect')
async def on_connect():
    print("✅ 연결 성공")

@client.on('disconnect')
async def on_disconnect():
    print("🔌 연결 해제")

@client.on('error')
async def on_error(error):
    print(f"❌ 오류: {error}")
```

**JavaScript:**
```javascript
client.on('connect', () => console.log('✅ 연결 성공'));
client.on('disconnect', () => console.log('🔌 연결 해제'));
client.on('error', (error) => console.log('❌ 오류:', error));
```

---

## 📊 테스트 결과 확인

### 로그 확인
- **Python**: 콘솔에 실시간 로그 출력
- **JavaScript**: 브라우저 개발자 도구 Console 탭
- **HTML 도구**: 페이지 내 로그 영역

### 성공 지표
- ✅ WebSocket 연결 성공 메시지
- ✅ 알림 전송 성공 응답 (message_id 반환)
- ✅ 실시간 알림 수신 확인
- ✅ 자동 재연결 동작 (연결 끊김 시)

### 일반적인 문제 해결

**연결 실패:**
- 서버 상태 확인: `curl http://server/health`
- 환경 변수 확인: `NOTIFY_*_ENABLE=true`
- 방화벽/포트 확인

**알림 전송 실패:**
- enum 값 확인 (kind, severity)
- recipients UUID 형식 확인
- CORS 설정 확인 (브라우저)

**WebSocket 연결 끊김:**
- 자동 재연결 설정 활성화
- 네트워크 연결 상태 확인
- 서버 로그 확인

---

## 📚 추가 문서

- **클라이언트 상세 가이드**: `client/README.md`
- **테스트 결과 요약**: `client/test_summary.md`
- **개발 관리 문서**: `../../server/app_server/docs/`

---

## 🎯 다음 단계

1. **기본 테스트**: HTML 도구로 연결 및 알림 전송 확인
2. **프로그래밍 테스트**: Python/JavaScript 클라이언트로 자동화
3. **통합 테스트**: 실제 애플리케이션에 클라이언트 통합
4. **성능 테스트**: 대량 알림 및 동시 연결 테스트
5. **프로덕션 배포**: 환경별 URL 설정 및 모니터링

---

## 💡 팁

- **개발 시**: `client/notification_client.html`로 빠른 테스트
- **디버깅 시**: `enable_logging=true`로 상세 로그 확인
- **프로덕션**: 자동 재연결 및 오류 핸들링 활성화
- **성능**: 필요시 연결 풀링 및 배치 전송 고려

**Happy Coding! 🚀**
