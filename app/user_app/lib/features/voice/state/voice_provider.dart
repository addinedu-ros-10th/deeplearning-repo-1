import 'dart:async';
import 'package:flutter/foundation.dart';
import 'dart:math' as math;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:typed_data';
import '../../../core/env/env.dart';
import '../service/openai_service.dart';
import '../service/speech_recognizer.dart';
import '../service/http_tts_service.dart';

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
  final HttpTtsService _httpTts = HttpTtsService();

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
  List<String> _availableEngines = <String>[]; // Android only; empty elsewhere
  String? _selectedEngine;
  final List<String> _availableBackends = <String>['system', 'piper', 'mimic3', 'opentts'];
  String _selectedBackend = (AppEnv.ttsBackend.isEmpty ? 'system' : AppEnv.ttsBackend).toLowerCase();
  List<String> _availableModelVoices = <String>[];
  String? _selectedModelVoice = AppEnv.ttsDefaultVoice.isNotEmpty ? AppEnv.ttsDefaultVoice : null;
  final AudioPlayer _audioPlayer = AudioPlayer();
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
    await _loadEngines();
    await _ensureKoreanLanguage();
    await _loadVoices();
    _refreshModelVoices();
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

  Future<void> speak(String text, {String? overrideVoice, bool useHttpTtsIfConfigured = true}) async {
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
    // If external HTTP TTS backend configured, prefer it for Korean voices
    try {
      if (useHttpTtsIfConfigured) {
        final String backend = _selectedBackend;
        if (backend == 'piper' || backend == 'mimic3' || backend == 'opentts') {
          final String? modelVoice = _selectedModelVoice ?? AppEnv.ttsDefaultVoice;
          final Uint8List wav = await _httpTts.synthesize(text, voice: modelVoice);
          await _playWavBytes(wav);
        } else {
          await _tts.speak(text);
        }
      } else {
        await _tts.speak(text);
      }
    } catch (_) {
      // fallback to system TTS
      await _tts.speak(text);
    }
    _isSpeaking = false;
    if (!_isListening) {
      _stopWaveformAnimation();
      _volumeLevel = 0.0;
    }
    notifyListeners();
  }

  Future<void> _playWavBytes(Uint8List wavBytes) async {
    await _audioPlayer.stop();
    await _audioPlayer.play(BytesSource(wavBytes));
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
  List<String> get availableEngines => _availableEngines;
  String? get selectedEngine => _selectedEngine;
  List<String> get availableBackends => _availableBackends;
  String get selectedBackend => _selectedBackend;
  List<String> get availableModelVoices => _availableModelVoices;
  String? get selectedModelVoice => _selectedModelVoice;

  String get engineInfoText {
    final String platform = defaultTargetPlatform.name;
    final String engine = (_selectedEngine ?? '').toLowerCase();
    if (engine.contains('google')) {
      return 'TTS 엔진: Google (Android). 한국어 ko-KR 음성이 비교적 자연스럽고 기기/버전에 따라 다양한 음성이 제공됩니다.';
    }
    if (engine.contains('samsung')) {
      return 'TTS 엔진: Samsung (Android). 한국어 음성 제공. 일부 기기에서 발음/억양 차이가 있을 수 있습니다.';
    }
    if (platform == 'iOS') {
      return 'TTS 엔진: iOS AVSpeechSynthesizer. 기기/OS 버전에 따라 한국어(ko-KR) 음성 품질이 다를 수 있습니다.';
    }
    if (_selectedEngine == null || _selectedEngine!.isEmpty) {
      return 'TTS 엔진: 시스템 기본 엔진 사용. 한국어 자연스러움을 위해 ko-KR 음성 선택을 권장합니다.';
    }
    return 'TTS 엔진: $_selectedEngine';
  }

  String get voiceInfoText {
    final String locale = (_selectedVoice?['locale']?.toString() ?? '').toLowerCase();
    final String name = _selectedVoice?['name']?.toString() ?? 'unknown';
    if (locale.startsWith('ko')) {
      return '선택된 음성: $name ($locale). 한국어 전용/지원 음성으로 자연스러운 발화를 기대할 수 있습니다.';
    }
    if (locale.isEmpty) {
      return '선택된 음성 정보가 제한적입니다. 한국어(ko-KR) 음성을 선택하면 자연스러움이 개선됩니다.';
    }
    return '선택된 음성: $name ($locale). 한국어가 아니므로 발음이 어색할 수 있습니다. ko-KR 음성을 권장합니다.';
  }

  String get sttInfoText {
    final String platform = defaultTargetPlatform.name;
    if (platform == 'android') {
      return 'STT: 기기 내 Google 음성 인식(설정에 따라 다름). 한국어 ko-KR로 설정 시 인식 품질이 개선됩니다.';
    }
    if (platform == 'iOS') {
      return 'STT: iOS 음성 인식. 한국어(ko-KR) 로케일 사용 시 인식률이 향상됩니다.';
    }
    return 'STT: 플랫폼 기본 음성 인식 사용. 한국어 로케일 설정과 조용한 환경이 인식 품질에 도움이 됩니다.';
  }

  String get backendInfoText {
    switch (_selectedBackend) {
      case 'piper':
        return 'Piper: 경량 고속, ko_KR-pml_high/low 추천. 서버 URL 필요.';
      case 'mimic3':
        return 'Mimic3: 다양한 음색, REST API. Piper보다 무거움.';
      case 'opentts':
        return 'OpenTTS: Piper/Mimic3 등 통합. 백엔드 교체 용이.';
      default:
        return 'System TTS: 기기 내 엔진 사용(예: Google TTS). ko-KR 음성 선택 권장.';
    }
  }

  String get modelVoiceInfoText {
    if (_selectedBackend == 'piper') {
      final String v = _selectedModelVoice ?? 'ko_KR-pml_high';
      return '모델 음성: $v (Piper). 일반적으로 pml_high가 더 자연스럽습니다.';
    }
    if (_selectedBackend == 'mimic3' || _selectedBackend == 'opentts') {
      return '모델 음성: ${_selectedModelVoice ?? '(미지정)'} (서버가 제공하는 보이스 이름을 사용)';
    }
    return '모델 음성: 시스템 엔진의 기기 음성 선택을 사용';
  }

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

  Future<void> _loadEngines() async {
    try {
      final dynamic engines = await _tts.getEngines;
      if (engines is List) {
        _availableEngines = engines.cast<String>().toList();
        // Prefer Google TTS if available on Android
        final String google = _availableEngines.firstWhere(
          (String e) => e.toLowerCase().contains('google'),
          orElse: () => _availableEngines.isNotEmpty ? _availableEngines.first : '',
        );
        if (google.isNotEmpty) {
          _selectedEngine = google;
          try {
            await _tts.setEngine(google);
          } catch (_) {}
        }
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> selectEngine(String engine) async {
    _selectedEngine = engine;
    try {
      await _tts.setEngine(engine);
    } catch (_) {}
    await _ensureKoreanLanguage();
    await _loadVoices();
    notifyListeners();
  }

  void selectBackend(String backend) {
    _selectedBackend = backend.toLowerCase();
    _refreshModelVoices();
    notifyListeners();
  }

  void setModelVoice(String voice) {
    _selectedModelVoice = voice;
    notifyListeners();
  }

  void _refreshModelVoices() {
    if (_selectedBackend == 'piper') {
      _availableModelVoices = <String>['ko-KR-pml-high', 'ko-KR-pml-low'];
      _selectedModelVoice ??= 'ko-KR-pml-high';
    } else {
      _availableModelVoices = <String>[];
      // keep selectedModelVoice as-is for non-Piper backends
    }
  }

  Future<void> _ensureKoreanLanguage() async {
    try {
      // Best-effort: set language to Korean for more natural TTS
      await _tts.setLanguage('ko-KR');
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


