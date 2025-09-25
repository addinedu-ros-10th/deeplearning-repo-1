#!/usr/bin/env python3
"""
WebSocket 알림 클라이언트 & REST API 전송자 (Python)

이 모듈은 두 가지 주요 클래스를 제공합니다:
1. NotificationClient: WebSocket을 통한 실시간 알림 수신
2. NotificationSender: REST API를 통한 알림 전송

=== 설치 ===
pip install websockets requests aiohttp

=== 1. NotificationClient (WebSocket 수신) ===

기본 사용법:
    from notification_client import NotificationClient
    
    client = NotificationClient('ws://your-server.com', 'your-user-id')
    await client.connect()

커스텀 설정:
    client = NotificationClient(
        base_url='ws://your-server.com',
        user_id='user-123',
        auto_reconnect=True,
        reconnect_interval=5.0,
        max_reconnect_attempts=10
    )

알림 타입별 핸들러 등록 (올바른 enum 값 사용):
    @client.on_notification('system')  # 시스템 알림 (경고/오류 포함)
    async def handle_system(notification):
        severity = notification.get('severity', 'unknown')
        if severity == 'yellow':
            print(f"⚠️ 경고: {notification['title']}")
        elif severity == 'red':
            print(f"🚨 오류: {notification['title']}")
    
    @client.on_notification('info')     # 정보 알림
    async def handle_info(notification):
        print(f"ℹ️ 정보: {notification['title']}")
    
    @client.on_notification('schedule') # 일정 알림
    async def handle_schedule(notification):
        print(f"📅 일정: {notification['title']}")
    
    @client.on_notification('contact')  # 연락 요청
    async def handle_contact(notification):
        print(f"📞 연락: {notification['title']}")

연결 이벤트 핸들러:
    @client.on('connect')
    async def on_connect():
        print("✅ WebSocket 연결 성공")
    
    @client.on('disconnect')
    async def on_disconnect():
        print("🔌 WebSocket 연결 해제")
    
    @client.on('error')
    async def on_error(error):
        print(f"❌ 오류: {error}")

=== 2. NotificationSender (REST API 전송) ===

기본 사용법:
    from notification_client import NotificationSender
    
    # WebSocket URL 또는 HTTP URL 모두 지원 (자동 변환)
    sender = NotificationSender('ws://your-server.com')  # 또는 'http://your-server.com'
    
    result = sender.send_notification(
        recipients=['user-id-1', 'user-id-2'],
        title='알림 제목',
        body='알림 내용',
        kind='system',      # 필수: system/schedule/info/contact/marketing/inbound
        severity='yellow',  # 필수: green/blue/yellow/orange/red
        data={'custom': 'data'}  # 선택: 추가 데이터
    )

올바른 kind/severity 조합:
    # 시스템 알림
    kind='system', severity='green'   # 정상 상태
    kind='system', severity='yellow'  # 경고 (예: 디스크 사용량 높음)
    kind='system', severity='red'     # 오류 (예: 서비스 장애)
    
    # 일정 알림
    kind='schedule', severity='blue'  # 복약, 진료 일정 등
    
    # 정보 알림
    kind='info', severity='green'     # 일반 정보성 알림
    
    # 연락 요청
    kind='contact', severity='orange' # 긴급 연락 필요

=== 3. 동적 URL 변환 기능 ===

WebSocket URL을 입력하면 HTTP API URL이 자동으로 생성됩니다:
    ws://localhost → http://localhost/api/v1/notify/queue
    wss://example.com → https://example.com/api/v1/notify/queue
    ws://server.com:8080/ws → http://server.com:8080/api/v1/notify/queue

API URL 직접 확인:
    client = NotificationClient('ws://your-server.com', 'user-id')
    api_url = client.get_api_url()  # HTTP API URL 반환
    
    sender = NotificationSender('ws://your-server.com')
    print(sender.api_url)  # 생성된 API URL 확인

=== 4. 완전한 예제 ===

async def main():
    # 1. WebSocket 클라이언트로 알림 수신
    client = NotificationClient('ws://your-server.com', 'user-123')
    
    @client.on_notification('system')
    async def handle_system(notification):
        print(f"시스템 알림: {notification}")
    
    await client.connect()
    
    # 2. REST API로 알림 전송
    sender = NotificationSender('ws://your-server.com')  # 같은 URL 사용
    result = sender.send_notification(
        recipients=['user-123'],
        title='테스트 알림',
        body='동적 URL 생성 테스트',
        kind='system',
        severity='green'
    )
    print(f"전송 결과: {result}")

if __name__ == "__main__":
    asyncio.run(main())

=== 주의사항 ===
- kind 값은 반드시 DB enum에 정의된 값을 사용: system/schedule/info/contact/marketing/inbound
- severity 값은 반드시 DB enum에 정의된 값을 사용: green/blue/yellow/orange/red
- 경고/오류는 kind='system'과 severity='yellow'/'red' 조합으로 표현
- recipients는 반드시 UUID 형식의 사용자 ID 배열
"""

