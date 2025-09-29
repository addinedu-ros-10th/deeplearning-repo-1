# Sender ID 기준 메시지 조회 API

## 개요
특정 sender ID로 전송된 메시지들을 조회하는 API입니다. 메시지의 `data` 필드에 포함된 `sender` 값을 기준으로 필터링합니다.

## 엔드포인트
```
GET /api/v1/notify/messages/by-sender/{sender_id}
```

## 파라미터

### Path Parameters
- `sender_id` (string, required): 조회할 sender ID

### Query Parameters
- `skip` (integer, optional): 건너뛸 메시지 수 (기본값: 0)
- `limit` (integer, optional): 반환할 최대 메시지 수 (기본값: 100, 최대: 1000)

## 응답

### 성공 응답 (200 OK)
```json
[
  {
    "message_id": "91dbb64f-557c-4542-b85d-d8465c061aeb",
    "kind": "info",
    "severity": "green",
    "title": "이제는 알림이 가나요?",
    "body": "이제는 알림이 갔으면 좋겠는 내용!",
    "data": {
      "sender": "10fa45f2-f375-41c9-a62a-093efcd01bd3",
      "timestamp": "2025-09-29T19:33:06.151Z"
    },
    "scheduled_at": null,
    "expires_at": null,
    "created_by": null,
    "created_ip": null,
    "created_at": "2025-09-29T19:33:06.308094Z",
    "updated_at": "2025-09-29T19:33:06.308094Z"
  }
]
```

## 사용 예시

### cURL
```bash
curl -X GET "http://localhost:8000/api/v1/notify/messages/by-sender/10fa45f2-f375-41c9-a62a-093efcd01bd3?skip=0&limit=10" \
  -H "accept: application/json"
```

### Python
```python
import requests

# Sender ID로 메시지 조회
sender_id = "10fa45f2-f375-41c9-a62a-093efcd01bd3"
response = requests.get(
    f"http://localhost:8000/api/v1/notify/messages/by-sender/{sender_id}",
    params={"skip": 0, "limit": 10}
)

if response.status_code == 200:
    messages = response.json()
    print(f"조회된 메시지 수: {len(messages)}")
    for message in messages:
        print(f"제목: {message['title']}")
        print(f"내용: {message['body']}")
        print(f"발신자: {message['data']['sender']}")
        print("---")
else:
    print(f"오류: {response.status_code}")
```

### JavaScript
```javascript
const senderId = "10fa45f2-f375-41c9-a62a-093efcd01bd3";

fetch(`http://localhost:8000/api/v1/notify/messages/by-sender/${senderId}?skip=0&limit=10`)
  .then(response => response.json())
  .then(messages => {
    console.log(`조회된 메시지 수: ${messages.length}`);
    messages.forEach(message => {
      console.log(`제목: ${message.title}`);
      console.log(`내용: ${message.body}`);
      console.log(`발신자: ${message.data.sender}`);
      console.log("---");
    });
  })
  .catch(error => console.error("오류:", error));
```

## 구현 세부사항

### 데이터베이스 쿼리
이 API는 PostgreSQL의 JSONB 연산자를 사용하여 `data` 필드에서 `sender` 값을 조회합니다:

```sql
SELECT * FROM notify.notify_message 
WHERE data->>'sender' = :sender_id 
ORDER BY created_at DESC 
LIMIT :limit OFFSET :skip
```

### 정렬
메시지는 생성 시간(`created_at`) 기준으로 내림차순 정렬됩니다. 즉, 가장 최근에 생성된 메시지가 먼저 반환됩니다.

### 페이지네이션
- `skip`: 건너뛸 메시지 수
- `limit`: 반환할 최대 메시지 수 (1-1000 사이)

## 오류 처리
- 잘못된 sender ID 형식이나 존재하지 않는 sender ID의 경우 빈 배열을 반환합니다.
- 데이터베이스 연결 오류 시 500 Internal Server Error를 반환합니다.


