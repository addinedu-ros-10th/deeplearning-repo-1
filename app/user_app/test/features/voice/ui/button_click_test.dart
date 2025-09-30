import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Button Click Tests', () {
    testWidgets('메뉴 버튼 클릭 시 상태가 변경되어야 함', (WidgetTester tester) async {
      bool showMenu = false;
      
      Widget testWidget = MaterialApp(
        home: Scaffold(
          body: Stack(
            children: [
              // 메뉴 버튼
              Positioned(
                bottom: 30,
                right: 30,
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () {
                      showMenu = !showMenu;
                    },
                    borderRadius: BorderRadius.circular(30),
                    child: Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: showMenu ? Colors.red[600] : Colors.blue[600],
                      ),
                      child: Icon(
                        showMenu ? Icons.close : Icons.menu,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                  ),
                ),
              ),
              
              // 메뉴 옵션들
              if (showMenu)
                Positioned(
                  bottom: 120,
                  right: 30,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _buildMenuOptionButton('나의 소지품 찾기', Icons.search, () {}),
                      const SizedBox(height: 8),
                      _buildMenuOptionButton('메시지', Icons.message, () {}),
                      const SizedBox(height: 8),
                      _buildMenuOptionButton('긴급/응급 신고', Icons.emergency, () {}),
                    ],
                  ),
                ),
            ],
          ),
        ),
      );

      await tester.pumpWidget(testWidget);
      await tester.pumpAndSettle();

      // 초기 상태: 메뉴가 닫혀있음
      expect(find.byIcon(Icons.menu), findsOneWidget);
      expect(find.byIcon(Icons.close), findsNothing);
      expect(find.text('나의 소지품 찾기'), findsNothing);

      // 메뉴 버튼 클릭
      final menuButton = find.byIcon(Icons.menu);
      await tester.tap(menuButton);
      await tester.pumpAndSettle();

      // 상태 변경 확인
      expect(showMenu, isTrue);
    });

    testWidgets('메뉴 옵션 버튼들이 Material과 InkWell로 감싸져 있어야 함', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              children: [
                _buildMenuOptionButton('나의 소지품 찾기', Icons.search, () {}),
                const SizedBox(height: 8),
                _buildMenuOptionButton('메시지', Icons.message, () {}),
                const SizedBox(height: 8),
                _buildMenuOptionButton('긴급/응급 신고', Icons.emergency, () {}),
              ],
            ),
          ),
        ),
      ));

      await tester.pumpAndSettle();

      // 각 버튼이 Material과 InkWell로 감싸져 있는지 확인
      final itemsButton = find.text('나의 소지품 찾기');
      final messagesButton = find.text('메시지');
      final emergencyButton = find.text('긴급/응급 신고');

      expect(find.ancestor(of: itemsButton, matching: find.byType(Material)), findsAtLeastNWidgets(1));
      expect(find.ancestor(of: itemsButton, matching: find.byType(InkWell)), findsOneWidget);
      
      expect(find.ancestor(of: messagesButton, matching: find.byType(Material)), findsAtLeastNWidgets(1));
      expect(find.ancestor(of: messagesButton, matching: find.byType(InkWell)), findsOneWidget);
      
      expect(find.ancestor(of: emergencyButton, matching: find.byType(Material)), findsAtLeastNWidgets(1));
      expect(find.ancestor(of: emergencyButton, matching: find.byType(InkWell)), findsOneWidget);
    });

    testWidgets('Stack 구조에서 터치 이벤트가 올바르게 작동해야 함', (WidgetTester tester) async {
      bool backgroundTapped = false;
      bool buttonTapped = false;

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: Stack(
            children: [
              // 배경
              GestureDetector(
                onTap: () {
                  backgroundTapped = true;
                },
                child: Container(
                  width: double.infinity,
                  height: double.infinity,
                  color: Colors.grey[100],
                ),
              ),
              
              // 버튼
              Positioned(
                bottom: 30,
                right: 30,
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () {
                      buttonTapped = true;
                    },
                    borderRadius: BorderRadius.circular(30),
                    child: Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.blue[600],
                      ),
                      child: const Icon(
                        Icons.menu,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ));

      await tester.pumpAndSettle();

      // 버튼 클릭
      final button = find.byIcon(Icons.menu);
      await tester.tap(button);
      await tester.pumpAndSettle();

      // 버튼만 클릭되고 배경은 클릭되지 않았는지 확인
      expect(buttonTapped, isTrue);
      expect(backgroundTapped, isFalse);
    });
  });
}

Widget _buildMenuOptionButton(String label, IconData icon, VoidCallback onTap) {
  return Material(
    color: Colors.transparent,
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(25),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(25),
          border: Border.all(color: Colors.grey[700]!),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 12),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    ),
  );
}
