import 'dart:convert';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../models/notification_models.dart';
import '../../../core/env/env.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final Dio _dio = Dio();
  WebSocketChannel? _channel;
  String? _currentUserId;
  bool _isConnected = false;
  
  // 스트림 컨트롤러들
  final StreamController<NotificationMessage> _notificationController = 
      StreamController<NotificationMessage>.broadcast();
  final StreamController<bool> _connectionController = 
      StreamController<bool>.broadcast();

  // Getters
  Stream<NotificationMessage> get notificationStream => _notificationController.stream;
  Stream<bool> get connectionStream => _connectionController.stream;
  bool get isConnected => _isConnected;
  String? get currentUserId => _currentUserId;

  // WebSocket 연결
  Future<bool> connect(String userId) async {
    try {
      // 알림 시스템이 비활성화된 경우
      if (!AppEnv.notifyEnabled) {
        print('알림 시스템이 비활성화되어 있습니다.');
        _isConnected = false;
        _connectionController.add(false);
        return false;
      }

      if (_isConnected && _currentUserId == userId) {
        return true;
      }

      // 기존 연결이 있으면 끊기
      await disconnect();

      _currentUserId = userId;
      
      // WebSocket URL 생성
      final wsUrl = _getWebSocketUrl();
      print('WebSocket 연결 시도: $wsUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse('$wsUrl?user_id=$userId'));
      
      // 연결 상태 리스너
      _channel!.ready.then((_) {
        _isConnected = true;
        _connectionController.add(true);
        print('WebSocket 연결 성공: $userId');
      });

      // 메시지 리스너
      _channel!.stream.listen(
        (data) {
          try {
            final jsonData = jsonDecode(data);
            final notification = NotificationMessage.fromJson(jsonData);
            _notificationController.add(notification);
            print('알림 수신: ${notification.title}');
          } catch (e) {
            print('알림 파싱 오류: $e');
          }
        },
        onError: (error) {
          print('WebSocket 오류: $error');
          _isConnected = false;
          _connectionController.add(false);
        },
        onDone: () {
          print('WebSocket 연결 종료');
          _isConnected = false;
          _connectionController.add(false);
        },
      );

      return true;
    } catch (e) {
      print('WebSocket 연결 실패: $e');
      _isConnected = false;
      _connectionController.add(false);
      return false;
    }
  }

  // WebSocket 연결 해제
  Future<void> disconnect() async {
    try {
      await _channel?.sink.close(status.goingAway);
      _channel = null;
      _isConnected = false;
      _currentUserId = null;
      _connectionController.add(false);
      print('WebSocket 연결 해제');
    } catch (e) {
      print('WebSocket 연결 해제 오류: $e');
    }
  }

  // 알림 전송
  Future<NotificationQueueResponse?> sendNotification({
    required List<String> recipients,
    required String title,
    required String body,
    NotificationKind kind = NotificationKind.info,
    NotificationSeverity severity = NotificationSeverity.blue,
    String channel = 'websocket',
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 알림 시스템이 비활성화된 경우
      if (!AppEnv.notifyEnabled) {
        print('알림 시스템이 비활성화되어 있습니다. 메시지 전송을 건너뜁니다.');
        return null;
      }

      final request = NotificationQueueRequest(
        kind: kind.value,
        severity: severity.value,
        title: title,
        body: body,
        recipients: recipients,
        channel: channel,
        metadata: metadata,
      );

      final response = await _dio.post(
        '${_getApiUrl()}/api/v1/notify/queue',
        data: request.toJson(),
        options: Options(
          headers: {'Content-Type': 'application/json'},
        ),
      );

      if (response.statusCode == 201) {
        return NotificationQueueResponse.fromJson(response.data);
      } else {
        print('알림 전송 실패: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('알림 전송 오류: $e');
      return null;
    }
  }

  // 메시지 목록 조회 (사용자별)
  Future<List<NotificationMessage>> getMessages({
    int skip = 0,
    int limit = 100,
    String? kind,
    String? severity,
    String? userId, // 사용자 ID 추가
  }) async {
    try {
      // 알림 시스템이 비활성화된 경우
      if (!AppEnv.notifyEnabled) {
        print('알림 시스템이 비활성화되어 있습니다. 빈 목록을 반환합니다.');
        return [];
      }

      // 사용자 ID가 제공된 경우 by-sender API 사용
      if (userId != null && userId.isNotEmpty) {
        return await _getMessagesBySender(
          userId: userId,
          skip: skip,
          limit: limit,
          kind: kind,
          severity: severity,
        );
      }

      // 기본 메시지 조회 API
      final queryParams = <String, dynamic>{
        'skip': skip,
        'limit': limit,
      };
      
      if (kind != null) queryParams['kind'] = kind;
      if (severity != null) queryParams['severity'] = severity;

      final response = await _dio.get(
        '${_getApiUrl()}/api/v1/notify/messages/',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => NotificationMessage.fromJson(json)).toList();
      } else {
        print('메시지 조회 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('메시지 조회 오류: $e');
      return [];
    }
  }

  // 사용자별 메시지 조회 (by-sender API)
  Future<List<NotificationMessage>> _getMessagesBySender({
    required String userId,
    int skip = 0,
    int limit = 100,
    String? kind,
    String? severity,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'skip': skip,
        'limit': limit,
      };
      
      if (kind != null) queryParams['kind'] = kind;
      if (severity != null) queryParams['severity'] = severity;

      final response = await _dio.get(
        '${_getApiUrl()}/api/v1/notify/messages/by-sender/$userId',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        print('사용자별 메시지 조회 성공: ${data.length}개 메시지');
        return data.map((json) => NotificationMessage.fromJson(json)).toList();
      } else {
        print('사용자별 메시지 조회 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('사용자별 메시지 조회 오류: $e');
      return [];
    }
  }

  // WebSocket URL 생성
  String _getWebSocketUrl() {
    final baseUrl = AppEnv.dlBaseUrl;
    if (baseUrl.startsWith('http://')) {
      return baseUrl.replaceFirst('http://', 'ws://') + '/ws';
    } else if (baseUrl.startsWith('https://')) {
      return baseUrl.replaceFirst('https://', 'wss://') + '/ws';
    } else {
      return 'ws://$baseUrl/ws';
    }
  }

  // API URL 생성
  String _getApiUrl() {
    return AppEnv.dlBaseUrl;
  }

  // 리소스 정리
  void dispose() {
    disconnect();
    _notificationController.close();
    _connectionController.close();
  }
}
