import 'package:flutter_tts/flutter_tts.dart';
import 'dart:async';

class FlutterTtsService {
  FlutterTtsService() {
    _initTts();
  }

  FlutterTts flutterTts = FlutterTts();
  bool _isInitialized = false;
  String _currentVoice = 'en-US';
  List<dynamic> _voices = [];
  Function()? _onComplete;
  Function()? _onError;

  Future<void> _initTts() async {
    try {
      await flutterTts.setLanguage("ko-KR");
      await flutterTts.setSpeechRate(0.5);
      await flutterTts.setVolume(1.0);
      await flutterTts.setPitch(1.0);
      
      // 사용 가능한 음성 목록 가져오기
      _voices = await flutterTts.getVoices;
      
      // 완료 및 에러 콜백 설정
      flutterTts.setCompletionHandler(() {
        print('TTS completed');
        _onComplete?.call();
      });
      
      flutterTts.setErrorHandler((msg) {
        print('TTS error: $msg');
        _onError?.call();
      });
      
      _isInitialized = true;
      print('FlutterTts initialized successfully');
    } catch (e) {
      print('FlutterTts initialization error: $e');
    }
  }

  Future<bool> isInitialized() async {
    return _isInitialized;
  }

  void setCallbacks({Function()? onComplete, Function()? onError}) {
    _onComplete = onComplete;
    _onError = onError;
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) {
      await _initTts();
    }
    
    try {
      await flutterTts.speak(text);
    } catch (e) {
      print('TTS speak error: $e');
    }
  }

  Future<void> stop() async {
    try {
      await flutterTts.stop();
    } catch (e) {
      print('TTS stop error: $e');
    }
  }

  Future<void> pause() async {
    try {
      await flutterTts.pause();
    } catch (e) {
      print('TTS pause error: $e');
    }
  }

  Future<List<String>> getAvailableVoices() async {
    if (!_isInitialized) {
      await _initTts();
    }
    
    try {
      List<String> voiceNames = [];
      for (var voice in _voices) {
        if (voice['name'] != null) {
          voiceNames.add(voice['name']);
        }
      }
      
      // 기본 음성들 추가 (사용 가능한 음성이 없을 경우)
      if (voiceNames.isEmpty) {
        voiceNames = [
          'en-US-Standard-A',
          'en-US-Standard-B', 
          'en-US-Standard-C',
          'en-US-Standard-D',
          'en-US-Standard-E',
          'en-US-Standard-F',
          'en-US-Standard-G',
          'en-US-Standard-H',
          'en-US-Standard-I',
          'en-US-Standard-J',
        ];
      }
      
      return voiceNames;
    } catch (e) {
      print('Get voices error: $e');
      return ['Default Voice'];
    }
  }

  Future<void> setVoice(String voiceName) async {
    if (!_isInitialized) {
      await _initTts();
    }
    
    try {
      await flutterTts.setVoice({"name": voiceName, "locale": "ko-KR"});
      _currentVoice = voiceName;
    } catch (e) {
      print('Set voice error: $e');
    }
  }

  Future<void> setSpeechRate(double rate) async {
    try {
      await flutterTts.setSpeechRate(rate);
    } catch (e) {
      print('Set speech rate error: $e');
    }
  }

  Future<void> setVolume(double volume) async {
    try {
      await flutterTts.setVolume(volume);
    } catch (e) {
      print('Set volume error: $e');
    }
  }

  Future<void> setPitch(double pitch) async {
    try {
      await flutterTts.setPitch(pitch);
    } catch (e) {
      print('Set pitch error: $e');
    }
  }

  String getCurrentVoice() {
    return _currentVoice;
  }

  void dispose() {
    flutterTts.stop();
  }
}
