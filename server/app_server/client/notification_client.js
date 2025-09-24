/**
 * WebSocket 알림 클라이언트 (Node.js/Browser)
 * 
 * 사용 방법:
 * 1. Node.js 환경에서 실행:
 *    npm install ws
 *    node notification_client.js
 * 
 * 2. 브라우저에서 사용:
 *    <script src="notification_client.js"></script>
 *    <script>
 *      const client = new NotificationClient('ws://localhost', 'your-user-id');
 *      client.connect();
 *    </script>
 * 
 * 3. 커스텀 설정으로 사용:
 *    const client = new NotificationClient('ws://localhost', 'user-123', {
 *      autoReconnect: true,
 *      reconnectInterval: 5000,
 *      maxReconnectAttempts: 10
 *    });
 */

// Node.js 환경에서 WebSocket 라이브러리 import
let WebSocket;
if (typeof window === 'undefined') {
    // Node.js 환경
    try {
        WebSocket = require('ws');
    } catch (e) {
        console.error('WebSocket 라이브러리가 필요합니다. npm install ws 명령어를 실행하세요.');
        process.exit(1);
    }
} else {
    // 브라우저 환경
    WebSocket = window.WebSocket;
}

/**
 * 알림 클라이언트 클래스
 */
class NotificationClient {
    /**
     * 생성자
     * @param {string} baseUrl - WebSocket 서버 URL (예: 'ws://localhost')
     * @param {string} userId - 사용자 ID (UUID 형식 권장)
     * @param {Object} options - 설정 옵션
     * @param {boolean} options.autoReconnect - 자동 재연결 여부 (기본값: true)
     * @param {number} options.reconnectInterval - 재연결 간격 (밀리초, 기본값: 5000)
     * @param {number} options.maxReconnectAttempts - 최대 재연결 시도 횟수 (기본값: 10)
     * @param {boolean} options.enableLogging - 로그 출력 여부 (기본값: true)
     */
    constructor(baseUrl, userId, options = {}) {
        this.baseUrl = baseUrl;
        this.userId = userId;
        this.options = {
            autoReconnect: true,
            reconnectInterval: 5000,
            maxReconnectAttempts: 10,
            enableLogging: true,
            ...options
        };
        
        this.ws = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.messageHandlers = new Map();
        this.eventListeners = new Map();
        
        // 기본 이벤트 리스너 등록
        this.on('connect', () => this.log('✅ WebSocket 연결 성공'));
        this.on('disconnect', () => this.log('🔌 WebSocket 연결 종료'));
        this.on('error', (error) => this.log('❌ WebSocket 오류:', error));
        this.on('message', (data) => this.log('📨 알림 수신:', data));
    }
    
    /**
     * WebSocket 연결
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.log('⚠️ 이미 연결되어 있습니다.');
            return;
        }
        
        const url = `${this.baseUrl}/ws?user_id=${encodeURIComponent(this.userId)}`;
        this.log('🔄 연결 시도 중...', url);
        
        try {
            this.ws = new WebSocket(url);
            this.setupEventHandlers();
        } catch (error) {
            this.log('❌ 연결 실패:', error.message);
            this.handleReconnect();
        }
    }
    
    /**
     * WebSocket 연결 해제
     */
    disconnect() {
        this.options.autoReconnect = false;
        this.clearReconnectTimer();
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.connected = false;
        this.emit('disconnect');
    }
    
    /**
     * 메시지 전송
     * @param {string|Object} message - 전송할 메시지
     */
    send(message) {
        if (!this.connected) {
            this.log('❌ 연결되지 않음. 메시지 전송 실패');
            return false;
        }
        
        try {
            const data = typeof message === 'string' ? message : JSON.stringify(message);
            this.ws.send(data);
            this.log('📤 메시지 전송:', data);
            return true;
        } catch (error) {
            this.log('❌ 메시지 전송 오류:', error.message);
            return false;
        }
    }
    
    /**
     * Ping 전송 (연결 테스트)
     */
    ping() {
        return this.send('ping');
    }
    
