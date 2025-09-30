import 'dart:async';
import 'package:flutter/material.dart';
import '../models/notification_models.dart';
import '../models/emergency_notification.dart';
import '../service/notification_service.dart';
import '../services/emergency_notification_service.dart';
import '../ui/notification_dialog.dart';

class NotificationProvider extends ChangeNotifier {
  final NotificationService _notificationService = NotificationService();
  
  bool _isConnected = false;
  String? _currentUserId;
  List<NotificationMessage> _messages = [];
  List<EmergencyNotification> _emergencyNotifications = [];
  bool _isLoading = false;
  String? _errorMessage;
  Set<String> _readMessageIds = {}; // 읽은 메시지 ID 추적
  BuildContext? _context; // 긴급 알림 표시를 위한 컨텍스트

  // Getters
  bool get isConnected => _isConnected;
  String? get currentUserId => _currentUserId;
  List<NotificationMessage> get messages => List.unmodifiable(_messages);
  List<EmergencyNotification> get emergencyNotifications => List.unmodifiable(_emergencyNotifications);
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  
  // 읽지 않은 메시지 개수
  int get unreadCount => _messages.where((msg) => !_readMessageIds.contains(msg.id)).length;
  
  // 읽지 않은 메시지 목록
  List<NotificationMessage> get unreadMessages => 
      _messages.where((msg) => !_readMessageIds.contains(msg.id)).toList();
  
  // 긴급 알림 개수
  int get emergencyCount => _emergencyNotifications.length;
  
  // 위기 단계 5단계 알림 개수
  int get emergencyLevel5Count => _emergencyNotifications.where((n) => n.isEmergencyLevel5).length;

  // 알림 서비스 스트림 구독
  StreamSubscription<NotificationMessage>? _notificationSubscription;
  StreamSubscription<bool>? _connectionSubscription;

  NotificationProvider() {
    _setupStreams();
  }

  void _setupStreams() {
    // 연결 상태 스트림 구독
    _connectionSubscription = _notificationService.connectionStream.listen(
      (connected) {
        _isConnected = connected;
        notifyListeners();
      },
    );

    // 알림 메시지 스트림 구독
    _notificationSubscription = _notificationService.notificationStream.listen(
      (notification) {
        _addMessage(notification);
      },
    );
  }

