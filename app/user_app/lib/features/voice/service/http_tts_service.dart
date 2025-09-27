import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../../../core/env/env.dart';

class HttpTtsService {
  HttpTtsService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppEnv.ttsBaseUrl.isNotEmpty ? AppEnv.ttsBaseUrl : 'http://localhost:5002',
            connectTimeout: const Duration(seconds: 10),
            receiveTimeout: const Duration(seconds: 30),
          ),
        );

  final Dio _dio;

  // Unified TTS request across Piper/Mimic3/OpenTTS styles
  // Returns 16-bit PCM WAV bytes
  Future<Uint8List> synthesize(String text, {String? voice}) async {
    final String backend = (AppEnv.ttsBackend.isEmpty ? 'system' : AppEnv.ttsBackend).toLowerCase();
    final String pickVoice = (voice?.isNotEmpty == true ? voice! : (AppEnv.ttsDefaultVoice.isNotEmpty ? AppEnv.ttsDefaultVoice : 'ko_KR-pml_high'));

    if (backend == 'piper') {
      // Common Piper HTTP wrapper convention: POST /api/tts?voice=ko_KR-pml_high -> audio/wav
      final Response<dynamic> res = await _dio.post(
        '/api/tts',
        queryParameters: <String, dynamic>{'voice': pickVoice},
        data: <String, dynamic>{'text': text},
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList((res.data as List<int>));
    } else if (backend == 'mimic3') {
      // Mimic3: GET /api/tts?voice=...&text=...
      final Response<dynamic> res = await _dio.get(
        '/api/tts',
        queryParameters: <String, dynamic>{'voice': pickVoice, 'text': text},
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList((res.data as List<int>));
    } else if (backend == 'opentts') {
      // OpenTTS: GET /api/tts?voice=...&text=...
      final Response<dynamic> res = await _dio.get(
        '/api/tts',
        queryParameters: <String, dynamic>{'voice': pickVoice, 'text': text},
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList((res.data as List<int>));
    }

    // system: fallback handled by platform TTS elsewhere
    throw UnsupportedError('HTTP TTS backend not configured: $backend');
  }
}


