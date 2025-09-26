import 'package:dio/dio.dart';
import '../../../core/env/env.dart';

class OpenAiService {
  OpenAiService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: 'https://api.openai.com',
            connectTimeout: const Duration(seconds: 20),
            receiveTimeout: const Duration(seconds: 30),
            headers: {
              if (AppEnv.authToken.isNotEmpty) 'Authorization': 'Bearer ${AppEnv.authToken}',
              'Content-Type': 'application/json',
            },
          ),
        );

  final Dio _dio;

  Future<String> chat(String userText) async {
    if (AppEnv.authToken.isEmpty) {
      return 'OpenAI API key가 설정되지 않았습니다.';
    }
    final Response<dynamic> res = await _dio.post(
      '/v1/chat/completions',
      data: {
        'model': 'gpt-4o-mini',
        'messages': [
          {'role': 'system', 'content': 'You are a concise Korean assistant.'},
          {'role': 'user', 'content': userText},
        ],
        'temperature': 0.7,
      },
    );
    try {
      final dynamic choices = res.data['choices'];
      if (choices is List && choices.isNotEmpty) {
        final dynamic msg = choices.first['message'];
        final String content = (msg?['content'] as String?) ?? '';
        return content.isEmpty ? '응답이 비어 있습니다.' : content.trim();
      }
      return '응답 형식이 올바르지 않습니다.';
    } catch (_) {
      return '응답 파싱 중 오류가 발생했습니다.';
    }
  }
}


