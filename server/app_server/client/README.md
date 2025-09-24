# 🔔 알림 시스템 클라이언트 프로그램

이 디렉토리에는 WebSocket 기반 실시간 알림 시스템과 상호작용할 수 있는 다양한 클라이언트 프로그램들이 포함되어 있습니다.

---

## 📁 파일 구조

```
client/
├── notification_client.js       # JavaScript/Node.js 클라이언트 라이브러리
├── notification_client.py       # Python 클라이언트 라이브러리
├── notification_client.html     # 브라우저용 테스트 클라이언트
├── test_js_client.js            # JavaScript 클라이언트 테스트 스크립트
├── test_python_client.py        # Python 클라이언트 테스트 스크립트
└── README.md                    # 이 파일
```

---

## 🚀 빠른 시작

### 1️⃣ 사전 요구사항

- **서버 실행**: 알림 시스템 서버가 실행 중이어야 합니다
- **환경 변수**: `NOTIFY_ENABLE=true`, `NOTIFY_DISPATCH_ENABLE=true`, `NOTIFY_WS_ENABLE=true`

### 2️⃣ 서버 상태 확인

```bash
# 서비스 상태 확인
docker compose ps

# API 서버 Health Check
curl http://localhost/health
```

---

## 💻 클라이언트 프로그램 사용법

### 🟨 JavaScript/Node.js 클라이언트

#### 설치
```bash
npm install ws  # WebSocket 라이브러리 (Node.js 환경에서만 필요)
```

#### 기본 사용법
```javascript
const { NotificationClient } = require('./notification_client.js');

// 클라이언트 생성
const client = new NotificationClient('ws://localhost', 'your-user-id');

// 이벤트 핸들러 등록
client.on('connect', () => console.log('연결됨!'));
client.on('message', (data) => console.log('메시지:', data));

// 알림 타입별 핸들러
client.onNotification('info', (notification) => {
    console.log('정보 알림:', notification.title);
});

// 연결
client.connect();
```

#### 테스트 실행
```bash
# 자동화 테스트
node test_js_client.js

# 대화형 실행
node notification_client.js
```

### 🐍 Python 클라이언트

#### 설치
```bash
pip install websockets requests aiohttp
```

#### 기본 사용법
```python
import asyncio
from notification_client import NotificationClient

async def main():
    # 클라이언트 생성
    client = NotificationClient('ws://localhost', 'your-user-id')
    
    # 알림 핸들러 등록
    @client.on_notification('info')
    async def handle_info(notification):
        print(f"정보: {notification['title']}")
    
    # 연결
    await client.connect()
    
    # 무한 대기
    while client.is_connected():
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
```

#### 테스트 실행
```bash
# 자동화 테스트
python3 test_python_client.py

# 대화형 실행
python3 notification_client.py
```

### 🌐 브라우저 클라이언트

#### 사용법
1. `notification_client.html` 파일을 브라우저에서 열기
2. 서버 URL과 사용자 ID 입력
3. "연결" 버튼 클릭
4. 알림 전송 테스트 또는 실시간 수신 확인

#### 특징
- 현대적인 UI/UX 디자인
- 실시간 로그 표시
- 연결 상태 모니터링
- 알림 타입별 전송 테스트
- 브라우저 알림 지원

---

## 🧪 테스트 결과

### ✅ JavaScript 클라이언트 테스트
```
🚀 JavaScript 클라이언트 종합 테스트
==================================================

1️⃣ 기본 연결 테스트
✅ WebSocket 연결 성공!
📤 Ping 전송...
👋 연결 해제 완료
📊 기본 연결 테스트: ✅ 성공

2️⃣ 알림 핸들러 테스트
✅ 핸들러 테스트용 연결 성공
🎭 가짜 알림 메시지 시뮬레이션...
ℹ️ 정보 알림 처리: 정보 테스트
⚠️ 경고 알림 처리: 경고 테스트
🚨 오류 알림 처리: 오류 테스트
📊 핸들러 테스트: ✅ 성공

총 2개 테스트 중 2개 성공
🎉 모든 테스트 통과!
```

