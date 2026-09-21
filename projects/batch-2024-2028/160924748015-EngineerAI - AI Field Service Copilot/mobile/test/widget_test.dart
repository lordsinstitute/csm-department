import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/main.dart';

void main() {
  testWidgets('App builds and shows the splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: EngineerAIApp()));
    await tester.pumpAndSettle();

    expect(find.text('EngineerAI'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
  });
}
