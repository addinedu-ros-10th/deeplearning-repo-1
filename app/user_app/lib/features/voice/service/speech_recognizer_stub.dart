import 'dart:async';
import 'speech_recognizer.dart';

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


