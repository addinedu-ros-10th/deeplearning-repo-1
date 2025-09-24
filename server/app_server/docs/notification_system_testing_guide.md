# 🧪 알림 시스템 테스트 가이드

---

## 🎯 테스트 개요

이 가이드는 WebSocket 기반 실시간 알림 시스템의 다양한 테스트 방법을 제공합니다. 개발자, QA 엔지니어, 시스템 관리자가 알림 시스템의 정상 작동을 확인할 수 있도록 단계별 테스트 절차를 설명합니다.

---

## 🚀 사전 준비

### 1️⃣ 환경 설정 확인

```bash
# 환경 변수 확인
echo $NOTIFY_ENABLE                # true 여야 함
echo $NOTIFY_DISPATCH_ENABLE       # true 여야 함  
echo $NOTIFY_WS_ENABLE            # true 여야 함
```

### 2️⃣ 서비스 상태 확인

```bash
# Docker 서비스 상태 확인
cd server/app_server
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml ps

# 예상 출력:
# NAME      COMMAND                  SERVICE   STATUS    PORTS
# api-1     "uvicorn app.main:ap…"   api       Up        8000/tcp
# nginx-1   "/docker-entrypoint.…"   nginx     Up        0.0.0.0:80->80/tcp
# redis-1   "docker-entrypoint.s…"   redis     Up        6379/tcp
```

### 3️⃣ API 서버 Health Check

```bash
# API 서버 상태 확인
curl -X GET "http://localhost/health"

# 예상 응답:
# {"status": "healthy", "timestamp": "2025-09-24T10:30:00Z"}
```

---

## 🔧 수동 테스트

### 1️⃣ WebSocket 연결 테스트

#### 웹 브라우저 테스트 도구 사용

1. **테스트 도구 열기**
   ```bash
   # 브라우저에서 다음 파일 열기
   open server/app_server/staging/tools/notify_ws_client.html
   ```

2. **연결 설정**
   - BASE URL: `http://localhost` (또는 운영 서버 URL)
   - User ID: `11111111-1111-1111-1111-111111111111`

3. **연결 테스트**
   - "Connect" 버튼 클릭
   - 로그에서 "✅ 연결 성공!" 메시지 확인

4. **Ping 테스트**
   - "Send Ping" 버튼 클릭
   - 로그에서 "📤 전송: ping" 메시지 확인

#### 커맨드라인 WebSocket 테스트

```bash
# wscat 설치 (Node.js 필요)
npm install -g wscat

# WebSocket 연결 테스트
wscat -c "ws://localhost/ws?user_id=11111111-1111-1111-1111-111111111111"

# 연결 성공 시 메시지 전송 가능
# > ping
# < (서버 응답 확인)
```

### 2️⃣ 알림 전송 테스트

#### 기본 알림 전송

```bash
# 간단한 정보 알림
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "info",
  "severity": "green",
  "title": "테스트 알림",
  "body": "이것은 테스트 메시지입니다.",
  "recipients": ["11111111-1111-1111-1111-111111111111"],
  "channel": "websocket"
}'

# 예상 응답:
# {
#   "message_id": "550e8400-e29b-41d4-a716-446655440000",
#   "queued_count": 1
# }
```

#### 경고 알림 전송

```bash
# 경고 알림 테스트
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "warning", 
  "severity": "yellow",
  "title": "⚠️ 시스템 경고",
  "body": "디스크 사용량이 높습니다.",
  "data": {"disk_usage": 85, "server": "test-01"},
  "recipients": ["11111111-1111-1111-1111-111111111111"],
  "channel": "websocket"
}'
```

#### 오류 알림 전송

```bash
# 오류 알림 테스트
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "error",
  "severity": "red", 
  "title": "🚨 시스템 오류",
  "body": "데이터베이스 연결에 실패했습니다.",
  "data": {"error_code": "DB_CONNECTION_FAILED", "timestamp": "2025-09-24T10:30:00Z"},
  "recipients": ["11111111-1111-1111-1111-111111111111"],
  "channel": "websocket"
}'
```

### 3️⃣ 다중 사용자 테스트

#### 여러 사용자에게 알림 전송

```bash
# 다중 수신자 테스트
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "info",
  "severity": "green",
  "title": "📢 공지사항",
  "body": "시스템 점검이 예정되어 있습니다.",
  "recipients": [
    "11111111-1111-1111-1111-111111111111",
    "22222222-2222-2222-2222-222222222222",
    "33333333-3333-3333-3333-333333333333"
  ],
  "channel": "websocket"
}'
```

