import 'package:valley_consumer/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('aplicativo expõe a raiz Valley', () {
    const app = ValleyApp();

    expect(app, isA<ValleyApp>());
  });
}
