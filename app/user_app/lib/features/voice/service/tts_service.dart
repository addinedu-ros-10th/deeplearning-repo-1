import 'package:dio/dio.dart';
import 'dart:typed_data';
import '../../../core/env/env.dart';

class TtsService {
  TtsService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppEnv.ttsBaseUrl.isNotEmpty ? AppEnv.ttsBaseUrl : 'http://localhost:8000',
            connectTimeout: const Duration(seconds: 30),
            receiveTimeout: const Duration(seconds: 60),
            headers: {
              'Content-Type': 'application/json',
            },
          ),
        );

  final Dio _dio;

  Future<Uint8List?> synthesize(String text, {String? voice}) async {
    try {
      final response = await _dio.post(
        '/tts',
        data: {
          'text': text,
          'voice': voice ?? (AppEnv.ttsDefaultVoice.isNotEmpty ? AppEnv.ttsDefaultVoice : 'alloy'),
        },
        options: Options(
          responseType: ResponseType.bytes,
        ),
      );

      if (response.data is List<int>) {
        return Uint8List.fromList(response.data);
      }
      return null;
    } catch (e) {
      print('TTS Error: $e');
      return null;
    }
  }

  Future<List<String>> getAvailableVoices() async {
    try {
      final response = await _dio.get('/voices');
      if (response.data is List) {
        return List<String>.from(response.data);
      }
      return ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];
    } catch (e) {
      print('Get voices error: $e');
      return ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];
    }
  }
}
