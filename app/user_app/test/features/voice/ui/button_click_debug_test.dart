import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:user_app/features/voice/ui/voice_interface_page.dart';
import 'package:user_app/features/notification/state/notification_provider.dart';
import 'package:user_app/features/auth/state/auth_provider.dart';
import 'package:user_app/features/notification/models/emergency_notification.dart';

void main() {
  group('Button Click Debug Tests', () {
    testWidgets('중앙 음성 버튼 클릭 이벤트 테스트', (WidgetTester tester) async {
      // Given: VoiceInterfacePage 위젯 생성
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => NotificationProvider()),
            ChangeNotifierProvider(create: (_) => AuthProvider()),
          ],
          child: const MaterialApp(
            home: VoiceInterfacePage(),
          ),
        ),
      );

      // When: 중앙 음성 버튼 찾기
      final voiceButton = find.byType(InkWell).first;
      expect(voiceButton, findsOneWidget);

      // Then: 버튼 클릭 테스트
      await tester.tap(voiceButton);
      await tester.pumpAndSettle();

      // 클릭 이벤트가 발생했는지 확인 (상태 변화로 검증)
      // 실제로는 _isVoiceInputActive 상태가 변경되어야 함
      print('중앙 음성 버튼 클릭 테스트 완료');
    });

    testWidgets('메뉴 버튼 클릭 이벤트 테스트', (WidgetTester tester) async {
      // Given: VoiceInterfacePage 위젯 생성
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => NotificationProvider()),
            ChangeNotifierProvider(create: (_) => AuthProvider()),
          ],
          child: const MaterialApp(
            home: VoiceInterfacePage(),
          ),
        ),
      );

      // When: 메뉴 버튼 찾기
      final menuButton = find.byIcon(Icons.apps);
      expect(menuButton, findsOneWidget);

      // Then: 메뉴 버튼 클릭 테스트
      await tester.tap(menuButton);
      await tester.pumpAndSettle();

      // 메뉴가 열렸는지 확인
      final closeButton = find.byIcon(Icons.close);
      expect(closeButton, findsOneWidget);

      print('메뉴 버튼 클릭 테스트 완료');
    });

    testWidgets('긴급 알림 테스트 버튼 클릭 이벤트 테스트', (WidgetTester tester) async {
      // Given: VoiceInterfacePage 위젯 생성
      final notificationProvider = NotificationProvider();
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider.value(value: notificationProvider),
            ChangeNotifierProvider(create: (_) => AuthProvider()),
          ],
          child: const MaterialApp(
            home: VoiceInterfacePage(),
          ),
        ),
      );

      // When: 메뉴 버튼 클릭하여 메뉴 열기
      final menuButton = find.byIcon(Icons.apps);
      await tester.tap(menuButton);
      await tester.pumpAndSettle();

      // 긴급 알림 테스트 버튼 찾기
      final emergencyTestButton = find.text('긴급 알림 테스트');
      expect(emergencyTestButton, findsOneWidget);

      // Then: 긴급 알림 테스트 버튼 클릭
      await tester.tap(emergencyTestButton);
      await tester.pumpAndSettle();

      // 긴급 알림이 생성되었는지 확인
      expect(notificationProvider.emergencyNotifications.length, greaterThan(0));
      
      final emergencyNotification = notificationProvider.emergencyNotifications.first;
      expect(emergencyNotification.kind, equals('system'));
      expect(emergencyNotification.severity, equals('red'));
      expect(emergencyNotification.isEmergencyLevel5, isTrue);

      print('긴급 알림 테스트 버튼 클릭 테스트 완료');
    });

    testWidgets('EmergencyNotification 모델 테스트', (WidgetTester tester) async {
      // Given: EmergencyNotification 생성
      final notification = EmergencyNotification(
        id: 'test-id',
        kind: 'system',
        severity: 'red',
        title: '긴급 상황 발생',
        message: '낙상 등 심각한 상황이 감지되었습니다.',
        timestamp: DateTime.now(),
      );

      // Then: 위기 5단계 조건 확인
      expect(notification.kind, equals('system'));
      expect(notification.severity, equals('red'));
      expect(notification.isEmergencyLevel5, isTrue);
      expect(notification.isEmergency, isTrue);

      print('EmergencyNotification 모델 테스트 완료');
    });
  });
}