import asyncio
import websockets
import json
import logging
import signal
import sys
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
import uuid
import requests
from urllib.parse import urlencode
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# 유틸리티 함수들
def websocket_to_http_url(ws_url: str) -> str:
    """
    WebSocket URL을 HTTP API URL로 변환
    
    Args:
        ws_url: WebSocket URL (예: 'ws://localhost', 'ws://example.com:8080')
        
    Returns:
        HTTP URL (예: 'http://localhost', 'http://example.com:8080')
    """
    if not ws_url:
        return 'http://localhost'
    
    # ws:// 또는 wss://를 http:// 또는 https://로 변환
    http_url = re.sub(r'^wss?://', lambda m: 'https://' if m.group(0) == 'wss://' else 'http://', ws_url)
    
    # /ws 경로가 있다면 제거
    http_url = re.sub(r'/ws/?$', '', http_url)
    
    return http_url

def get_api_url(base_url: str, endpoint: str = '/api/v1/notify/queue') -> str:
    """
    Base URL에서 API URL 생성
    
    Args:
        base_url: WebSocket 또는 HTTP base URL
        endpoint: API 엔드포인트 경로
        
    Returns:
        완전한 API URL
    """
    if base_url.startswith('ws'):
        base_url = websocket_to_http_url(base_url)
    
    return f"{base_url.rstrip('/')}{endpoint}"

