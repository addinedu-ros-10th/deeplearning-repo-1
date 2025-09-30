import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:user_app/features/voice/ui/voice_interface_page.dart';
import 'package:user_app/features/notification/state/notification_provider.dart';
import 'package:user_app/features/auth/state/auth_provider.dart';

void main() {
  group('VoiceInterfacePage Integration Tests', () {
    late NotificationProvider notificationProvider;
    late AuthProvider authProvider;

    setUp(() {
      notificationProvider = NotificationProvider();
      authProvider = AuthProvider();
    });

    Widget createTestWidget() {
      return MultiProvider(
        providers: [
          ChangeNotifierProvider<NotificationProvider>.value(
            value: notificationProvider,
          ),
          ChangeNotifierProvider<AuthProvider>.value(
            value: authProvider,
          ),
        ],
        child: MaterialApp(
          home: VoiceInterfacePage(),
        ),
      );
    }

    group('Button Click Tests', () {
      testWidgets('메뉴 버튼 클릭 시 메뉴 옵션들이 표시되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 버튼 찾기
        final menuButton = find.byIcon(Icons.menu);
        expect(menuButton, findsOneWidget);

        // 메뉴 버튼 클릭
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 메뉴 옵션들이 표시되는지 확인
        expect(find.text('나의 소지품 찾기'), findsOneWidget);
        expect(find.text('메시지'), findsOneWidget);
        expect(find.text('긴급/응급 신고'), findsOneWidget);
      });

      testWidgets('메뉴 옵션 버튼 클릭 시 메뉴가 닫혀야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 열기
        final menuButton = find.byIcon(Icons.menu);
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 메뉴 옵션 버튼 클릭
        final itemsButton = find.text('나의 소지품 찾기');
        await tester.tap(itemsButton);
        await tester.pumpAndSettle();

        // 메뉴가 닫혔는지 확인
        expect(find.text('나의 소지품 찾기'), findsNothing);
        expect(find.byIcon(Icons.menu), findsOneWidget);
      });

      testWidgets('음성 입력 버튼이 화면에 표시되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 음성 입력 버튼 찾기
        final voiceButton = find.byIcon(Icons.mic_none);
        expect(voiceButton, findsOneWidget);
      });
    });

    group('UI Structure Tests', () {
      testWidgets('Stack 구조가 올바르게 구성되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Stack 위젯이 존재해야 함
        expect(find.byType(Stack), findsOneWidget);

        // 메뉴 버튼이 Positioned 위젯으로 감싸져 있어야 함
        final menuButton = find.byIcon(Icons.menu);
        expect(find.ancestor(of: menuButton, matching: find.byType(Positioned)), findsOneWidget);
      });

      testWidgets('메뉴 버튼이 Material과 InkWell로 감싸져 있어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final menuButton = find.byIcon(Icons.menu);
        
        // Material 위젯으로 감싸져 있는지 확인
        expect(find.ancestor(of: menuButton, matching: find.byType(Material)), findsOneWidget);
        
        // InkWell 위젯으로 감싸져 있는지 확인
        expect(find.ancestor(of: menuButton, matching: find.byType(InkWell)), findsOneWidget);
      });
    });

    group('Touch Event Tests', () {
      testWidgets('모든 버튼이 터치 이벤트를 받을 수 있어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 버튼 터치 테스트
        final menuButton = find.byIcon(Icons.menu);
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 메뉴가 열렸는지 확인
        expect(find.text('나의 소지품 찾기'), findsOneWidget);

        // 메뉴 옵션 버튼 터치 테스트
        final itemsButton = find.text('나의 소지품 찾기');
        await tester.tap(itemsButton);
        await tester.pumpAndSettle();

        // 메뉴가 닫혔는지 확인
        expect(find.text('나의 소지품 찾기'), findsNothing);
      });

      testWidgets('메뉴 옵션 버튼들이 Material과 InkWell로 감싸져 있어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 열기
        final menuButton = find.byIcon(Icons.menu);
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 각 메뉴 옵션 버튼이 Material과 InkWell로 감싸져 있는지 확인
        final itemsButton = find.text('나의 소지품 찾기');
        final messagesButton = find.text('메시지');
        final emergencyButton = find.text('긴급/응급 신고');

        expect(find.ancestor(of: itemsButton, matching: find.byType(Material)), findsOneWidget);
        expect(find.ancestor(of: itemsButton, matching: find.byType(InkWell)), findsOneWidget);
        
        expect(find.ancestor(of: messagesButton, matching: find.byType(Material)), findsOneWidget);
        expect(find.ancestor(of: messagesButton, matching: find.byType(InkWell)), findsOneWidget);
        
        expect(find.ancestor(of: emergencyButton, matching: find.byType(Material)), findsOneWidget);
        expect(find.ancestor(of: emergencyButton, matching: find.byType(InkWell)), findsOneWidget);
      });
    });
  });
}
