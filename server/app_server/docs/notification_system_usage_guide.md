# 📱 알림 시스템 사용 가이드

---

## 🎯 개요

이 가이드는 WebSocket 기반 실시간 알림 시스템의 사용법을 설명합니다. 개발자와 시스템 관리자가 알림 기능을 효과적으로 활용할 수 있도록 단계별 사용법을 제공합니다.

---

## 🚀 빠른 시작

### 1️⃣ 환경 설정 확인

먼저 다음 환경 변수가 설정되어 있는지 확인하세요:

```bash
# .env 파일 또는 환경 변수
NOTIFY_ENABLE=true                # 알림 시스템 활성화
NOTIFY_DISPATCH_ENABLE=true       # 백그라운드 디스패처 활성화  
NOTIFY_WS_ENABLE=true            # WebSocket 지원 활성화
DB_APP_URL=postgresql+asyncpg://user:pass@host:port/db
```

### 2️⃣ 서비스 시작

```bash
# Docker Compose로 서비스 시작
cd server/app_server
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml up -d

# 서비스 상태 확인
docker compose ps
```

### 3️⃣ WebSocket 연결 테스트

브라우저에서 `server/app_server/staging/tools/notify_ws_client.html`을 열어 연결을 테스트하세요.

---

## 📡 WebSocket 클라이언트 연결

### JavaScript 클라이언트 예제

```javascript
// WebSocket 연결 설정
const BASE_URL = 'ws://localhost';  // 또는 운영 서버 URL
const USER_ID = '11111111-1111-1111-1111-111111111111';

// WebSocket 연결
const ws = new WebSocket(`${BASE_URL}/ws?user_id=${USER_ID}`);

// 연결 성공 시
ws.onopen = function(event) {
    console.log('✅ WebSocket 연결 성공');
};

// 메시지 수신 시
ws.onmessage = function(event) {
    const notification = JSON.parse(event.data);
    console.log('📨 알림 수신:', notification);
    
    // 알림 처리 로직
    displayNotification(notification);
};

// 연결 종료 시
ws.onclose = function(event) {
    console.log('🔌 WebSocket 연결 종료');
};

// 오류 발생 시
ws.onerror = function(error) {
    console.error('❌ WebSocket 오류:', error);
};
```

### 알림 표시 함수 예제

```javascript
function displayNotification(notification) {
    // 브라우저 알림 표시
    if (Notification.permission === 'granted') {
        new Notification(notification.title || '알림', {
            body: notification.body,
            icon: '/static/notification-icon.png'
        });
    }
    
    // 페이지 내 알림 표시
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${notification.severity}`;
    alertDiv.innerHTML = `
        <h4>${notification.title}</h4>
        <p>${notification.body}</p>
        <small>종류: ${notification.kind}</small>
    `;
    document.getElementById('notifications').appendChild(alertDiv);
}
```

---

## 🔔 알림 전송 API

### REST API를 통한 알림 생성

#### 기본 알림 전송

```bash
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "info",
  "severity": "green",
  "title": "시스템 알림",
  "body": "작업이 성공적으로 완료되었습니다.",
  "recipients": ["11111111-1111-1111-1111-111111111111"],
  "channel": "websocket"
}'
```

#### 고급 알림 전송 (데이터 포함)

```bash
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "warning",
  "severity": "yellow", 
  "title": "시스템 경고",
  "body": "디스크 사용량이 80%를 초과했습니다.",
  "data": {
    "disk_usage": 85,
    "server": "web-01",
    "action_required": true
  },
  "recipients": [
    "11111111-1111-1111-1111-111111111111",
    "22222222-2222-2222-2222-222222222222"
  ],
  "channel": "websocket",
  "expires_at": "2025-09-25T10:00:00Z"
}'
```

#### 예약 알림 전송

```bash
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "info",
  "severity": "green",
  "title": "정기 점검 안내",
  "body": "오늘 밤 12시부터 시스템 점검이 시작됩니다.",
  "recipients": ["11111111-1111-1111-1111-111111111111"],
  "channel": "websocket",
  "scheduled_at": "2025-09-24T21:00:00Z"
}'
```

### Python 클라이언트 예제

```python
import requests
import json
from datetime import datetime, timezone

