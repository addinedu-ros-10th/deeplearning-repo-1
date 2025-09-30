import 'package:flutter/material.dart';
import 'package:user_app/features/notification/models/emergency_notification.dart';
import 'package:user_app/features/notification/ui/emergency_alert_dialog.dart';

/// 긴급 알림 서비스
class EmergencyNotificationService {
  static final EmergencyNotificationService _instance = EmergencyNotificationService._internal();
  factory EmergencyNotificationService() => _instance;
  EmergencyNotificationService._internal();

  /// 긴급 알림 표시
  static Future<void> showEmergencyAlert(
    BuildContext context,
    EmergencyNotification notification,
  ) async {
    print('=== showEmergencyAlert 호출됨 ===');
    print('notification.kind: ${notification.kind}');
    print('notification.severity: ${notification.severity}');
    print('notification.isEmergencyLevel5: ${notification.isEmergencyLevel5}');
    print('context: $context');
    print('context.mounted: ${context.mounted}');
    
    if (!notification.isEmergencyLevel5) {
      print('긴급 알림이 아닙니다: ${notification.kind}, ${notification.severity}');
      return;
    }

    // BuildContext 유효성 검사
    if (!context.mounted) {
      print('BuildContext가 유효하지 않습니다. 긴급 알림 표시를 건너뜁니다.');
      return;
    }

    print('긴급 알림 표시 시작: ${notification.title}');

    try {
      // 현재 context가 유효한지 다시 한번 확인
      if (!context.mounted) {
        print('showDialog 호출 전 context 유효성 재검사 실패');
        return;
      }

      await showEmergencyAlertDialog(
        context,
        title: notification.title,
        message: notification.message,
        onConfirm: () {
          print('사용자 의식 있음 확인됨');
          _sendUserConsciousnessConfirmation(notification);
        },
        onCancel: () {
          print('긴급 알림 취소됨');
          _sendUserConsciousnessCancellation(notification);
        },
      );
      print('긴급 알림 다이얼로그 표시 완료');
    } catch (e) {
      print('긴급 알림 다이얼로그 표시 오류: $e');
      print('오류 타입: ${e.runtimeType}');
      
      // context가 유효하지 않은 경우, 새로운 context를 찾아서 시도
      if (e.toString().contains('BuildContext is no longer valid')) {
        print('BuildContext가 유효하지 않음. 긴급 알림을 대기열에 추가합니다.');
        // TODO: 긴급 알림을 대기열에 추가하여 나중에 표시
      }
    }
  }

  /// 사용자 의식 있음 확인 피드백 전송
  static Future<void> _sendUserConsciousnessConfirmation(
    EmergencyNotification notification,
  ) async {
    try {
      // TODO: 실제 서버 API 호출
      print('서버에 사용자 의식 있음 확인 전송: ${notification.id}');
      
      // 임시로 로컬에 저장
      await _saveUserResponse(notification.id, 'consciousness_confirmed');
      
    } catch (e) {
      print('사용자 의식 확인 전송 오류: $e');
    }
  }

  /// 사용자 의식 확인 취소 피드백 전송
  static Future<void> _sendUserConsciousnessCancellation(
    EmergencyNotification notification,
  ) async {
    try {
      // TODO: 실제 서버 API 호출
      print('서버에 사용자 의식 확인 취소 전송: ${notification.id}');
      
      // 임시로 로컬에 저장
      await _saveUserResponse(notification.id, 'consciousness_cancelled');
      
    } catch (e) {
      print('사용자 의식 확인 취소 전송 오류: $e');
    }
  }

  /// 사용자 응답 로컬 저장 (임시)
  static Future<void> _saveUserResponse(String notificationId, String response) async {
    // TODO: SharedPreferences 또는 로컬 데이터베이스에 저장
    print('사용자 응답 저장: $notificationId -> $response');
  }

  /// 알림 우선순위에 따라 정렬
  static List<EmergencyNotification> sortByPriority(
    List<EmergencyNotification> notifications,
  ) {
    notifications.sort((a, b) => b.priority.compareTo(a.priority));
    return notifications;
  }

  /// 위기 단계별 알림 필터링
  static List<EmergencyNotification> filterByEmergencyLevel(
    List<EmergencyNotification> notifications,
    int level,
  ) {
    switch (level) {
      case 5:
        return notifications.where((n) => n.isEmergencyLevel5).toList();
      case 4:
        return notifications.where((n) => n.kind == 'system' && n.severity == 'orange').toList();
      case 3:
        return notifications.where((n) => n.kind == 'system' && n.severity == 'yellow').toList();
      case 2:
        return notifications.where((n) => n.kind == 'system' && n.severity == 'blue').toList();
      case 1:
        return notifications.where((n) => n.kind == 'system' && n.severity == 'green').toList();
      default:
        return notifications;
    }
  }

  /// 긴급 알림 생성 (테스트용)
  static EmergencyNotification createTestEmergencyNotification({
    String? title,
    String? message,
  }) {
    print('=== 테스트 긴급 알림 생성 시작 ===');
    
    final notification = EmergencyNotification(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      kind: 'system',
      severity: 'red',
      title: title ?? '긴급 상황 발생',
      message: message ?? '낙상 등 심각한 상황이 감지되었습니다. 즉시 응답해주세요.',
      timestamp: DateTime.now(),
      metadata: {
        'type': 'fall_detection',
        'location': 'living_room',
        'confidence': 0.95,
        'test': true, // 테스트 알림임을 표시
      },
    );
    
    print('테스트 긴급 알림 생성 완료:');
    print('  id: ${notification.id}');
    print('  kind: ${notification.kind}');
    print('  severity: ${notification.severity}');
    print('  title: ${notification.title}');
    print('  message: ${notification.message}');
    print('  isEmergency: ${notification.isEmergency}');
    print('  isEmergencyLevel5: ${notification.isEmergencyLevel5}');
    print('  alertColor: ${notification.alertColor}');
    print('  priority: ${notification.priority}');
    print('================================');
    
    return notification;
  }
}
