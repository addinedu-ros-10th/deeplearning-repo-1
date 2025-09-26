import 'speech_recognizer_stt.dart';

abstract class SpeechRecognizer {
  Stream<double> get levelStream;
  Stream<String> get transcriptStream;
  Future<void> start();
  Future<void> stop();
}

SpeechRecognizer createSpeechRecognizer() => SttSpeechRecognizer();


