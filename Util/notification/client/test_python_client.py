#!/usr/bin/env python3
"""
Python 클라이언트 테스트 스크립트
"""

import asyncio
import sys
import os

# notification_client.py에서 클래스 import
from notification_client import NotificationClient, NotificationSender

async def test_websocket_connection():
    """WebSocket 연결 테스트"""
    print('\n1️⃣ WebSocket 연결 테스트')
    
    client = NotificationClient(
        base_url='ws://localhost',
        user_id='python-test-user-123',
        auto_reconnect=False,
        enable_logging=True
    )
    
    connected = False
    
    async def on_connect():
        nonlocal connected
        connected = True
        print('✅ Python 클라이언트 연결 성공!')
        print(f'📊 연결 정보: {client.get_connection_info()}')
        
        # 2초 후 ping 전송
        await asyncio.sleep(2)
        await client.ping()
        
        # 3초 후 연결 해제
        await asyncio.sleep(3)
        await client.disconnect()
    
    async def on_message(data):
        print(f'📨 메시지 수신: {data}')
    
    async def on_disconnect():
        print('👋 연결 해제 완료')
    
    async def on_error(error):
        print(f'❌ 오류 발생: {error}')
    
    # 이벤트 핸들러 등록
    client.on('connect', on_connect)
    client.on('message', on_message)
    client.on('disconnect', on_disconnect)
    client.on('error', on_error)
    
    # 연결 시작
    await client.connect()
    
    # 10초 대기 (연결 및 테스트 완료 대기)
    for i in range(100):  # 10초 = 100 * 0.1초
        await asyncio.sleep(0.1)
        if not client.is_connected():
            break
    
    return connected

async def test_notification_handlers():
    """알림 핸들러 테스트"""
    print('\n2️⃣ 알림 핸들러 테스트')
    
    client = NotificationClient(
        base_url='ws://localhost',
        user_id='python-handler-test-456',
        auto_reconnect=False,
        enable_logging=False  # 핸들러 테스트를 위해 로그 비활성화
    )
    
    handler_tested = False
    
    # 알림 핸들러들 등록
    @client.on_notification('info')
    async def handle_info(notification):
        nonlocal handler_tested
        print(f"ℹ️ 정보 알림 처리: {notification['title']}")
        handler_tested = True
    
    @client.on_notification('warning')
    async def handle_warning(notification):
        nonlocal handler_tested
        print(f"⚠️ 경고 알림 처리: {notification['title']}")
        handler_tested = True
    
    @client.on_notification('error')
    async def handle_error(notification):
        nonlocal handler_tested
        print(f"🚨 오류 알림 처리: {notification['title']}")
        handler_tested = True
    
    async def on_connect():
        print('✅ 핸들러 테스트용 연결 성공')
        
        # 1초 후 가짜 알림 메시지 시뮬레이션
        await asyncio.sleep(1)
        print('🎭 가짜 알림 메시지 시뮬레이션...')
        
        fake_notifications = [
            {'kind': 'info', 'title': '정보 테스트', 'body': '정보 알림입니다'},
            {'kind': 'warning', 'title': '경고 테스트', 'body': '경고 알림입니다'},
            {'kind': 'error', 'title': '오류 테스트', 'body': '오류 알림입니다'}
        ]
        
        for i, notification in enumerate(fake_notifications):
            await asyncio.sleep(i * 0.5)
            await client._handle_notification(notification)
        
        # 2초 후 연결 해제
        await asyncio.sleep(2)
        await client.disconnect()
    
    async def on_disconnect():
        print('👋 핸들러 테스트 완료')
    
    # 이벤트 핸들러 등록
    client.on('connect', on_connect)
    client.on('disconnect', on_disconnect)
    
    # 연결 시작
    await client.connect()
    
    # 대기
    for i in range(100):  # 10초
        await asyncio.sleep(0.1)
        if not client.is_connected():
            break
    
    return handler_tested

async def test_api_connection():
    """API 연결 테스트 (데이터베이스 없이)"""
    print('\n3️⃣ API 연결 테스트')
    
    sender = NotificationSender('http://localhost')
    
    # Health check 등 간단한 연결 테스트
    try:
        import requests
        response = requests.get('http://localhost/health', timeout=5)
        if response.status_code == 200:
            print('✅ API 서버 연결 성공')
            print(f'📊 서버 상태: {response.json()}')
            return True
        else:
            print(f'⚠️ API 서버 응답 이상: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ API 연결 실패: {e}')
        return False

async def run_all_tests():
    """모든 테스트 실행"""
    print('🚀 Python 클라이언트 종합 테스트')
    print('=' * 50)
    
    results = {}
    
    try:
        # 1. WebSocket 연결 테스트
        results['websocket'] = await test_websocket_connection()
        print(f'\n📊 WebSocket 연결 테스트: {"✅ 성공" if results["websocket"] else "❌ 실패"}')
        
        # 잠시 대기
        await asyncio.sleep(2)
        
        # 2. 알림 핸들러 테스트
        results['handlers'] = await test_notification_handlers()
        print(f'📊 핸들러 테스트: {"✅ 성공" if results["handlers"] else "❌ 실패"}')
        
        # 3. API 연결 테스트
        results['api'] = await test_api_connection()
        print(f'📊 API 연결 테스트: {"✅ 성공" if results["api"] else "❌ 실패"}')
        
        # 결과 요약
        print('\n' + '=' * 50)
        print('📈 테스트 결과 요약')
        print(f'WebSocket 연결: {"✅" if results["websocket"] else "❌"}')
        print(f'알림 핸들러: {"✅" if results["handlers"] else "❌"}')
        print(f'API 연결: {"✅" if results["api"] else "❌"}')
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        print(f'\n총 {total_tests}개 테스트 중 {passed_tests}개 성공')
        
        if passed_tests == total_tests:
            print('🎉 모든 테스트 통과!')
        else:
            print('⚠️ 일부 테스트 실패')
            if not results['websocket']:
                print('  - WebSocket 연결 문제: 서버 상태 확인 필요')
            if not results['api']:
                print('  - API 연결 문제: 서버 또는 네트워크 확인 필요')
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f'❌ 테스트 실행 중 오류: {e}')
        return False

if __name__ == '__main__':
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print('\n👋 테스트 중단됨')
        sys.exit(1)
