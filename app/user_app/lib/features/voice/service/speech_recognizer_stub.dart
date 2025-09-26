import 'dart:async';

abstract class SpeechRecognizer {
  Stream<double> get levelStream;
  Future<void> start();
  Future<void> stop();
}

class StubSpeechRecognizer implements SpeechRecognizer {
  @override
  Stream<double> get levelStream => const Stream<double>.empty();

  @override
  Future<void> start() async {}

  @override
  Future<void> stop() async {}
}