class NotificationClient:
    """
    WebSocket 기반 알림 클라이언트
    """
    
    def __init__(
        self,
        base_url: str = 'ws://localhost',
        user_id: str = None,
        auto_reconnect: bool = True,
        reconnect_interval: float = 5.0,
        max_reconnect_attempts: int = 10,
        enable_logging: bool = True
    ):
        """
        알림 클라이언트 초기화
        
        Args:
            base_url: WebSocket 서버 URL
            user_id: 사용자 ID (None이면 자동 생성)
            auto_reconnect: 자동 재연결 여부
            reconnect_interval: 재연결 간격 (초)
            max_reconnect_attempts: 최대 재연결 시도 횟수
            enable_logging: 로그 출력 여부
        """
        self.base_url = base_url
        self.user_id = user_id or str(uuid.uuid4())
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.enable_logging = enable_logging
        
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 0
        self.reconnect_task = None
        
        # 이벤트 핸들러들
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.notification_handlers: Dict[str, List[Callable]] = {}
        
        # 로거 설정
        self.logger = logging.getLogger(f'NotificationClient-{self.user_id[:8]}')
        if not enable_logging:
            self.logger.setLevel(logging.CRITICAL)
    
    def on(self, event: str, handler: Callable):
        """
        이벤트 핸들러 등록
        
        Args:
            event: 이벤트 이름 ('connect', 'disconnect', 'message', 'error')
            handler: 이벤트 핸들러 함수
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def on_notification(self, notification_type: str):
        """
        알림 타입별 핸들러 데코레이터
        
        Args:
            notification_type: 알림 타입 ('info', 'warning', 'error')
        
        Usage:
            @client.on_notification('warning')
            async def handle_warning(notification):
                print(f"경고: {notification['title']}")
        """
        def decorator(handler: Callable):
            if notification_type not in self.notification_handlers:
                self.notification_handlers[notification_type] = []
            self.notification_handlers[notification_type].append(handler)
            return handler
        return decorator
    
    def get_api_url(self, endpoint: str = '/api/v1/notify/queue') -> str:
        """
        WebSocket base URL에서 HTTP API URL 생성
        
        Args:
            endpoint: API 엔드포인트 경로
            
        Returns:
            완전한 API URL
        """
        return get_api_url(self.base_url, endpoint)

    def add_notification_handler(self, notification_type: str, handler: Callable):
        """
        알림 핸들러 직접 등록
        
        Args:
            notification_type: 알림 타입
            handler: 핸들러 함수
        """
        if notification_type not in self.notification_handlers:
            self.notification_handlers[notification_type] = []
        self.notification_handlers[notification_type].append(handler)
    
    async def connect(self):
        """WebSocket 연결"""
        if self.websocket and not self.websocket.closed:
            self.logger.warning("이미 연결되어 있습니다.")
            return
        
        url = f"{self.base_url}/ws?{urlencode({'user_id': self.user_id})}"
        self.logger.info(f"연결 시도 중... {url}")
        
        try:
            self.websocket = await websockets.connect(url)
            self.connected = True
            self.reconnect_attempts = 0
            
            # 연결 이벤트 발생
            await self._emit_event('connect')
            self.logger.info("✅ WebSocket 연결 성공")
            
            # 메시지 수신 루프 시작
            asyncio.create_task(self._message_loop())
            
        except Exception as e:
            self.logger.error(f"❌ 연결 실패: {e}")
            await self._emit_event('error', e)
            
            if self.auto_reconnect:
                await self._schedule_reconnect()
    
    async def disconnect(self):
        """연결 해제"""
        self.auto_reconnect = False
        
        if self.reconnect_task:
            self.reconnect_task.cancel()
            self.reconnect_task = None
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.connected = False
        await self._emit_event('disconnect')
        self.logger.info("🔌 WebSocket 연결 해제")
    
    async def send(self, message: Any) -> bool:
        """
        메시지 전송
        
        Args:
            message: 전송할 메시지 (str 또는 dict)
        
        Returns:
            bool: 전송 성공 여부
        """
        if not self.connected or not self.websocket:
            self.logger.error("❌ 연결되지 않음. 메시지 전송 실패")
            return False
        
        try:
            if isinstance(message, dict):
                data = json.dumps(message)
            else:
                data = str(message)
            
            await self.websocket.send(data)
            self.logger.info(f"📤 메시지 전송: {data}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 메시지 전송 오류: {e}")
            return False
    
    async def ping(self) -> bool:
        """Ping 전송 (연결 테스트)"""
        return await self.send('ping')
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.connected
    
    def get_connection_info(self) -> Dict[str, Any]:
        """연결 정보 반환"""
        return {
            'base_url': self.base_url,
            'user_id': self.user_id,
            'connected': self.connected,
            'reconnect_attempts': self.reconnect_attempts,
            'websocket_state': getattr(self.websocket, 'state', None)
        }
    
    # === 내부 메서드들 ===
    
    async def _message_loop(self):
        """메시지 수신 루프"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("연결이 종료되었습니다.")
        except Exception as e:
            self.logger.error(f"메시지 루프 오류: {e}")
            await self._emit_event('error', e)
        finally:
            self.connected = False
            await self._emit_event('disconnect')
            
            if self.auto_reconnect:
                await self._schedule_reconnect()
    
    async def _handle_message(self, message: str):
        """수신된 메시지 처리"""
        try:
            # JSON 파싱 시도
            data = json.loads(message)
            await self._handle_notification(data)
            await self._emit_event('message', data)
            
        except json.JSONDecodeError:
            # 일반 텍스트 메시지
            await self._emit_event('message', message)
        
        self.logger.info(f"📨 메시지 수신: {message}")
    
    async def _handle_notification(self, notification: Dict[str, Any]):
        """알림 메시지 처리"""
        notification_type = notification.get('kind')
        if notification_type and notification_type in self.notification_handlers:
            handlers = self.notification_handlers[notification_type]
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(notification)
                    else:
                        handler(notification)
                except Exception as e:
                    self.logger.error(f"❌ 알림 핸들러 오류: {e}")
    
    async def _emit_event(self, event: str, *args):
        """이벤트 발생"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(*args)
                    else:
                        handler(*args)
                except Exception as e:
                    self.logger.error(f"❌ 이벤트 핸들러 오류: {e}")
    
    async def _schedule_reconnect(self):
        """재연결 예약"""
        if (self.reconnect_attempts >= self.max_reconnect_attempts):
            self.logger.error("🚫 재연결 중단 (최대 시도 횟수 초과)")
            return
        
        self.reconnect_attempts += 1
        self.logger.info(
            f"🔄 재연결 예약 {self.reconnect_attempts}/{self.max_reconnect_attempts} "
            f"({self.reconnect_interval}초 후)"
        )
        
        self.reconnect_task = asyncio.create_task(
            self._delayed_reconnect()
        )
    
    async def _delayed_reconnect(self):
        """지연 재연결"""
        try:
            await asyncio.sleep(self.reconnect_interval)
            await self.connect()
        except asyncio.CancelledError:
            pass


class NotificationSender:
    """
    REST API를 통한 알림 전송 클래스
    """
    
    def __init__(self, base_url: str = 'http://localhost'):
        """
        알림 전송자 초기화
        
        Args:
            base_url: API 서버 URL (HTTP 또는 WebSocket URL 모두 지원)
        """
        # WebSocket URL인 경우 HTTP URL로 변환
        if base_url.startswith('ws'):
            self.base_url = websocket_to_http_url(base_url)
        else:
            self.base_url = base_url
            
        self.api_url = get_api_url(self.base_url)
        self.logger = logging.getLogger('NotificationSender')
    
    def send_notification(
        self,
        recipients: List[str],
        title: str,
        body: str,
        kind: str = 'info',
        severity: str = 'green',
        data: Optional[Dict] = None,
        scheduled_at: Optional[str] = None,
        expires_at: Optional[str] = None,
        timeout: int = 10
    ) -> Optional[Dict]:
        """
        알림 전송
        
        Args:
            recipients: 수신자 UUID 목록
            title: 알림 제목
            body: 알림 본문
            kind: 알림 종류 ('info', 'warning', 'error')
            severity: 심각도 ('green', 'yellow', 'red')
            data: 추가 데이터
            scheduled_at: 예약 시간 (ISO 형식)
            expires_at: 만료 시간 (ISO 형식)
            timeout: 요청 타임아웃 (초)
        
        Returns:
            Dict: 응답 데이터 또는 None (실패 시)
        """
        payload = {
            'kind': kind,
            'severity': severity,
            'title': title,
            'body': body,
            'recipients': recipients,
            'channel': 'websocket'
        }
        
        if data:
            payload['data'] = data
        if scheduled_at:
            payload['scheduled_at'] = scheduled_at
        if expires_at:
            payload['expires_at'] = expires_at
        
        try:
            response = requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 201:
                result = response.json()
                self.logger.info(f"✅ 알림 전송 성공: {result['message_id']}")
                return result
            else:
                self.logger.error(f"❌ 알림 전송 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ 알림 전송 오류: {e}")
            return None


# === 사용 예제들 ===

async def basic_example():
    """기본 사용 예제"""
    print("🚀 기본 예제 시작...")
    
    # 클라이언트 생성
    client = NotificationClient('ws://localhost', '11111111-1111-1111-1111-111111111111')
    
    # 알림 타입별 핸들러 등록
    @client.on_notification('info')
    async def handle_info(notification):
        print(f"ℹ️ 정보: {notification['title']} - {notification['body']}")
    
    @client.on_notification('warning')
    async def handle_warning(notification):
        print(f"⚠️ 경고: {notification['title']} - {notification['body']}")
    
    @client.on_notification('error')
    async def handle_error(notification):
        print(f"🚨 오류: {notification['title']} - {notification['body']}")
    
    # 연결
    await client.connect()
    
    # 5초 후 ping 전송
    await asyncio.sleep(5)
    await client.ping()
    
    return client


async def advanced_example():
    """고급 사용 예제"""
    print("🚀 고급 예제 시작...")
    
    client = NotificationClient(
        base_url='ws://localhost',
        user_id='user-advanced-123',
        auto_reconnect=True,
        reconnect_interval=3.0,
        max_reconnect_attempts=5
    )
    
    # 이벤트 핸들러들
    @client.on('connect')
    async def on_connect():
        print("🎉 연결됨!", client.get_connection_info())
    
    @client.on('disconnect')
    async def on_disconnect():
        print("😢 연결 끊김")
    
    @client.on('message')
    async def on_message(data):
        print(f"📥 수신: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 특정 조건의 알림 처리
    @client.on_notification('warning')
    async def handle_critical_warning(notification):
        data = notification.get('data', {})
        if data.get('disk_usage', 0) > 90:
            print(f"🚨 긴급: 디스크 사용량 위험! {data['disk_usage']}%")
    
    await client.connect()
    return client


async def sender_example():
    """알림 전송 예제"""
    print("📤 알림 전송 예제...")
    
    sender = NotificationSender('http://localhost')
    
    # 기본 알림 전송
    result = sender.send_notification(
        recipients=['11111111-1111-1111-1111-111111111111'],
        title='Python 클라이언트 테스트',
        body='이것은 Python에서 전송한 테스트 알림입니다.',
        kind='info'
    )
    
    if result:
        print(f"✅ 알림 전송 완료: {result['message_id']}")
    
    # 데이터가 포함된 경고 알림
    result = sender.send_notification(
        recipients=['11111111-1111-1111-1111-111111111111'],
        title='시스템 경고',
        body='디스크 사용량이 높습니다.',
        kind='warning',
        severity='yellow',
        data={
            'disk_usage': 85,
            'server': 'python-test-server',
            'timestamp': datetime.now().isoformat()
        }
    )


async def interactive_example():
    """대화형 예제"""
    print("🎮 대화형 예제 시작...")
    print("명령어: ping, send, info, quit")
    
    client = NotificationClient('ws://localhost')
    sender = NotificationSender('http://localhost')
    
    @client.on_notification('info')
    async def handle_any(notification):
        print(f"🔔 알림: {notification.get('title', '')} - {notification.get('body', '')}")
    
    await client.connect()
    
    while True:
        try:
            cmd = input("\n명령어 입력 > ").strip().lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'ping':
                await client.ping()
            elif cmd == 'send':
                sender.send_notification(
                    recipients=[client.user_id],
                    title='대화형 테스트',
                    body=f'시간: {datetime.now().strftime("%H:%M:%S")}'
                )
            elif cmd == 'info':
                print(f"연결 정보: {client.get_connection_info()}")
            else:
                print("알 수 없는 명령어. (ping, send, info, quit)")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"오류: {e}")
    
    await client.disconnect()


async def main():
    """메인 함수"""
    print("🔔 Python 알림 클라이언트")
    print("=" * 50)
    
    # 예제 선택
    examples = {
        '1': ('기본 예제', basic_example),
        '2': ('고급 예제', advanced_example),
        '3': ('전송 예제', sender_example),
        '4': ('대화형 예제', interactive_example)
    }
    
    print("예제를 선택하세요:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    try:
        choice = input("\n선택 (1-4, Enter=기본): ").strip() or '1'
        
        if choice in examples:
            name, example_func = examples[choice]
            print(f"\n🚀 {name} 실행 중...")
            
            if choice == '3':  # 전송 예제는 async가 아님
                await example_func()
            else:
                client = await example_func()
                
                # Ctrl+C 처리
                def signal_handler(signum, frame):
                    print("\n👋 종료 중...")
                    asyncio.create_task(client.disconnect())
                    sys.exit(0)
                
                signal.signal(signal.SIGINT, signal_handler)
                
                # 무한 대기 (Ctrl+C로 종료)
                if choice != '4':  # 대화형 예제가 아닌 경우
                    print("Ctrl+C로 종료하세요...")
                    try:
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        await client.disconnect()
        else:
            print("잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n👋 종료합니다.")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")

