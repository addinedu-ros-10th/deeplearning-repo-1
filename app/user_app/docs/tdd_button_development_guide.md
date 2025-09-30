# TDD 기반 버튼 클릭 문제 해결 가이드

## 🎯 목표
같은 버튼 클릭 문제가 반복되지 않도록 TDD(Test-Driven Development) 방식으로 개발하는 가이드

## 📋 TDD 개발 프로세스

### 1단계: 실패하는 테스트 작성 (Red)
```dart
testWidgets('메뉴 버튼 클릭 시 상태가 변경되어야 함', (WidgetTester tester) async {
  // 테스트 시나리오 작성
  // 초기 상태 확인
  // 액션 수행
  // 결과 검증
});
```

### 2단계: 테스트를 통과하는 최소한의 코드 작성 (Green)
```dart
// 최소한의 기능만 구현
// 테스트가 통과하도록 하는 코드
```

### 3단계: 코드 리팩토링 (Refactor)
```dart
// 코드 품질 개선
// 중복 제거
// 가독성 향상
```

## 🔧 버튼 클릭 문제 해결 체크리스트

### ✅ Stack 구조 검증
- [ ] `GestureDetector`가 전체 `body`를 감싸지 않는지 확인
- [ ] `Stack` 내부에서 터치 이벤트 충돌이 없는지 확인
- [ ] `Positioned` 위젯들이 올바른 순서로 배치되었는지 확인

### ✅ 터치 이벤트 처리 검증
- [ ] `Material` + `InkWell` 조합 사용
- [ ] `GestureDetector` 대신 `InkWell` 사용
- [ ] 터치 피드백 효과 적용

### ✅ 상태 관리 검증
- [ ] 버튼 상태 변경이 올바르게 작동하는지 확인
- [ ] UI 업데이트가 정상적으로 이루어지는지 확인
- [ ] 메모리 누수 방지

## 🧪 테스트 작성 패턴

### 기본 버튼 테스트
```dart
testWidgets('버튼 클릭 시 상태가 변경되어야 함', (WidgetTester tester) async {
  // Given: 초기 상태 설정
  bool isPressed = false;
  
  // When: 버튼 클릭
  await tester.tap(find.byIcon(Icons.menu));
  await tester.pumpAndSettle();
  
  // Then: 상태 변경 확인
  expect(isPressed, isTrue);
});
```

### UI 구조 테스트
```dart
testWidgets('버튼이 올바른 위젯으로 감싸져 있어야 함', (WidgetTester tester) async {
  // Given: 위젯 렌더링
  await tester.pumpWidget(testWidget);
  
  // When: 버튼 찾기
  final button = find.byIcon(Icons.menu);
  
  // Then: 구조 검증
  expect(find.ancestor(of: button, matching: find.byType(Material)), findsAtLeastNWidgets(1));
  expect(find.ancestor(of: button, matching: find.byType(InkWell)), findsOneWidget);
});
```

### 터치 이벤트 테스트
```dart
testWidgets('Stack 구조에서 터치 이벤트가 올바르게 작동해야 함', (WidgetTester tester) async {
  // Given: 상태 변수 설정
  bool backgroundTapped = false;
  bool buttonTapped = false;
  
  // When: 버튼 클릭
  await tester.tap(find.byIcon(Icons.menu));
  
  // Then: 올바른 이벤트 발생 확인
  expect(buttonTapped, isTrue);
  expect(backgroundTapped, isFalse);
});
```

## 🚨 주의사항

### 1. GestureDetector 사용 시 주의점
- 전체 `body`를 감싸면 하위 위젯의 터치 이벤트를 차단할 수 있음
- `Stack` 내부에서 사용할 때는 위치를 신중히 고려

### 2. Material + InkWell 조합
- 터치 피드백 효과를 위해 `Material`과 `InkWell`을 함께 사용
- `color: Colors.transparent`로 설정하여 배경색 영향 방지

### 3. 테스트 작성 시
- 실제 의존성을 Mock으로 대체하여 테스트 안정성 확보
- `pumpAndSettle()` 사용 시 타임아웃 주의
- 위젯 트리 구조를 정확히 파악하여 테스트 작성

## 📊 테스트 커버리지 목표

- [ ] 버튼 클릭 이벤트: 100%
- [ ] UI 구조 검증: 100%
- [ ] 상태 변경 로직: 100%
- [ ] 터치 이벤트 처리: 100%

## 🔄 지속적 개선

1. **테스트 실행**: 모든 변경 후 테스트 실행
2. **리팩토링**: 테스트 통과 후 코드 품질 개선
3. **문서화**: 변경사항을 가이드에 반영
4. **검토**: 팀원과 코드 리뷰 진행

이 가이드를 따라 개발하면 버튼 클릭 문제가 반복되지 않고, 안정적인 UI를 구축할 수 있습니다.
