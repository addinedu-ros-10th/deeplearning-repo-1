#!/usr/bin/env python3
"""
실시간 알림 송수신 테스트 스크립트

사용법:
1. 이 스크립트를 실행하면 WebSocket 클라이언트가 시작됩니다
2. 다른 터미널에서 curl 명령어로 알림을 전송합니다
3. 실시간으로 알림 수신을 확인할 수 있습니다
"""

import asyncio
import sys
import json
import signal
from datetime import datetime
from notification_client import NotificationClient, NotificationSender

class LiveNotificationTester:
    def __init__(self):
        self.client = None
        self.sender = NotificationSender('http://localhost')
        self.user_id = 'live-test-user-' + str(int(datetime.now().timestamp()))
        self.running = True
        
    async def start_client(self):
        """WebSocket 클라이언트 시작"""
        print(f"🚀 실시간 알림 테스트 시작")
        print(f"👤 사용자 ID: {self.user_id}")
        print("=" * 60)
        
        self.client = NotificationClient(
            base_url='ws://localhost',
            user_id=self.user_id,
            auto_reconnect=True,
            reconnect_interval=3.0,
            enable_logging=True
        )
        
        # 이벤트 핸들러 등록
        await self.setup_handlers()
        
        # 연결 시작
        await self.client.connect()
        
        # 연결 성공 후 가이드 출력
        await asyncio.sleep(2)  # 연결 완료 대기
        if self.client.is_connected():
            self.print_guide()
        
        # 메인 루프
        await self.main_loop()
    
    async def setup_handlers(self):
        """이벤트 핸들러 설정"""
        
        async def on_connect():
            print("✅ WebSocket 연결 성공!")
            print(f"📊 연결 정보: {self.client.get_connection_info()}")
            print()
        
        async def on_disconnect():
            print("🔌 WebSocket 연결 해제")
        
        async def on_error(error):
            print(f"❌ 연결 오류: {error}")
        
        async def on_message(data):
            timestamp = datetime.now().strftime("%H:%M:%S")
            if isinstance(data, dict):
                print(f"\n📨 [{timestamp}] 알림 수신:")
                print(f"   제목: {data.get('title', 'N/A')}")
                print(f"   내용: {data.get('body', 'N/A')}")
                print(f"   종류: {data.get('kind', 'N/A')} ({data.get('severity', 'N/A')})")
                if data.get('data'):
                    print(f"   데이터: {json.dumps(data['data'], indent=2, ensure_ascii=False)}")
                print("-" * 50)
            else:
                print(f"\n📨 [{timestamp}] 텍스트 메시지: {data}")
        
        # 알림 타입별 핸들러
        @self.client.on_notification('info')
        async def handle_info(notification):
            print(f"ℹ️  정보 알림 처리 완료: {notification.get('title')}")
        
        @self.client.on_notification('warning')
        async def handle_warning(notification):
            print(f"⚠️  경고 알림 처리 완료: {notification.get('title')}")
        
        @self.client.on_notification('error')
        async def handle_error(notification):
            print(f"🚨 오류 알림 처리 완료: {notification.get('title')}")
        
        # 핸들러 등록
        self.client.on('connect', on_connect)
        self.client.on('disconnect', on_disconnect)
        self.client.on('error', on_error)
        self.client.on('message', on_message)
    
    def print_guide(self):
        """사용법 가이드 출력"""
        print("🎯 알림 전송 방법:")
        print()
        print("1️⃣ 새 터미널을 열고 다음 명령어를 실행하세요:")
        print()
        print("# 정보 알림 전송")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{")
        print(f'  "kind": "info",')
        print(f'  "severity": "green",')
        print(f'  "title": "테스트 정보 알림",')
        print(f'  "body": "이것은 정보 알림 테스트입니다.",')
        print(f'  "recipients": ["{self.user_id}"],')
        print(f'  "channel": "websocket"')
        print(f"}}'")
        print()
        print("# 경고 알림 전송")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{")
        print(f'  "kind": "system",')
        print(f'  "severity": "yellow",')
        print(f'  "title": "⚠️ 시스템 경고",')
        print(f'  "body": "디스크 사용량이 80%를 초과했습니다.",')
        print(f'  "data": {{"disk_usage": 85, "server": "test-01"}},')
        print(f'  "recipients": ["{self.user_id}"],')
        print(f'  "channel": "websocket"')
        print(f"}}'")
        print()
        print("# 오류 알림 전송")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{")
        print(f'  "kind": "system",')
        print(f'  "severity": "red",')
        print(f'  "title": "🚨 시스템 오류",')
        print(f'  "body": "데이터베이스 연결에 실패했습니다.",')
        print(f'  "data": {{"error_code": "DB_CONNECTION_FAILED"}},')
        print(f'  "recipients": ["{self.user_id}"],')
        print(f'  "channel": "websocket"')
        print(f"}}'")
        print()
        print("2️⃣ 또는 대화형 명령어를 사용하세요:")
        print("   - 'ping': 연결 테스트")
        print("   - 'send': 자동 알림 전송")
        print("   - 'info': 연결 정보 확인")
        print("   - 'quit': 종료")
        print()
        print("=" * 60)
        print("💡 알림 전송 후 이 화면에서 실시간으로 수신 내용을 확인하세요!")
        print("=" * 60)
        print()
    
    async def main_loop(self):
        """메인 대화형 루프"""
        print("명령어를 입력하세요 (ping, send, info, quit):")
        
        while self.running and self.client and self.client.is_connected():
            try:
                # 비동기 입력 처리
                cmd = await asyncio.to_thread(input, "> ")
                cmd = cmd.strip().lower()
                
                if cmd == 'quit' or cmd == 'q':
                    self.running = False
                    break
                elif cmd == 'ping':
                    await self.client.ping()
                    print("📤 Ping 전송됨")
                elif cmd == 'send':
                    await self.send_test_notification()
                elif cmd == 'info':
                    print(f"📊 연결 정보: {self.client.get_connection_info()}")
                elif cmd == 'help' or cmd == 'h':
                    self.print_guide()
                elif cmd == '':
                    continue
                else:
                    print("알 수 없는 명령어. (ping, send, info, quit, help)")
                    
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"❌ 명령어 처리 오류: {e}")
        
        await self.cleanup()
    
    async def send_test_notification(self):
        """테스트 알림 전송"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = self.sender.send_notification(
            recipients=[self.user_id],
            title=f"🤖 자동 테스트 알림",
            body=f"시간: {timestamp} - Python 클라이언트에서 전송한 테스트 알림입니다.",
            kind='info',
            data={
                'sender': 'python_client',
                'timestamp': timestamp,
                'test_data': {'counter': 1, 'automated': True}
            }
        )
        
        if result:
            print(f"✅ 알림 전송 성공: {result['message_id']}")
        else:
            print("❌ 알림 전송 실패")
    
    async def cleanup(self):
        """정리 작업"""
        print("\n👋 클라이언트 종료 중...")
        if self.client:
            await self.client.disconnect()
        print("✅ 종료 완료")

async def main():
    """메인 함수"""
    tester = LiveNotificationTester()
    
    # Ctrl+C 처리
    def signal_handler(signum, frame):
        print("\n\n⚠️ 중단 신호 수신...")
        tester.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await tester.start_client()
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        await tester.cleanup()

if __name__ == '__main__':
    print("🔔 실시간 알림 송수신 테스트")
    print("Ctrl+C로 언제든지 종료할 수 있습니다.")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 프로그램 종료")