#### 여러 브라우저 탭에서 동시 연결

1. 브라우저에서 테스트 도구를 여러 탭으로 열기
2. 각 탭에서 다른 User ID로 연결
3. 다중 수신자로 알림 전송
4. 모든 탭에서 알림 수신 확인

---

## 🤖 자동화 테스트

### 1️⃣ Python 테스트 스크립트

```python
#!/usr/bin/env python3
"""
알림 시스템 자동화 테스트 스크립트
"""

import asyncio
import websockets
import requests
import json
import uuid
from datetime import datetime

class NotificationTester:
    def __init__(self, base_url="http://localhost", ws_url="ws://localhost"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.api_url = f"{base_url}/api/v1/notify/queue"
        
    async def test_websocket_connection(self, user_id):
        """WebSocket 연결 테스트"""
        try:
            uri = f"{self.ws_url}/ws?user_id={user_id}"
            async with websockets.connect(uri) as websocket:
                print(f"✅ WebSocket 연결 성공: {user_id}")
                
                # Ping 전송
                await websocket.send("ping")
                print("📤 Ping 전송")
                
                # 5초 대기 (알림 수신 대기)
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📨 메시지 수신: {message}")
                    return True
                except asyncio.TimeoutError:
                    print("⏰ 메시지 수신 타임아웃")
                    return False
                    
        except Exception as e:
            print(f"❌ WebSocket 연결 실패: {e}")
            return False
    
    def send_notification(self, recipients, title, body, kind="info", severity="green"):
        """알림 전송"""
        payload = {
            "kind": kind,
            "severity": severity,
            "title": title,
            "body": body,
            "recipients": recipients,
            "channel": "websocket"
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ 알림 전송 성공: {result['message_id']}")
                return result
            else:
                print(f"❌ 알림 전송 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 알림 전송 오류: {e}")
            return None
    
    async def test_notification_flow(self):
        """전체 알림 플로우 테스트"""
        user_id = str(uuid.uuid4())
        print(f"\n🧪 알림 플로우 테스트 시작 (User: {user_id})")
        
        # WebSocket 연결 및 메시지 대기
        async def websocket_listener():
            try:
                uri = f"{self.ws_url}/ws?user_id={user_id}"
                async with websockets.connect(uri) as websocket:
                    print("✅ WebSocket 연결 완료")
                    
                    # 알림 대기
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    notification = json.loads(message)
                    print(f"📨 알림 수신 성공: {notification.get('title')}")
                    return True
                    
            except asyncio.TimeoutError:
                print("⏰ 알림 수신 타임아웃")
                return False
            except Exception as e:
                print(f"❌ WebSocket 오류: {e}")
                return False
        
        # WebSocket 연결 시작
        websocket_task = asyncio.create_task(websocket_listener())
        
        # 잠시 대기 후 알림 전송
        await asyncio.sleep(1)
        
        result = self.send_notification(
            recipients=[user_id],
            title="자동화 테스트 알림",
            body=f"테스트 시간: {datetime.now().isoformat()}"
        )
        
        if not result:
            return False
        
        # WebSocket 메시지 수신 대기
        websocket_result = await websocket_task
        return websocket_result

async def run_tests():
    """테스트 실행"""
    tester = NotificationTester()
    
    print("🚀 알림 시스템 자동화 테스트 시작")
    print("=" * 50)
    
    # 1. 기본 WebSocket 연결 테스트
    print("\n1️⃣ WebSocket 연결 테스트")
    test_user = "11111111-1111-1111-1111-111111111111"
    connection_result = await tester.test_websocket_connection(test_user)
    
    # 2. 알림 전송 테스트
    print("\n2️⃣ 알림 전송 테스트")
    send_result = tester.send_notification(
        recipients=[test_user],
        title="연결 테스트",
        body="WebSocket 연결 테스트용 알림입니다."
    )
    
    # 3. 전체 플로우 테스트
    print("\n3️⃣ 전체 플로우 테스트")
    flow_result = await tester.test_notification_flow()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print(f"WebSocket 연결: {'✅ 성공' if connection_result else '❌ 실패'}")
    print(f"알림 전송: {'✅ 성공' if send_result else '❌ 실패'}")
    print(f"전체 플로우: {'✅ 성공' if flow_result else '❌ 실패'}")
    
    success_count = sum([connection_result, bool(send_result), flow_result])
    print(f"\n총 테스트: 3개, 성공: {success_count}개, 실패: {3-success_count}개")
    
    return success_count == 3

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
```

### 2️⃣ 테스트 스크립트 실행

