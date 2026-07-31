import 'package:flutter_test/flutter_test.dart';
import 'package:oops/main.dart';

void main() {
  testWidgets('HireMeApp widget test', (WidgetTester tester) async {
    await tester.pumpWidget(const HireMeApp());
    await tester.pumpAndSettle();
  });
}