### ✅ Python 클라이언트 테스트
```
🚀 Python 클라이언트 종합 테스트
==================================================

1️⃣ WebSocket 연결 테스트
✅ Python 클라이언트 연결 성공!
📊 WebSocket 연결 테스트: ✅ 성공

2️⃣ 알림 핸들러 테스트
✅ 핸들러 테스트용 연결 성공
🎭 가짜 알림 메시지 시뮬레이션...
ℹ️ 정보 알림 처리: 정보 테스트
⚠️ 경고 알림 처리: 경고 테스트
🚨 오류 알림 처리: 오류 테스트
📊 핸들러 테스트: ✅ 성공

3️⃣ API 연결 테스트
✅ API 서버 연결 성공
📊 API 연결 테스트: ✅ 성공

총 3개 테스트 중 3개 성공
🎉 모든 테스트 통과!
```

---

## 🔧 고급 사용법

### 연결 옵션 설정

#### JavaScript
```javascript
const client = new NotificationClient('ws://localhost', 'user-id', {
    autoReconnect: true,           // 자동 재연결
    reconnectInterval: 5000,       // 재연결 간격 (밀리초)
    maxReconnectAttempts: 10,      // 최대 재연결 시도
    enableLogging: true            // 로그 출력
});
```

#### Python
```python
client = NotificationClient(
    base_url='ws://localhost',
    user_id='user-id',
    auto_reconnect=True,           # 자동 재연결
    reconnect_interval=5.0,        # 재연결 간격 (초)
    max_reconnect_attempts=10,     # 최대 재연결 시도
    enable_logging=True            # 로그 출력
)
```

### 알림 전송

#### REST API 사용
```bash
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "info",
  "severity": "green",
  "title": "테스트 알림",
  "body": "이것은 테스트 메시지입니다.",
  "recipients": ["user-id"],
  "channel": "websocket"
}'
```

#### Python 클라이언트 사용
```python
from notification_client import NotificationSender

sender = NotificationSender('http://localhost')
result = sender.send_notification(
    recipients=['user-id'],
    title='Python 알림',
    body='Python에서 전송한 알림입니다.',
    kind='info'
)
```

### 이벤트 핸들링

#### 연결 상태 모니터링
```javascript
client.on('connect', () => {
    console.log('연결됨:', client.getConnectionInfo());
});

client.on('disconnect', () => {
    console.log('연결 끊김');
});

client.on('error', (error) => {
    console.error('오류:', error);
});
```

#### 알림 타입별 처리
```javascript
// 정보 알림
client.onNotification('info', (notification) => {
    console.log('📘', notification.title);
});

// 경고 알림
client.onNotification('warning', (notification) => {
    console.warn('⚠️', notification.title);
    // 특별한 처리 로직
});

// 오류 알림
client.onNotification('error', (notification) => {
    console.error('🚨', notification.title);
    // 긴급 처리 로직
});
```

---

## 🛠️ 문제 해결

### 연결 실패
```bash
# 서버 상태 확인
curl http://localhost/health

# 환경 변수 확인
echo $NOTIFY_ENABLE
echo $NOTIFY_WS_ENABLE

# 서비스 로그 확인
docker compose logs api
```

### 알림 수신 안됨
1. **WebSocket 연결 확인**: 연결 상태 표시등 확인
2. **사용자 ID 확인**: 전송 시 수신자 ID와 연결된 사용자 ID 일치 확인
3. **서버 로그 확인**: 디스패처 오류 로그 확인

### 성능 문제
- **연결 수 제한**: 동시 연결 수 모니터링
- **메시지 크기**: 큰 데이터는 별도 API로 조회
- **재연결 간격**: 너무 짧은 간격 설정 지양

---

## 📚 참고 자료

- [알림 시스템 개발 관리 문서](../docs/notification_system_development.md)
- [알림 시스템 사용 가이드](../docs/notification_system_usage_guide.md)
- [알림 시스템 테스트 가이드](../docs/notification_system_testing_guide.md)
- [API 문서](http://localhost/docs)

---

## 🤝 기여하기

1. 새로운 클라이언트 언어 추가
2. 기존 클라이언트 기능 개선
3. 테스트 케이스 추가
4. 문서 개선

---

*Last Updated: 2025-09-24*
*Version: 1.0.0*
*Status: ✅ Production Ready*
