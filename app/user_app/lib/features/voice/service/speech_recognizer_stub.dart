import 'dart:async';

abstract class SpeechRecognizer {
  Stream<double> get levelStream;
  Stream<String> get transcriptStream;
  Future<void> start();
  Future<void> stop();
}

class StubSpeechRecognizer implements SpeechRecognizer {
  @override
  Stream<double> get levelStream => const Stream<double>.empty();

  @override
  Stream<String> get transcriptStream => const Stream<String>.empty();

  @override
  Future<void> start() async {}

  @override
  Future<void> stop() async {}
}


