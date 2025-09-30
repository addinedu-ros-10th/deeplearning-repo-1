import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:user_app/features/notification/models/emergency_notification.dart';
import 'package:user_app/features/notification/services/emergency_notification_service.dart';

void main() {
  group('EmergencyNotification TDD Tests', () {
    test('EmergencyNotification 모델 테스트 - 위기 5단계', () {
      final notification = EmergencyNotification(
        id: 'test_123',
        kind: 'system',
        severity: 'red',
        title: '긴급 상황 발생',
        message: '낙상 등 심각한 상황이 감지되었습니다.',
        timestamp: DateTime.now(),
      );

      print('=== EmergencyNotification 모델 테스트 ===');
      print('kind: ${notification.kind}');
      print('severity: ${notification.severity}');
      print('isEmergency: ${notification.isEmergency}');
      print('isEmergencyLevel5: ${notification.isEmergencyLevel5}');
      print('alertColor: ${notification.alertColor}');
      print('priority: ${notification.priority}');

      expect(notification.kind, equals('system'));
      expect(notification.severity, equals('red'));
      expect(notification.isEmergency, isTrue);
      expect(notification.isEmergencyLevel5, isTrue);
      expect(notification.alertColor, equals(Colors.red[600]));
      expect(notification.priority, equals(5));
    });

    test('EmergencyNotification 모델 테스트 - 일반 알림', () {
      final notification = EmergencyNotification(
        id: 'test_456',
        kind: 'info',
        severity: 'blue',
        title: '일반 알림',
        message: '일반적인 정보 알림입니다.',
        timestamp: DateTime.now(),
      );

      print('=== 일반 알림 테스트 ===');
      print('kind: ${notification.kind}');
      print('severity: ${notification.severity}');
      print('isEmergency: ${notification.isEmergency}');
      print('isEmergencyLevel5: ${notification.isEmergencyLevel5}');

      expect(notification.kind, equals('info'));
      expect(notification.severity, equals('blue'));
      expect(notification.isEmergency, isFalse);
      expect(notification.isEmergencyLevel5, isFalse);
    });

    test('EmergencyNotificationService.createTestEmergencyNotification 테스트', () {
      final testNotification = EmergencyNotificationService.createTestEmergencyNotification();
      
      print('=== 테스트 긴급 알림 생성 테스트 ===');
      print('kind: ${testNotification.kind}');
      print('severity: ${testNotification.severity}');
      print('isEmergency: ${testNotification.isEmergency}');
      print('isEmergencyLevel5: ${testNotification.isEmergencyLevel5}');
      print('title: ${testNotification.title}');
      print('message: ${testNotification.message}');

      expect(testNotification.kind, equals('system'));
      expect(testNotification.severity, equals('red'));
      expect(testNotification.isEmergency, isTrue);
      expect(testNotification.isEmergencyLevel5, isTrue);
      expect(testNotification.title, contains('긴급'));
      expect(testNotification.message, contains('낙상'));
    });

    test('위기 5단계 조건 확인 테스트', () {
      // 위기 5단계 조건: kind='system' AND severity='red'
      final testCases = [
        {'kind': 'system', 'severity': 'red', 'expected': true},
        {'kind': 'system', 'severity': 'orange', 'expected': false},
        {'kind': 'system', 'severity': 'yellow', 'expected': false},
        {'kind': 'info', 'severity': 'red', 'expected': false},
        {'kind': 'schedule', 'severity': 'red', 'expected': false},
      ];

      for (var testCase in testCases) {
        final notification = EmergencyNotification(
          id: 'test_${testCase['kind']}_${testCase['severity']}',
          kind: testCase['kind'] as String,
          severity: testCase['severity'] as String,
          title: 'Test',
          message: 'Test message',
          timestamp: DateTime.now(),
        );

        final result = notification.isEmergencyLevel5;
        final expected = testCase['expected'] as bool;
        
        print('kind=${testCase['kind']}, severity=${testCase['severity']} -> isEmergencyLevel5=$result (expected: $expected)');
        expect(result, equals(expected));
      }
    });
  });
}