class NotificationClient:
    def __init__(self, base_url="http://localhost"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/notify/queue"
    
    def send_notification(self, 
                         recipients, 
                         title, 
                         body,
                         kind="info",
                         severity="green", 
                         data=None,
                         scheduled_at=None,
                         expires_at=None):
        """
        알림 전송
        
        Args:
            recipients: 수신자 UUID 리스트
            title: 알림 제목
            body: 알림 본문
            kind: 알림 종류 (info, warning, error)
            severity: 심각도 (green, yellow, red)
            data: 추가 데이터 (dict)
            scheduled_at: 예약 시간 (datetime)
            expires_at: 만료 시간 (datetime)
        """
        payload = {
            "kind": kind,
            "severity": severity,
            "title": title,
            "body": body,
            "recipients": recipients,
            "channel": "websocket"
        }
        
        if data:
            payload["data"] = data
            
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at.isoformat()
            
        if expires_at:
            payload["expires_at"] = expires_at.isoformat()
        
        response = requests.post(
            self.api_url,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        return response.json()

# 사용 예제
client = NotificationClient()

# 즉시 전송
result = client.send_notification(
    recipients=["11111111-1111-1111-1111-111111111111"],
    title="작업 완료",
    body="데이터 처리가 완료되었습니다.",
    kind="info",
    data={"processed_records": 1500}
)

print(f"알림 전송 완료: {result['message_id']}")
```

---

## 🎨 UI 컴포넌트 예제

### React 컴포넌트

```jsx
import React, { useState, useEffect } from 'react';

const NotificationSystem = ({ userId, baseUrl = 'ws://localhost' }) => {
    const [notifications, setNotifications] = useState([]);
    const [ws, setWs] = useState(null);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        // WebSocket 연결
        const websocket = new WebSocket(`${baseUrl}/ws?user_id=${userId}`);
        
        websocket.onopen = () => {
            setConnected(true);
            console.log('WebSocket 연결됨');
        };
        
        websocket.onmessage = (event) => {
            const notification = JSON.parse(event.data);
            setNotifications(prev => [...prev, {
                ...notification,
                id: Date.now(),
                timestamp: new Date()
            }]);
        };
        
        websocket.onclose = () => {
            setConnected(false);
            console.log('WebSocket 연결 끊김');
        };
        
        setWs(websocket);
        
        return () => {
            websocket.close();
        };
    }, [userId, baseUrl]);

    const removeNotification = (id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    return (
        <div className="notification-system">
            <div className="connection-status">
                {connected ? '🟢 연결됨' : '🔴 연결 끊김'}
            </div>
            
            <div className="notifications">
                {notifications.map(notification => (
                    <div 
                        key={notification.id}
                        className={`notification notification-${notification.severity}`}
                    >
                        <div className="notification-header">
                            <h4>{notification.title}</h4>
                            <button onClick={() => removeNotification(notification.id)}>
                                ✕
                            </button>
                        </div>
                        <p>{notification.body}</p>
                        <small>
                            {notification.kind} • {notification.timestamp.toLocaleTimeString()}
                        </small>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default NotificationSystem;
```

### CSS 스타일

```css
.notification-system {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 350px;
    z-index: 1000;
}

.connection-status {
    background: #f8f9fa;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 10px;
    font-size: 0.9rem;
    text-align: center;
}

.notification {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
    padding: 16px;
    animation: slideIn 0.3s ease-out;
}

.notification-green {
    border-left: 4px solid #10b981;
}

.notification-yellow {
    border-left: 4px solid #f59e0b;
}

.notification-red {
    border-left: 4px solid #ef4444;
}

.notification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.notification-header h4 {
    margin: 0;
    font-size: 1rem;
}

.notification-header button {
    background: none;
    border: none;
    cursor: pointer;
    color: #6b7280;
    font-size: 1.2rem;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
```

---

## 🔧 고급 사용법

### 알림 필터링

```javascript
// 특정 종류의 알림만 처리
ws.onmessage = function(event) {
    const notification = JSON.parse(event.data);
    
    // 중요한 알림만 브라우저 알림으로 표시
    if (notification.severity === 'red') {
        showBrowserNotification(notification);
    }
    
    // 모든 알림을 UI에 표시
    displayInUI(notification);
};
```

### 배치 알림 처리

```python
# 여러 사용자에게 동일한 알림 전송
def broadcast_notification(title, body, user_list, kind="info"):
    client = NotificationClient()
    
    # 사용자를 그룹별로 나누어 전송 (예: 100명씩)
    batch_size = 100
    for i in range(0, len(user_list), batch_size):
        batch = user_list[i:i+batch_size]
        
        result = client.send_notification(
            recipients=batch,
            title=title,
            body=body,
            kind=kind
        )
        
        print(f"배치 {i//batch_size + 1} 전송 완료: {len(batch)}명")
```

### 연결 재시도 로직

```javascript
class RobustWebSocketClient {
    constructor(url, userId) {
        this.url = url;
        this.userId = userId;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        this.connect();
    }
    
    connect() {
        this.ws = new WebSocket(`${this.url}/ws?user_id=${this.userId}`);
        
        this.ws.onopen = () => {
            console.log('WebSocket 연결 성공');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const notification = JSON.parse(event.data);
            this.handleNotification(notification);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket 연결 종료');
            this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket 오류:', error);
        };
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('최대 재연결 시도 횟수 초과');
        }
    }
    
    handleNotification(notification) {
        // 알림 처리 로직
        console.log('알림 수신:', notification);
    }
}
```

---

## ⚠️ 주의사항

### 보안 고려사항

1. **사용자 인증**: 실제 운영에서는 JWT 토큰 등을 통한 사용자 인증 구현 필요
2. **권한 검증**: 알림 전송 API에 적절한 권한 검증 로직 추가
3. **입력 검증**: 모든 입력 데이터에 대한 검증 및 sanitization

### 성능 최적화

1. **연결 수 제한**: 동시 WebSocket 연결 수 모니터링
2. **메시지 크기**: 큰 데이터는 별도 API로 조회하도록 구성
3. **배치 처리**: 대량 알림은 배치로 나누어 전송

### 에러 처리

1. **연결 실패**: 재연결 로직 구현
2. **메시지 손실**: 중요한 알림은 DB에서 재조회 가능하도록 구성
3. **서버 오류**: 적절한 fallback 메커니즘 구현

---

## 📞 지원 및 문의

### 🐛 문제 해결

1. **연결 안됨**: 환경 변수 및 네트워크 설정 확인
2. **알림 안옴**: 디스패처 로그 및 DB 상태 확인
3. **성능 문제**: 연결 수 및 메시지 처리량 모니터링

### 📚 추가 자료

- [개발 관리 문서](./notification_system_development.md)
- [테스트 가이드](./notification_system_testing_guide.md)
- [API 문서](http://localhost/docs)

---

*Last Updated: 2025-09-24*
*Version: 1.0.0*
