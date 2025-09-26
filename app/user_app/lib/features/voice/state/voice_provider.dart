import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../service/openai_service.dart';
import '../service/speech_recognizer.dart';

class VoiceProvider extends ChangeNotifier {
  VoiceProvider() {
    _initTts();
  }

  final FlutterTts _tts = FlutterTts();
  bool _isListening = false;
  bool _isSpeaking = false;
  double _volumeLevel = 0.0; // 0.0 - 1.0 for waveform
  String _transcript = '';
  String _responseText = '';
  final OpenAiService _ai = OpenAiService();

  StreamSubscription<double>? _levelSub;
  final SpeechRecognizer _recognizer = _createRecognizer();

  bool get isListening => _isListening;
  bool get isSpeaking => _isSpeaking;
  double get volumeLevel => _volumeLevel;
  String get transcript => _transcript;
  String get responseText => _responseText;

  Future<void> _initTts() async {
    await _tts.setSpeechRate(0.95);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
  }

  Future<void> startListening() async {
    if (_isListening) return;
    _isListening = true;
    notifyListeners();

    await _recognizer.start();
    _levelSub?.cancel();
    _levelSub = _recognizer.levelStream.listen((double level) {
      _volumeLevel = level.clamp(0.0, 1.0);
      notifyListeners();
    });
  }

  Future<void> stopListening() async {
    if (!_isListening) return;
    _isListening = false;
    await _recognizer.stop();
    await _levelSub?.cancel();
    _levelSub = null;
    _volumeLevel = 0.0;
    notifyListeners();

    // For now, echo transcript placeholder and response
    if (_transcript.isEmpty) {
      _transcript = '...';
    }
  }

  void setTranscript(String text) {
    _transcript = text;
    notifyListeners();
  }

  void setResponse(String text) {
    _responseText = text;
    notifyListeners();
  }

  Future<void> speak(String text) async {
    if (text.isEmpty) return;
    _isSpeaking = true;
    notifyListeners();
    await _tts.speak(text);
    _isSpeaking = false;
    notifyListeners();
  }

  Future<void> sendToAssistant() async {
    final String prompt = _transcript.isEmpty ? '안녕하세요, 테스트 요청입니다.' : _transcript;
    final String reply = await _ai.chat(prompt);
    setResponse(reply);
    await speak(reply);
  }
}

SpeechRecognizer _createRecognizer() {
  try {
    // On web, this returns WebSpeechRecognizer due to conditional export
    // On non-web, StubSpeechRecognizer
    // ignore: prefer_const_constructors
    return (WebSpeechRecognizer as dynamic?) != null ? WebSpeechRecognizer() as SpeechRecognizer : StubSpeechRecognizer();
  } catch (_) {
    return StubSpeechRecognizer();
  }
}