```bash
# Python 테스트 스크립트 저장 후 실행
python3 notification_test.py

# 예상 출력:
# 🚀 알림 시스템 자동화 테스트 시작
# ==================================================
# 
# 1️⃣ WebSocket 연결 테스트
# ✅ WebSocket 연결 성공: 11111111-1111-1111-1111-111111111111
# 📤 Ping 전송
# 
# 2️⃣ 알림 전송 테스트  
# ✅ 알림 전송 성공: 550e8400-e29b-41d4-a716-446655440000
# 
# 3️⃣ 전체 플로우 테스트
# 🧪 알림 플로우 테스트 시작 (User: a1b2c3d4-e5f6-7890-abcd-ef1234567890)
# ✅ WebSocket 연결 완료
# ✅ 알림 전송 성공: 660e8400-e29b-41d4-a716-446655440001
# 📨 알림 수신 성공: 자동화 테스트 알림
```

---

## 🔍 로그 모니터링 테스트

### 1️⃣ 서비스 로그 확인

```bash
# API 서버 로그 확인
docker compose --env-file ./secret/.env.local -f docker/compose.base.yml -f docker/compose.local.yml logs api

# 디스패처 관련 로그 필터링
docker compose logs api | grep -i notify

# 예상 로그:
# api-1 | [notify] dispatcher started (ws=true)
# api-1 | [notify] queued notification: 550e8400-e29b-41d4-a716-446655440000
# api-1 | [notify] delivered to user: 11111111-1111-1111-1111-111111111111
```

### 2️⃣ 실시간 로그 모니터링

```bash
# 실시간 로그 모니터링
docker compose logs -f api | grep -i notify

# 새 터미널에서 알림 전송 테스트 실행
curl -X POST "http://localhost/api/v1/notify/queue" \
-H "Content-Type: application/json" \
-d '{
  "kind": "info",
  "severity": "green", 
  "title": "로그 테스트",
  "body": "로그 모니터링 테스트입니다.",
  "recipients": ["11111111-1111-1111-1111-111111111111"],
  "channel": "websocket"
}'
```

---

## 🗄️ 데이터베이스 테스트

### 1️⃣ 알림 데이터 확인

```bash
# PostgreSQL 연결 (SSH 터널 필요)
psql -h localhost -p 15432 -U your_user -d your_db

# 알림 메시지 조회
SELECT message_id, kind, severity, title, created_at 
FROM notify.notify_message 
ORDER BY created_at DESC 
LIMIT 10;

# 전송 기록 조회  
SELECT delivery_id, message_id, user_id, status, created_at
FROM notify.notify_delivery 
ORDER BY created_at DESC 
LIMIT 10;
```

### 2️⃣ 상태별 알림 통계

```sql
-- 알림 종류별 통계
SELECT kind, COUNT(*) as count
FROM notify.notify_message 
GROUP BY kind;

-- 전송 상태별 통계
SELECT status, COUNT(*) as count  
FROM notify.notify_delivery
GROUP BY status;

-- 최근 1시간 알림 현황
SELECT 
    nm.kind,
    nd.status,
    COUNT(*) as count
FROM notify.notify_message nm
JOIN notify.notify_delivery nd ON nm.message_id = nd.message_id
WHERE nm.created_at > NOW() - INTERVAL '1 hour'
GROUP BY nm.kind, nd.status
ORDER BY count DESC;
```

---

## 🚀 성능 테스트

### 1️⃣ 부하 테스트

```python
#!/usr/bin/env python3
"""
알림 시스템 부하 테스트
"""

import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def send_bulk_notifications(session, base_url, count=100):
    """대량 알림 전송 테스트"""
    url = f"{base_url}/api/v1/notify/queue"
    
    async def send_single():
        payload = {
            "kind": "info",
            "severity": "green",
            "title": "부하 테스트",
            "body": f"테스트 시간: {time.time()}",
            "recipients": ["11111111-1111-1111-1111-111111111111"],
            "channel": "websocket"
        }
        
        async with session.post(url, json=payload) as response:
            return response.status == 201
    
    # 동시 전송
    start_time = time.time()
    tasks = [send_single() for _ in range(count)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    success_count = sum(results)
    duration = end_time - start_time
    
    print(f"📊 부하 테스트 결과:")
    print(f"   총 요청: {count}개")
    print(f"   성공: {success_count}개")
    print(f"   실패: {count - success_count}개")
    print(f"   소요 시간: {duration:.2f}초")
    print(f"   TPS: {count / duration:.2f}")

async def run_load_test():
    async with aiohttp.ClientSession() as session:
        await send_bulk_notifications(session, "http://localhost", count=100)

if __name__ == "__main__":
    asyncio.run(run_load_test())
```

