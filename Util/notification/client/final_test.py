#!/usr/bin/env python3
"""
최종 알림 송수신 테스트 (UUID 형식 사용자 ID)
"""

import asyncio
import json
import uuid
from notification_client import NotificationClient

async def final_test():
    print("🚀 최종 알림 송수신 테스트")
    print("=" * 60)
    
    # UUID 형식의 사용자 ID 생성
    USER_ID = str(uuid.uuid4())
    
    print(f"👤 사용자 ID: {USER_ID}")
    print()
    
    # 클라이언트 생성
    client = NotificationClient(
        base_url='ws://localhost',
        user_id=USER_ID,
        auto_reconnect=False,
        enable_logging=True
    )
    
    # 수신 카운터
    received_notifications = []
    
    # 알림 핸들러들
    def handle_info(notification):
        received_notifications.append(notification)
        print(f"ℹ️  정보 알림 수신:")
        print(f"   제목: {notification.get('title')}")
        print(f"   내용: {notification.get('body')}")
        if notification.get('data'):
            print(f"   데이터: {json.dumps(notification['data'], indent=2, ensure_ascii=False)}")
        print()
    
    def handle_warning(notification):
        received_notifications.append(notification)
        print(f"⚠️  경고 알림 수신:")
        print(f"   제목: {notification.get('title')}")
        print(f"   내용: {notification.get('body')}")
        print()
    
    def handle_error(notification):
        received_notifications.append(notification)
        print(f"🚨 오류 알림 수신:")
        print(f"   제목: {notification.get('title')}")
        print(f"   내용: {notification.get('body')}")
        print()
    
    # 핸들러 등록
    client.add_notification_handler('info', handle_info)
    client.add_notification_handler('warning', handle_warning)
    client.add_notification_handler('error', handle_error)
    
    # 연결 이벤트
    def on_connect():
        print("✅ WebSocket 연결 성공!")
        print()
        print("🎯 다음 명령어들을 새 터미널에서 실행해보세요:")
        print()
        print("1️⃣ 정보 알림:")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"info\",\"severity\":\"green\",\"title\":\"✅ 성공\",\"body\":\"작업이 완료되었습니다\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\",\"data\":{{\"progress\":100,\"status\":\"completed\"}}}}'")
        print()
        print("2️⃣ 경고 알림:")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"warning\",\"severity\":\"yellow\",\"title\":\"⚠️ 주의\",\"body\":\"디스크 사용량이 80%를 초과했습니다\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\",\"data\":{{\"disk_usage\":85,\"server\":\"web-01\"}}}}'")
        print()
        print("3️⃣ 오류 알림:")
        print(f"curl -X POST 'http://localhost/api/v1/notify/queue' \\")
        print(f"-H 'Content-Type: application/json' \\")
        print(f"-d '{{\"kind\":\"error\",\"severity\":\"red\",\"title\":\"🚨 오류\",\"body\":\"데이터베이스 연결에 실패했습니다\",\"recipients\":[\"{USER_ID}\"],\"channel\":\"websocket\",\"data\":{{\"error_code\":\"DB_CONN_FAIL\",\"retry_count\":3}}}}'")
        print()
        print("=" * 60)
        print("💡 명령어 실행 후 이 화면에서 실시간 알림 수신을 확인하세요!")
        print("=" * 60)
        print()
    
    def on_message(data):
        if isinstance(data, str) and data == 'ping':
            print("🏓 Pong!")
    
    def on_disconnect():
        print("🔌 연결 해제")
    
    def on_error(error):
        print(f"❌ 오류: {error}")
    
    # 이벤트 핸들러 등록
    client.on('connect', on_connect)
    client.on('message', on_message)
    client.on('disconnect', on_disconnect)
    client.on('error', on_error)
    
    # 연결
    print("🔄 WebSocket 연결 중...")
    await client.connect()
    
    # 60초 동안 알림 대기
    print("60초 동안 알림을 기다립니다... (Ctrl+C로 중단)")
    try:
        for i in range(600):  # 60초 = 600 * 0.1초
            if not client.is_connected():
                print("❌ 연결이 끊어졌습니다.")
                break
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
    
    # 연결 해제
    await client.disconnect()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과:")
    print(f"   총 수신한 알림: {len(received_notifications)}개")
    
    if received_notifications:
        print("\n📝 수신한 알림 목록:")
        for i, notif in enumerate(received_notifications, 1):
            print(f"   {i}. [{notif.get('kind', 'unknown')}] {notif.get('title', 'N/A')}")
    else:
        print("\n💡 알림을 수신하지 못했습니다. 다음을 확인해보세요:")
        print("   - 서버가 정상 실행 중인지")
        print("   - 환경변수가 올바르게 설정되었는지 (NOTIFY_ENABLE=true)")
        print("   - 데이터베이스 연결이 정상인지")
    
    print("\n✅ 테스트 완료!")

if __name__ == '__main__':
    try:
        asyncio.run(final_test())
    except KeyboardInterrupt:
        print("\n👋 프로그램 종료")

