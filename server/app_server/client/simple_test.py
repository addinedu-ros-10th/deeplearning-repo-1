#!/usr/bin/env python3
"""
간단한 알림 수신 테스트
"""

import asyncio
from notification_client import NotificationClient

# 고정된 사용자 ID 사용
USER_ID = "test-user-12345"

async def simple_test():
    print(f"🚀 간단한 알림 수신 테스트 시작")
    print(f"👤 사용자 ID: {USER_ID}")
    print("=" * 50)
    
    client = NotificationClient(
        base_url='ws://localhost',
        user_id=USER_ID,
        auto_reconnect=False,
        enable_logging=True
    )
    
    # 알림 수신 핸들러
    @client.on_notification('info')
    async def handle_info(notification):
        print(f"ℹ️ 정보 알림: {notification.get('title')} - {notification.get('body')}")
    
    @client.on_notification('warning')
    async def handle_warning(notification):
        print(f"⚠️ 경고 알림: {notification.get('title')} - {notification.get('body')}")
    
    @client.on_notification('error')
    async def handle_error(notification):
        print(f"🚨 오류 알림: {notification.get('title')} - {notification.get('body')}")
    
    # 연결 이벤트
    @client.on('connect')
    async def on_connect():
        print("✅ 연결 성공! 알림을 기다리는 중...")
        print()
        print("다른 터미널에서 다음 명령어로 알림을 전송하세요:")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"info\",\"severity\":\"green\",\"title\":\"테스트\",\"body\":\"Hello!\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\"}}'")
        print()
    
    @client.on('message')
    async def on_message(data):
        print(f"📨 메시지 수신: {data}")
    
    # 연결
    await client.connect()
    
    # 20초 동안 대기
    print("20초 동안 알림을 기다립니다...")
    await asyncio.sleep(20)
    
    await client.disconnect()
    print("테스트 완료!")

if __name__ == '__main__':
    asyncio.run(simple_test())