### 2️⃣ WebSocket 연결 수 테스트

```python
#!/usr/bin/env python3
"""
WebSocket 동시 연결 수 테스트
"""

import asyncio
import websockets
import uuid

async def create_websocket_connection(ws_url, user_id, duration=30):
    """WebSocket 연결 유지"""
    try:
        uri = f"{ws_url}/ws?user_id={user_id}"
        async with websockets.connect(uri) as websocket:
            print(f"✅ 연결 성공: {user_id[:8]}...")
            await asyncio.sleep(duration)
            return True
    except Exception as e:
        print(f"❌ 연결 실패: {user_id[:8]}... - {e}")
        return False

async def test_concurrent_connections(ws_url="ws://localhost", count=50):
    """동시 연결 테스트"""
    print(f"🧪 동시 WebSocket 연결 테스트 ({count}개)")
    
    # 동시 연결 생성
    tasks = []
    for _ in range(count):
        user_id = str(uuid.uuid4())
        task = create_websocket_connection(ws_url, user_id)
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    success_count = sum(1 for r in results if r is True)
    duration = end_time - start_time
    
    print(f"📊 동시 연결 테스트 결과:")
    print(f"   목표 연결: {count}개")
    print(f"   성공 연결: {success_count}개")
    print(f"   실패 연결: {count - success_count}개")
    print(f"   소요 시간: {duration:.2f}초")

if __name__ == "__main__":
    import time
    asyncio.run(test_concurrent_connections(count=50))
```

---

## 🐛 문제 해결 가이드

### 1️⃣ 일반적인 문제들

#### WebSocket 연결 실패
```bash
# 1. 서비스 상태 확인
docker compose ps

# 2. 네트워크 연결 확인  
curl -I http://localhost/health

# 3. 환경 변수 확인
docker compose exec api env | grep NOTIFY

# 4. 로그 확인
docker compose logs api | grep -i error
```

#### 알림이 전송되지 않음
```bash
# 1. 디스패처 상태 확인
docker compose logs api | grep -i dispatch

# 2. 데이터베이스 연결 확인
docker compose exec api python -c "
import asyncio
from app.infrastructure.db.session import db_manager
async def test():
    await db_manager.initialize()
    print('DB 연결 성공')
asyncio.run(test())
"

# 3. 큐 상태 확인 (PostgreSQL)
psql -h localhost -p 15432 -U user -d db -c "
SELECT status, COUNT(*) 
FROM notify.notify_delivery 
GROUP BY status;
"
```

#### 성능 문제
```bash
# 1. 리소스 사용량 확인
docker stats

# 2. 연결 수 확인
ss -tuln | grep :80

# 3. 프로세스 상태 확인  
docker compose exec api ps aux
```

### 2️⃣ 디버깅 모드

```bash
# 디버그 로그 활성화
export LOG_LEVEL=DEBUG

# 서비스 재시작
docker compose restart api

# 상세 로그 확인
docker compose logs -f api
```

---

## ✅ 테스트 체크리스트

### 기본 기능 테스트
- [ ] WebSocket 연결 성공
- [ ] 기본 알림 전송/수신
- [ ] 다중 사용자 알림
- [ ] 다양한 알림 타입 (info, warning, error)
- [ ] 알림 데이터 포함 전송

### 고급 기능 테스트  
- [ ] 예약 알림 (scheduled_at)
- [ ] 만료 시간 설정 (expires_at)
- [ ] 대량 알림 전송
- [ ] 연결 재시도 로직

### 성능 테스트
- [ ] 동시 연결 수 테스트
- [ ] 대량 알림 처리 성능
- [ ] 메모리 사용량 모니터링
- [ ] CPU 사용률 확인

### 안정성 테스트
- [ ] 서비스 재시작 테스트
- [ ] 네트워크 단절 시나리오
- [ ] 데이터베이스 연결 실패 처리
- [ ] 예외 상황 처리

---

## 📞 지원 및 문의

### 🔧 테스트 실패 시
1. 로그 파일 수집
2. 환경 설정 확인
3. 네트워크 상태 점검
4. 데이터베이스 연결 상태 확인

### 📚 추가 자료
- [개발 관리 문서](./notification_system_development.md)
- [사용 가이드](./notification_system_usage_guide.md)
- [API 문서](http://localhost/docs)

---

*Last Updated: 2025-09-24*
*Version: 1.0.0*
