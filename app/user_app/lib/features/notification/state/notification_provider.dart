import 'dart:async';
import 'package:flutter/material.dart';
import '../models/notification_models.dart';
import '../service/notification_service.dart';

class NotificationProvider extends ChangeNotifier {
  final NotificationService _notificationService = NotificationService();
  
  bool _isConnected = false;
  String? _currentUserId;
  List<NotificationMessage> _messages = [];
  bool _isLoading = false;
  String? _errorMessage;

  // Getters
  bool get isConnected => _isConnected;
  String? get currentUserId => _currentUserId;
  List<NotificationMessage> get messages => List.unmodifiable(_messages);
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

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
      final messages = await _notificationService.getMessages();
      _messages = messages;
      notifyListeners();
    } catch (e) {
      print('메시지 로드 오류: $e');
    }
  }

  // 새 메시지 추가
  void _addMessage(NotificationMessage message) {
    _messages.insert(0, message); // 최신 메시지를 맨 위에 추가
    notifyListeners();
  }

  // 메시지 삭제
  void removeMessage(String messageId) {
    _messages.removeWhere((msg) => msg.id == messageId);
    notifyListeners();
  }

  // 모든 메시지 삭제
  void clearMessages() {
    _messages.clear();
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

  @override
  void dispose() {
    _notificationSubscription?.cancel();
    _connectionSubscription?.cancel();
    _notificationService.dispose();
    super.dispose();
  }
}
