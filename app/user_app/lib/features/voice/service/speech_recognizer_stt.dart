import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'speech_recognizer.dart';

class SttSpeechRecognizer implements SpeechRecognizer {
  SttSpeechRecognizer() {
    _levelController = StreamController<double>.broadcast();
    _transcriptController = StreamController<String>.broadcast();
  }

  final stt.SpeechToText _stt = stt.SpeechToText();
  late final StreamController<double> _levelController;
  late final StreamController<String> _transcriptController;

  @override
  Stream<double> get levelStream => _levelController.stream;

  @override
  Stream<String> get transcriptStream => _transcriptController.stream;

  @override
  Future<void> start() async {
    final bool available = await _stt.initialize(onStatus: (String status) {
      if (status == 'notListening') {
        _levelController.add(0.0);
      }
    }, onError: (dynamic e) {
      _levelController.add(0.0);
    });
    if (!available) return;

    await _stt.listen(
      localeId: 'ko_KR',
      onResult: (dynamic result) {
        try {
          final String text = result.recognizedWords as String;
          if (text.isNotEmpty) _transcriptController.add(text);
        } catch (_) {}
      },
      // Use deprecated fields for broader compatibility across platforms
      listenMode: stt.ListenMode.dictation,
      partialResults: true,
      onSoundLevelChange: (double level) {
        final double normalized = (level / 30.0).clamp(0.0, 1.0);
        _levelController.add(normalized);
      },
    );
  }

  @override
  Future<void> stop() async {
    try {
      await _stt.stop();
    } catch (_) {}
    _levelController.add(0.0);
  }
}


