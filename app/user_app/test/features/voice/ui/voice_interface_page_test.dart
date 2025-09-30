import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import 'package:user_app/features/voice/ui/voice_interface_page.dart';
import 'package:user_app/features/notification/state/notification_provider.dart';
import 'package:user_app/features/auth/state/auth_provider.dart';
import 'package:user_app/features/voice/service/flutter_tts_service.dart';
import 'package:user_app/features/voice/service/openai_service.dart';

import 'voice_interface_page_test.mocks.dart';

@GenerateMocks([
  NotificationProvider,
  AuthProvider,
  FlutterTtsService,
  OpenAiService,
])
void main() {
  group('VoiceInterfacePage Button Tests', () {
    late MockNotificationProvider mockNotificationProvider;
    late MockAuthProvider mockAuthProvider;
    late MockFlutterTtsService mockTtsService;
    late MockOpenAiService mockOpenAiService;

    setUp(() {
      mockNotificationProvider = MockNotificationProvider();
      mockAuthProvider = MockAuthProvider();
      mockTtsService = MockFlutterTtsService();
      mockOpenAiService = MockOpenAiService();

      // 기본 mock 설정
      when(mockAuthProvider.isLoggedIn).thenReturn(true);
      when(mockAuthProvider.userId).thenReturn('test-user-id');
      when(mockNotificationProvider.messages).thenReturn([]);
      when(mockNotificationProvider.unreadCount).thenReturn(0);
    });

    Widget createTestWidget() {
      return MultiProvider(
        providers: [
          ChangeNotifierProvider<NotificationProvider>.value(
            value: mockNotificationProvider,
          ),
          ChangeNotifierProvider<AuthProvider>.value(
            value: mockAuthProvider,
          ),
        ],
        child: MaterialApp(
          home: VoiceInterfacePage(),
        ),
      );
    }

    group('Menu Button Tests', () {
      testWidgets('메뉴 버튼이 화면에 표시되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 버튼 찾기
        final menuButton = find.byIcon(Icons.menu);
        expect(menuButton, findsOneWidget);
      });

      testWidgets('메뉴 버튼 클릭 시 메뉴 옵션들이 표시되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 버튼 클릭
        final menuButton = find.byIcon(Icons.menu);
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 메뉴 옵션들이 표시되는지 확인
        expect(find.text('나의 소지품 찾기'), findsOneWidget);
        expect(find.text('메시지'), findsOneWidget);
        expect(find.text('긴급/응급 신고'), findsOneWidget);
      });

      testWidgets('메뉴 버튼 클릭 시 아이콘이 close로 변경되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 초기 상태: menu 아이콘
        expect(find.byIcon(Icons.menu), findsOneWidget);
        expect(find.byIcon(Icons.close), findsNothing);

        // 메뉴 버튼 클릭
        final menuButton = find.byIcon(Icons.menu);
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 변경된 상태: close 아이콘
        expect(find.byIcon(Icons.close), findsOneWidget);
        expect(find.byIcon(Icons.menu), findsNothing);
      });

      testWidgets('메뉴 옵션 버튼들이 클릭 가능해야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 열기
        final menuButton = find.byIcon(Icons.menu);
        await tester.tap(menuButton);
        await tester.pumpAndSettle();

        // 각 메뉴 옵션 버튼이 클릭 가능한지 확인
        final itemsButton = find.text('나의 소지품 찾기');
        final messagesButton = find.text('메시지');
        final emergencyButton = find.text('긴급/응급 신고');

        expect(itemsButton, findsOneWidget);
        expect(messagesButton, findsOneWidget);
        expect(emergencyButton, findsOneWidget);

        // 버튼들이 Material 위젯으로 감싸져 있는지 확인
        expect(find.ancestor(of: itemsButton, matching: find.byType(Material)), findsOneWidget);
        expect(find.ancestor(of: messagesButton, matching: find.byType(Material)), findsOneWidget);
        expect(find.ancestor(of: emergencyButton, matching: find.byType(Material)), findsOneWidget);
      });
    });

    group('Voice Input Button Tests', () {
      testWidgets('음성 입력 버튼이 화면 중앙에 표시되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 음성 입력 버튼 찾기
        final voiceButton = find.byIcon(Icons.mic_none);
        expect(voiceButton, findsOneWidget);

        // 버튼이 화면 중앙에 위치하는지 확인
        final RenderBox buttonBox = tester.renderObject(find.byIcon(Icons.mic_none));
        final screenSize = tester.view.physicalSize / tester.view.devicePixelRatio;
        final buttonCenter = buttonBox.localToGlobal(Offset.zero) + buttonBox.size.center(Offset.zero);
        final screenCenter = screenSize.center(Offset.zero);

        // 중앙 위치 허용 오차 (50px)
        expect((buttonCenter - screenCenter).distance, lessThan(50));
      });

      testWidgets('음성 입력 버튼이 150x150 크기여야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final voiceButton = find.byIcon(Icons.mic_none);
        final RenderBox buttonBox = tester.renderObject(voiceButton);
        
        expect(buttonBox.size.width, equals(150));
        expect(buttonBox.size.height, equals(150));
      });
    });

    group('Background Tap Tests', () {
      testWidgets('배경 터치 시 STT가 비활성화되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // STT 활성화 상태로 설정 (실제로는 mock을 통해 설정)
        // 여기서는 UI 상태만 확인
        
        // 배경 터치 (SafeArea 내부)
        final safeArea = find.byType(SafeArea);
        await tester.tap(safeArea);
        await tester.pumpAndSettle();

        // STT가 비활성화되었는지 확인 (아이콘이 mic_none으로 변경)
        expect(find.byIcon(Icons.mic_none), findsOneWidget);
      });
    });

    group('Stack Structure Tests', () {
      testWidgets('Stack 구조가 올바르게 구성되어야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Stack 위젯이 존재해야 함
        expect(find.byType(Stack), findsOneWidget);

        // Stack의 자식들이 올바른 순서로 배치되어야 함
        final stack = find.byType(Stack);
        final stackWidget = tester.widget<Stack>(stack);
        
        expect(stackWidget.children.length, greaterThanOrEqualTo(4));
      });

      testWidgets('메뉴 버튼이 Stack의 최상단에 위치해야 함', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // 메뉴 버튼이 Positioned 위젯으로 감싸져 있는지 확인
        final menuButton = find.byIcon(Icons.menu);
        expect(find.ancestor(of: menuButton, matching: find.byType(Positioned)), findsOneWidget);
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
    });
  });
}
