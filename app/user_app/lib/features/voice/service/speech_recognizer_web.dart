// dart:html is only available on web
import 'dart:async';
import 'dart:html' as html;

abstract class SpeechRecognizer {
  Stream<double> get levelStream;
  Stream<String> get transcriptStream;
  Future<void> start();
  Future<void> stop();
}

class WebSpeechRecognizer implements SpeechRecognizer {
  WebSpeechRecognizer() {
    _controller = StreamController<double>.broadcast();
  }

  late final StreamController<double> _controller;
  late final StreamController<String> _transcriptController;
  html.SpeechRecognition? _rec;

  @override
  Stream<double> get levelStream => _controller.stream;
  @override
  Stream<String> get transcriptStream => _transcriptController.stream;

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

    _transcriptController = StreamController<String>.broadcast();

    _rec!.onresult.listen((html.SpeechRecognitionEvent e) {
      // Aggregate best transcript from results
      final List<html.SpeechRecognitionResult> results = e.results;
      if (results.isEmpty) return;
      final html.SpeechRecognitionResult last = results.last;
      if (last.isFinal ?? false) {
        final String text = last.first.transcript ?? '';
        _transcriptController.add(text);
      } else {
        final String text = last.first.transcript ?? '';
        if (text.isNotEmpty) _transcriptController.add(text);
      }
      // pseudo level during recognition
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


