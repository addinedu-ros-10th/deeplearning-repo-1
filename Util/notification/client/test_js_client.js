#!/usr/bin/env node

/**
 * JavaScript 클라이언트 테스트 스크립트
 */

// notification_client.js 모듈 로드
const { NotificationClient } = require('./notification_client.js');

console.log('🧪 JavaScript 클라이언트 테스트 시작...');

async function testBasicConnection() {
    console.log('\n1️⃣ 기본 연결 테스트');
    
    const client = new NotificationClient('ws://localhost', 'js-test-user-789', {
        enableLogging: true,
        autoReconnect: false
    });
    
    return new Promise((resolve) => {
        let connected = false;
        
        client.on('connect', () => {
            console.log('✅ 연결 성공!');
            connected = true;
            
            // 연결 정보 출력
            console.log('📊 연결 정보:', JSON.stringify(client.getConnectionInfo(), null, 2));
            
            // Ping 테스트
            setTimeout(() => {
                console.log('📤 Ping 전송...');
                client.ping();
            }, 1000);
            
            // 3초 후 연결 해제
            setTimeout(() => {
                console.log('🔌 연결 해제...');
                client.disconnect();
            }, 3000);
        });
        
        client.on('message', (data) => {
            console.log('📨 메시지 수신:', data);
        });
        
        client.on('disconnect', () => {
            console.log('👋 연결 해제 완료');
            resolve(connected);
        });
        
        client.on('error', (error) => {
            console.log('❌ 오류 발생:', error);
            resolve(false);
        });
        
        // 연결 시작
        console.log('🔄 연결 시도 중...');
        client.connect();
        
        // 10초 타임아웃
        setTimeout(() => {
            if (!connected) {
                console.log('⏰ 연결 타임아웃');
                client.disconnect();
                resolve(false);
            }
        }, 10000);
    });
}

async function testNotificationHandlers() {
    console.log('\n2️⃣ 알림 핸들러 테스트');
    
    const client = new NotificationClient('ws://localhost', 'js-handler-test-999', {
        enableLogging: false // 핸들러 테스트를 위해 로그 비활성화
    });
    
    return new Promise((resolve) => {
        let handlerTested = false;
        
        // 알림 타입별 핸들러 등록
        client.onNotification('info', (notification) => {
            console.log('ℹ️ 정보 알림 처리:', notification.title);
            handlerTested = true;
        });
        
        client.onNotification('warning', (notification) => {
            console.log('⚠️ 경고 알림 처리:', notification.title);
            handlerTested = true;
        });
        
        client.onNotification('error', (notification) => {
            console.log('🚨 오류 알림 처리:', notification.title);
            handlerTested = true;
        });
        
        client.on('connect', () => {
            console.log('✅ 핸들러 테스트용 연결 성공');
            
            // 가짜 알림 메시지 시뮬레이션
            setTimeout(() => {
                console.log('🎭 가짜 알림 메시지 시뮬레이션...');
                
                // 내부 메서드 직접 호출하여 알림 처리 테스트
                const fakeNotifications = [
                    { kind: 'info', title: '정보 테스트', body: '정보 알림입니다' },
                    { kind: 'warning', title: '경고 테스트', body: '경고 알림입니다' },
                    { kind: 'error', title: '오류 테스트', body: '오류 알림입니다' }
                ];
                
                fakeNotifications.forEach((notification, index) => {
                    setTimeout(() => {
                        client.handleNotificationMessage(notification);
                    }, index * 500);
                });
                
                // 3초 후 종료
                setTimeout(() => {
                    client.disconnect();
                }, 2000);
            }, 1000);
        });
        
        client.on('disconnect', () => {
            console.log('👋 핸들러 테스트 완료');
            resolve(handlerTested);
        });
        
        client.on('error', (error) => {
            console.log('❌ 핸들러 테스트 오류:', error);
            resolve(false);
        });
        
        client.connect();
    });
}

async function runAllTests() {
    console.log('🚀 JavaScript 클라이언트 종합 테스트');
    console.log('=' * 50);
    
    try {
        // 1. 기본 연결 테스트
        const connectionResult = await testBasicConnection();
        console.log(`\n📊 기본 연결 테스트: ${connectionResult ? '✅ 성공' : '❌ 실패'}`);
        
        // 잠시 대기
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 2. 알림 핸들러 테스트
        const handlerResult = await testNotificationHandlers();
        console.log(`📊 핸들러 테스트: ${handlerResult ? '✅ 성공' : '❌ 실패'}`);
        
        // 결과 요약
        console.log('\n' + '='.repeat(50));
        console.log('📈 테스트 결과 요약');
        console.log(`연결 테스트: ${connectionResult ? '✅' : '❌'}`);
        console.log(`핸들러 테스트: ${handlerResult ? '✅' : '❌'}`);
        
        const totalTests = 2;
        const passedTests = (connectionResult ? 1 : 0) + (handlerResult ? 1 : 0);
        console.log(`\n총 ${totalTests}개 테스트 중 ${passedTests}개 성공`);
        
        if (passedTests === totalTests) {
            console.log('🎉 모든 테스트 통과!');
        } else {
            console.log('⚠️ 일부 테스트 실패');
        }
        
    } catch (error) {
        console.error('❌ 테스트 실행 중 오류:', error);
    }
    
    process.exit(0);
}

// 메인 실행
if (require.main === module) {
    runAllTests().catch(console.error);
}