    /**
     * 이벤트 리스너 등록
     * @param {string} event - 이벤트 이름 ('connect', 'disconnect', 'message', 'error')
     * @param {Function} handler - 이벤트 핸들러
     */
    on(event, handler) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(handler);
    }
    
    /**
     * 이벤트 리스너 제거
     * @param {string} event - 이벤트 이름
     * @param {Function} handler - 제거할 핸들러
     */
    off(event, handler) {
        const handlers = this.eventListeners.get(event);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    /**
     * 특정 타입의 알림에 대한 핸들러 등록
     * @param {string} notificationType - 알림 타입 ('info', 'warning', 'error')
     * @param {Function} handler - 알림 핸들러
     */
    onNotification(notificationType, handler) {
        if (!this.messageHandlers.has(notificationType)) {
            this.messageHandlers.set(notificationType, []);
        }
        this.messageHandlers.get(notificationType).push(handler);
    }
    
    /**
     * 연결 상태 확인
     * @returns {boolean} 연결 상태
     */
    isConnected() {
        return this.connected;
    }
    
    /**
     * 연결 정보 반환
     * @returns {Object} 연결 정보
     */
    getConnectionInfo() {
        return {
            baseUrl: this.baseUrl,
            userId: this.userId,
            connected: this.connected,
            reconnectAttempts: this.reconnectAttempts,
            readyState: this.ws ? this.ws.readyState : null
        };
    }
    
    // === 내부 메서드들 ===
    
    /**
     * WebSocket 이벤트 핸들러 설정
     */
    setupEventHandlers() {
        this.ws.onopen = () => {
            this.connected = true;
            this.reconnectAttempts = 0;
            this.clearReconnectTimer();
            this.emit('connect');
        };
        
        this.ws.onmessage = (event) => {
            try {
                // JSON 파싱 시도
                const data = JSON.parse(event.data);
                this.handleNotificationMessage(data);
                this.emit('message', data);
            } catch (e) {
                // 일반 텍스트 메시지
                this.emit('message', event.data);
            }
        };
        
        this.ws.onclose = (event) => {
            this.connected = false;
            this.emit('disconnect', event);
            
            if (this.options.autoReconnect) {
                this.handleReconnect();
            }
        };
        
        this.ws.onerror = (error) => {
            this.emit('error', error);
        };
    }
    
    /**
     * 알림 메시지 처리
     * @param {Object} notification - 알림 데이터
     */
    handleNotificationMessage(notification) {
        if (notification.kind) {
            const handlers = this.messageHandlers.get(notification.kind);
            if (handlers) {
                handlers.forEach(handler => {
                    try {
                        handler(notification);
                    } catch (error) {
                        this.log('❌ 알림 핸들러 오류:', error.message);
                    }
                });
            }
        }
    }
    
    /**
     * 재연결 처리
     */
    handleReconnect() {
        if (!this.options.autoReconnect || 
            this.reconnectAttempts >= this.options.maxReconnectAttempts) {
            this.log('🚫 재연결 중단 (최대 시도 횟수 초과)');
            return;
        }
        
        this.reconnectAttempts++;
        this.log(`🔄 재연결 시도 ${this.reconnectAttempts}/${this.options.maxReconnectAttempts}`);
        
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.options.reconnectInterval);
    }
    
    /**
     * 재연결 타이머 정리
     */
    clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }
    
    /**
     * 이벤트 발생
     * @param {string} event - 이벤트 이름
     * @param {...any} args - 이벤트 인수
     */
    emit(event, ...args) {
        const handlers = this.eventListeners.get(event);
        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler(...args);
                } catch (error) {
                    this.log('❌ 이벤트 핸들러 오류:', error.message);
                }
            });
        }
    }
    
    /**
     * 로그 출력
     * @param {...any} args - 로그 메시지
     */
    log(...args) {
        if (this.options.enableLogging) {
            const timestamp = new Date().toLocaleTimeString();
            console.log(`[${timestamp}] NotificationClient:`, ...args);
        }
    }
}

// === 사용 예제 ===

/**
 * 기본 사용 예제
 */
function basicExample() {
    // 클라이언트 생성
    const client = new NotificationClient('ws://localhost', '11111111-1111-1111-1111-111111111111');
    
    // 알림 타입별 핸들러 등록
    client.onNotification('info', (notification) => {
        console.log('ℹ️ 정보 알림:', notification.title, '-', notification.body);
    });
    
    client.onNotification('warning', (notification) => {
        console.log('⚠️ 경고 알림:', notification.title, '-', notification.body);
    });
    
    client.onNotification('error', (notification) => {
        console.log('🚨 오류 알림:', notification.title, '-', notification.body);
        // 오류 알림 시 특별한 처리 (예: 사용자에게 팝업 표시)
    });
    
    // 연결
    client.connect();
    
    // 5초 후 ping 전송
    setTimeout(() => {
        client.ping();
    }, 5000);
    
    return client;
}

/**
 * 고급 사용 예제
 */
function advancedExample() {
    const client = new NotificationClient('ws://localhost', 'user-advanced-123', {
        autoReconnect: true,
        reconnectInterval: 3000,
        maxReconnectAttempts: 5,
        enableLogging: true
    });
    
    // 연결 상태 변경 이벤트
    client.on('connect', () => {
        console.log('🎉 연결됨! 사용자 정보:', client.getConnectionInfo());
    });
    
    client.on('disconnect', () => {
        console.log('😢 연결 끊김');
    });
    
    // 모든 메시지 로깅
    client.on('message', (data) => {
        console.log('📥 수신된 메시지:', JSON.stringify(data, null, 2));
    });
    
    // 특정 데이터가 포함된 알림 처리
    client.onNotification('warning', (notification) => {
        if (notification.data && notification.data.disk_usage > 90) {
            console.log('🚨 긴급: 디스크 사용량 위험 수준!', notification.data.disk_usage + '%');
        }
    });
    
    client.connect();
    
    return client;
}

// Node.js 환경에서 직접 실행 시
if (typeof window === 'undefined' && require.main === module) {
    console.log('🚀 알림 클라이언트 시작...');
    console.log('Ctrl+C로 종료할 수 있습니다.');
    
    // 기본 예제 실행
    const client = basicExample();
    
    // 종료 시 정리
    process.on('SIGINT', () => {
        console.log('\n👋 클라이언트 종료 중...');
        client.disconnect();
        process.exit(0);
    });
}

// 브라우저 또는 모듈 환경에서 사용할 수 있도록 export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NotificationClient, basicExample, advancedExample };
}

if (typeof window !== 'undefined') {
    window.NotificationClient = NotificationClient;
    window.notificationClientExamples = { basicExample, advancedExample };
}
