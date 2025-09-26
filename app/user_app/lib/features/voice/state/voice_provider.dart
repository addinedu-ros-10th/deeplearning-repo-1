import 'dart:async';
import 'package:flutter/foundation.dart';
import 'dart:math' as math;
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
  StreamSubscription<String>? _transcriptSub;
  bool _hasLevel = false;
  Timer? _waveAnimTimer;
  double _animPhase = 0.0;
  String _animMode = 'none'; // none | listen | speak

  // TTS configuration
  List<Map<String, dynamic>> _availableVoices = <Map<String, dynamic>>[];
  Map<String, dynamic>? _selectedVoice;
  double _ttsRate = 0.95;
  double _ttsPitch = 1.0;
  final SpeechRecognizer _recognizer = createSpeechRecognizer();

  bool get isListening => _isListening;
  bool get isSpeaking => _isSpeaking;
  double get volumeLevel => _volumeLevel;
  String get transcript => _transcript;
  String get responseText => _responseText;

  Future<void> _initTts() async {
    await _tts.setSpeechRate(_ttsRate);
    await _tts.setVolume(1.0);
    await _tts.setPitch(_ttsPitch);
    try {
      await _tts.awaitSpeakCompletion(true);
    } catch (_) {}
    await _loadVoices();
  }

  Future<void> startListening() async {
    if (_isListening) return;
    _isListening = true;
    notifyListeners();

    await _recognizer.start();
    _levelSub?.cancel();
    _levelSub = _recognizer.levelStream.listen((double level) {
      _volumeLevel = level.clamp(0.0, 1.0);
      _hasLevel = true;
      notifyListeners();
    });
    _transcriptSub?.cancel();
    _transcriptSub = _recognizer.transcriptStream.listen((String text) {
      _transcript = text;
      notifyListeners();
    });
    _startWaveformAnimation(mode: 'listen');
  }

  Future<void> stopListening() async {
    if (!_isListening) return;
    _isListening = false;
    await _recognizer.stop();
    await _levelSub?.cancel();
    _levelSub = null;
    await _transcriptSub?.cancel();
    _transcriptSub = null;
    _volumeLevel = 0.0;
    _hasLevel = false;
    if (!_isSpeaking) {
      _stopWaveformAnimation();
    }
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
    _startWaveformAnimation(mode: 'speak');

    if (_selectedVoice != null) {
      try {
        await _tts.setVoice(_voiceToTts(_selectedVoice!));
      } catch (_) {}
    }
    await _tts.setSpeechRate(_ttsRate);
    await _tts.setPitch(_ttsPitch);
    await _tts.speak(text);
    _isSpeaking = false;
    if (!_isListening) {
      _stopWaveformAnimation();
      _volumeLevel = 0.0;
    }
    notifyListeners();
  }

  Future<void> sendToAssistant() async {
    final String prompt = _transcript.isEmpty ? '안녕하세요, 테스트 요청입니다.' : _transcript;
    final String reply = await _ai.chat(prompt);
    setResponse(reply);
    await speak(reply);
  }

  // Waveform fallback animation for web where sound level may be unavailable
  void _startWaveformAnimation({required String mode}) {
    _animMode = mode;
    _waveAnimTimer ??= Timer.periodic(const Duration(milliseconds: 50), (Timer _) {
      _animPhase += 0.25;
      // Speaking animation always visible; Listening only when no level
      if (_isSpeaking && _animMode == 'speak') {
        final double amp = 0.18;
        _volumeLevel = 0.05 + amp * (0.5 + 0.5 * _sinFast(_animPhase));
        notifyListeners();
        return;
      }
      if (_isListening && !_hasLevel && _animMode == 'listen') {
        final double amp = 0.22;
        _volumeLevel = 0.05 + amp * (0.5 + 0.5 * _sinFast(_animPhase));
        notifyListeners();
      }
    });
  }

  void _stopWaveformAnimation() {
    _animMode = 'none';
    _waveAnimTimer?.cancel();
    _waveAnimTimer = null;
  }

  double _sinFast(double x) => math.sin(x);

  // Voices
  List<Map<String, dynamic>> get availableVoices => _availableVoices;
  Map<String, dynamic>? get selectedVoice => _selectedVoice;
  double get ttsRate => _ttsRate;
  double get ttsPitch => _ttsPitch;

  Future<void> _loadVoices() async {
    try {
      final dynamic voices = await _tts.getVoices;
      if (voices is List) {
        _availableVoices = voices.map<Map<String, dynamic>>((dynamic v) => Map<String, dynamic>.from(v as Map)).toList();
        // pick a Korean voice if available
        _selectedVoice = _availableVoices.firstWhere(
          (Map<String, dynamic> v) => (v['locale']?.toString().startsWith('ko') ?? false),
          orElse: () => _availableVoices.isNotEmpty ? _availableVoices.first : <String, dynamic>{},
        );
        if (_selectedVoice != null && _selectedVoice!.isNotEmpty) {
          try {
            await _tts.setVoice(_voiceToTts(_selectedVoice!));
          } catch (_) {}
        }
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> selectVoiceByName(String name) async {
    final Map<String, dynamic>? pick = _availableVoices.cast<Map<String, dynamic>?>().firstWhere(
      (Map<String, dynamic>? v) => (v?['name']?.toString() ?? '') == name,
      orElse: () => null,
    );
    if (pick != null) {
      _selectedVoice = pick;
      try {
        await _tts.setVoice(_voiceToTts(pick));
      } catch (_) {}
      notifyListeners();
    }
  }

  Future<void> setTtsRate(double value) async {
    _ttsRate = value.clamp(0.1, 1.5);
    await _tts.setSpeechRate(_ttsRate);
    notifyListeners();
  }

  Map<String, String> _voiceToTts(Map<String, dynamic> v) {
    final Map<String, String> out = <String, String>{};
    for (final MapEntry<String, dynamic> e in v.entries) {
      out[e.key] = (e.value ?? '').toString();
    }
    return out;
  }

  Future<void> setTtsPitch(double value) async {
    _ttsPitch = value.clamp(0.5, 2.0);
    await _tts.setPitch(_ttsPitch);
    notifyListeners();
  }
}

// factory moved to speech_recognizer.dart


