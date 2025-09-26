import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart' as stt;

abstract class SpeechRecognizer {
  Stream<double> get levelStream;
  Stream<String> get transcriptStream;
  Future<void> start();
  Future<void> stop();
}

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
    }, onError: (stt.SpeechRecognitionError e) {
      _levelController.add(0.0);
    });
    if (!available) return;

    await _stt.listen(
      localeId: 'ko_KR',
      onResult: (stt.SpeechRecognitionResult result) {
        final String text = result.recognizedWords;
        if (text.isNotEmpty) _transcriptController.add(text);
      },
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