  // 사용자 연결
  Future<bool> connect(String userId) async {
    _setLoading(true);
    _clearError();

    try {
      final success = await _notificationService.connect(userId);
      if (success) {
        _currentUserId = userId;
        await _loadMessages(); // 기존 메시지 로드
      } else {
        _setError('연결에 실패했습니다.');
      }
      return success;
    } catch (e) {
      _setError('연결 오류: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // 연결 해제
  Future<void> disconnect() async {
    await _notificationService.disconnect();
    _currentUserId = null;
    _messages.clear();
    notifyListeners();
  }

  // 알림 전송
  Future<bool> sendNotification({
    required List<String> recipients,
    required String title,
    required String body,
    NotificationKind kind = NotificationKind.info,
    NotificationSeverity severity = NotificationSeverity.blue,
    String channel = 'websocket',
    Map<String, dynamic>? metadata,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _notificationService.sendNotification(
        recipients: recipients,
        title: title,
        body: body,
        kind: kind,
        severity: severity,
        channel: channel,
        metadata: metadata,
      );

      if (response != null) {
        return true;
      } else {
        _setError('알림 전송에 실패했습니다.');
        return false;
      }
    } catch (e) {
      _setError('알림 전송 오류: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // 메시지 목록 로드
  Future<void> _loadMessages() async {
    try {
      // 현재 사용자 ID가 있으면 사용자별 메시지 조회
      final messages = await _notificationService.getMessages(
        userId: _currentUserId,
      );
      _messages = messages;
      notifyListeners();
    } catch (e) {
      print('메시지 로드 오류: $e');
    }
  }

  // 새 메시지 추가
  void _addMessage(NotificationMessage message) {
    print('=== 새 알림 도착 ===');
    print('알림 ID: ${message.id}');
    print('제목: ${message.title}');
    print('내용: ${message.body}');
    print('kind: ${message.kind}');
    print('severity: ${message.severity}');
    print('생성 시간: ${message.createdAt}');
    print('메타데이터: ${message.metadata}');
    print('==================');
    
    _messages.insert(0, message); // 최신 메시지를 맨 위에 추가
    notifyListeners();
    
    // 긴급 알림인지 확인하고 처리
    _checkAndHandleEmergencyNotification(message);
  }

  // 긴급 알림 확인 및 처리
  void _checkAndHandleEmergencyNotification(NotificationMessage message) {
    // NotificationMessage를 EmergencyNotification으로 변환
    final emergencyNotification = EmergencyNotification(
      id: message.id,
      kind: message.kind,
      severity: message.severity,
      title: message.title,
      message: message.body,
      timestamp: message.createdAt,
      isRead: _readMessageIds.contains(message.id),
      metadata: message.metadata,
    );
    
    print('긴급 알림 확인: kind=${message.kind}, severity=${message.severity}, isEmergency=${emergencyNotification.isEmergency}, isEmergencyLevel5=${emergencyNotification.isEmergencyLevel5}');

    // 긴급 알림인지 확인
    if (emergencyNotification.isEmergency) {
      _emergencyNotifications.insert(0, emergencyNotification);
      
      // 위기 단계 5단계 알림이면 즉시 다이얼로그 표시
      if (emergencyNotification.isEmergencyLevel5 && _context != null) {
        EmergencyNotificationService.showEmergencyAlert(_context!, emergencyNotification);
      }
      
      notifyListeners();
    }
  }

  // 메시지 읽음 처리
  void markAsRead(String messageId) {
    _readMessageIds.add(messageId);
    notifyListeners();
  }

  // 모든 메시지 읽음 처리
  void markAllAsRead() {
    _readMessageIds.addAll(_messages.map((msg) => msg.id));
    notifyListeners();
  }

  // 메시지 삭제
  void removeMessage(String messageId) {
    _messages.removeWhere((msg) => msg.id == messageId);
    _readMessageIds.remove(messageId); // 읽음 상태도 제거
    notifyListeners();
  }

  // 모든 메시지 삭제
  void clearMessages() {
    _messages.clear();
    _readMessageIds.clear();
    notifyListeners();
  }

  // 로딩 상태 설정
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // 에러 설정
  void _setError(String error) {
    _errorMessage = error;
    notifyListeners();
  }

  // 에러 클리어
  void _clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // 컨텍스트 설정 (긴급 알림 표시용)
  void setContext(BuildContext context) {
    _context = context;
  }

  // 긴급 알림 추가 (테스트용)
  void addEmergencyNotification(EmergencyNotification notification) {
    print('긴급 알림 추가: ${notification.title}');
    print('kind: ${notification.kind}, severity: ${notification.severity}');
    print('isEmergency: ${notification.isEmergency}, isEmergencyLevel5: ${notification.isEmergencyLevel5}');
    print('context is null: ${_context == null}');
    
    _emergencyNotifications.insert(0, notification);
    notifyListeners();
    
    // 위기 단계 5단계 알림이면 즉시 다이얼로그 표시
    if (notification.isEmergencyLevel5 && _context != null) {
      print('위기 5단계 다이얼로그 표시 시도');
      
      // context 유효성 검사
      if (_context!.mounted) {
        EmergencyNotificationService.showEmergencyAlert(_context!, notification);
      } else {
        print('context가 mounted되지 않음. 긴급 알림을 대기열에 추가합니다.');
        // TODO: 긴급 알림을 대기열에 추가하여 나중에 표시
      }
    } else {
      print('다이얼로그 표시 조건 미충족: isEmergencyLevel5=${notification.isEmergencyLevel5}, context=${_context != null}');
    }
  }

  // 긴급 알림 제거
  void removeEmergencyNotification(String notificationId) {
    _emergencyNotifications.removeWhere((n) => n.id == notificationId);
    notifyListeners();
  }

  // 모든 긴급 알림 제거
  void clearEmergencyNotifications() {
    _emergencyNotifications.clear();
    notifyListeners();
  }

  // 긴급 알림 읽음 처리
  void markEmergencyAsRead(String notificationId) {
    final index = _emergencyNotifications.indexWhere((n) => n.id == notificationId);
    if (index != -1) {
      _emergencyNotifications[index] = _emergencyNotifications[index].copyWith(isRead: true);
      notifyListeners();
    }
  }

  // 테스트용 긴급 알림 생성
  void createTestEmergencyNotification() {
    final testNotification = EmergencyNotificationService.createTestEmergencyNotification();
    addEmergencyNotification(testNotification);
  }

  @override
  void dispose() {
    _notificationSubscription?.cancel();
    _connectionSubscription?.cancel();
    _notificationService.dispose();
    super.dispose();
  }
}
