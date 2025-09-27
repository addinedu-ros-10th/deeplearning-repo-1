import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../../../core/env/env.dart';

class HttpTtsService {
  HttpTtsService({Dio? dio, String? baseUrl})
      : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: baseUrl ?? (AppEnv.ttsBaseUrl.isNotEmpty ? AppEnv.ttsBaseUrl : 'http://localhost:5002'),
                connectTimeout: const Duration(seconds: 10),
                receiveTimeout: const Duration(seconds: 30),
              ),
            );

  final Dio _dio;

  // GET /healthz expected: { status: "ok", backend: "piper" }
  Future<Map<String, dynamic>> health() async {
    final Response<dynamic> res = await _dio.get('/healthz');
    final dynamic data = res.data;
    if (data is Map<String, dynamic>) return data;
    if (data is Map) return Map<String, dynamic>.from(data);
    return <String, dynamic>{};
  }

  // Unified TTS request across Piper/Mimic3/OpenTTS styles
  // Returns 16-bit PCM WAV bytes
  Future<Uint8List> synthesize(String text, {String? voice, String? backend}) async {
    final String resolvedBackend = ((backend ?? AppEnv.ttsBackend).isEmpty ? 'system' : (backend ?? AppEnv.ttsBackend)).toLowerCase();
    final String pickVoice = (voice?.isNotEmpty == true ? voice! : (AppEnv.ttsDefaultVoice.isNotEmpty ? AppEnv.ttsDefaultVoice : 'ko_KR-pml_high'));

    if (resolvedBackend == 'piper') {
      // Piper via wrapper: prefer POST, fallback to GET for compatibility
      try {
        final Response<dynamic> res = await _dio.post(
          '/api/tts',
          queryParameters: <String, dynamic>{'voice': pickVoice},
          data: <String, dynamic>{'text': text},
          options: Options(responseType: ResponseType.bytes),
        );
        return Uint8List.fromList((res.data as List<int>));
      } on DioException catch (e) {
        final int code = e.response?.statusCode ?? -1;
        if (code == 404 || code == 400 || code == 405) {
          final Response<dynamic> res = await _dio.get(
            '/api/tts',
            queryParameters: <String, dynamic>{'voice': pickVoice, 'text': text},
            options: Options(responseType: ResponseType.bytes),
          );
          return Uint8List.fromList((res.data as List<int>));
        }
        rethrow;
      }
    } else if (resolvedBackend == 'mimic3' || resolvedBackend == 'opentts') {
      // Mimic3/OpenTTS: prefer GET, fallback to POST for compatibility
      try {
        final Response<dynamic> res = await _dio.get(
          '/api/tts',
          queryParameters: <String, dynamic>{'voice': pickVoice, 'text': text},
          options: Options(responseType: ResponseType.bytes),
        );
        return Uint8List.fromList((res.data as List<int>));
      } on DioException catch (e) {
        final int code = e.response?.statusCode ?? -1;
        if (code == 404 || code == 400 || code == 405) {
          final Response<dynamic> res = await _dio.post(
            '/api/tts',
            queryParameters: <String, dynamic>{'voice': pickVoice},
            data: <String, dynamic>{'text': text},
            options: Options(responseType: ResponseType.bytes),
          );
          return Uint8List.fromList((res.data as List<int>));
        }
        rethrow;
      }
    }

    // system: fallback handled by platform TTS elsewhere
    throw UnsupportedError('HTTP TTS backend not configured: $resolvedBackend');
  }
}


