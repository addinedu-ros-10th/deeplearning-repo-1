#!/usr/bin/env python3
"""
실제 작동하는 알림 테스트
"""

import asyncio
import json
from notification_client import NotificationClient, NotificationSender

async def working_test():
    print("🚀 실제 알림 송수신 테스트")
    print("=" * 50)
    
    USER_ID = "working-test-user-123"
    
    # 클라이언트 생성
    client = NotificationClient(
        base_url='ws://localhost',
        user_id=USER_ID,
        auto_reconnect=False,
        enable_logging=True
    )
    
    # 알림 수신 카운터
    received_count = 0
    
    # 알림 타입별 핸들러 등록
    def handle_info(notification):
        nonlocal received_count
        received_count += 1
        print(f"ℹ️  [{received_count}] 정보 알림 수신:")
        print(f"   제목: {notification.get('title')}")
        print(f"   내용: {notification.get('body')}")
        if notification.get('data'):
            print(f"   데이터: {json.dumps(notification['data'], indent=2, ensure_ascii=False)}")
        print()
    
    def handle_warning(notification):
        nonlocal received_count
        received_count += 1
        print(f"⚠️  [{received_count}] 경고 알림 수신:")
        print(f"   제목: {notification.get('title')}")
        print(f"   내용: {notification.get('body')}")
        print()
    
    def handle_error(notification):
        nonlocal received_count
        received_count += 1
        print(f"🚨 [{received_count}] 오류 알림 수신:")
        print(f"   제목: {notification.get('title')}")
        print(f"   내용: {notification.get('body')}")
        print()
    
    # 핸들러 등록
    client.add_notification_handler('info', handle_info)
    client.add_notification_handler('warning', handle_warning)
    client.add_notification_handler('error', handle_error)
    
    # 연결 이벤트 핸들러
    def on_connect():
        print("✅ WebSocket 연결 성공!")
        print(f"👤 사용자 ID: {USER_ID}")
        print()
        print("🎯 알림 전송 명령어:")
        print()
        print("# 정보 알림")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"info\",\"severity\":\"green\",\"title\":\"정보 테스트\",\"body\":\"정보 알림 테스트입니다\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\"}}'")
        print()
        print("# 경고 알림")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"warning\",\"severity\":\"yellow\",\"title\":\"경고 테스트\",\"body\":\"경고 알림 테스트입니다\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\"}}'")
        print()
        print("# 오류 알림")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"error\",\"severity\":\"red\",\"title\":\"오류 테스트\",\"body\":\"오류 알림 테스트입니다\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\"}}'")
        print()
        print("=" * 50)
        print("💡 위 명령어를 새 터미널에서 실행하면 이곳에서 실시간으로 확인할 수 있습니다!")
        print("=" * 50)
        print()
    
    def on_message(data):
        if isinstance(data, str) and data != 'ping':
            print(f"📨 텍스트 메시지: {data}")
    
    def on_disconnect():
        print("🔌 연결 해제됨")
    
    def on_error(error):
        print(f"❌ 오류: {error}")
    
    # 이벤트 핸들러 등록
    client.on('connect', on_connect)
    client.on('message', on_message)
    client.on('disconnect', on_disconnect)
    client.on('error', on_error)
    
    # 연결
    await client.connect()
    
    # 30초 동안 알림 대기
    print("30초 동안 알림을 기다립니다...")
    for i in range(300):  # 30초 = 300 * 0.1초
        if not client.is_connected():
            print("❌ 연결이 끊어졌습니다.")
            break
        await asyncio.sleep(0.1)
    
    # 연결 해제
    await client.disconnect()
    
    print(f"\n📊 테스트 결과:")
    print(f"   수신한 알림 수: {received_count}개")
    print(f"   테스트 완료!")

if __name__ == '__main__':
    try:
        asyncio.run(working_test())
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단됨")

