// dart:html is only available on web
import 'dart:async';
import 'dart:html' as html;

abstract class SpeechRecognizer {
  Stream<double> get levelStream;
  Future<void> start();
  Future<void> stop();
}

class WebSpeechRecognizer implements SpeechRecognizer {
  WebSpeechRecognizer() {
    _controller = StreamController<double>.broadcast();
  }

  late final StreamController<double> _controller;
  html.SpeechRecognition? _rec;

  @override
  Stream<double> get levelStream => _controller.stream;

  @override
  Future<void> start() async {
    // Web Speech API
    final dynamic speechCtor = (html.window as dynamic).SpeechRecognition ?? (html.window as dynamic).webkitSpeechRecognition;
    if (speechCtor == null) {
      return; // unsupported
    }
    _rec = speechCtor();
    _rec!.lang = 'ko-KR';
    _rec!.continuous = true;
    _rec!.interimResults = true;

    _rec!.onresult.listen((html.SpeechRecognitionEvent e) {
      // No actual audio level from API; emit pseudo level during recognition
      _controller.add(0.6);
    });
    _rec!.onstart.listen((_) => _controller.add(0.5));
    _rec!.onnomatch.listen((_) => _controller.add(0.2));
    _rec!.onend.listen((_) => _controller.add(0.0));
    _rec!.onerror.listen((_) => _controller.add(0.0));

    _rec!.start();
  }

  @override
  Future<void> stop() async {
    try {
      await _rec?.stop();
    } catch (_) {}
    _controller.add(0.0);
  }
}


