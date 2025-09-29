import 'package:dio/dio.dart';
import '../../../core/env/env.dart';

class OpenAiService {
  OpenAiService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppEnv.openaiBaseUrl,
            connectTimeout: const Duration(seconds: 20),
            receiveTimeout: const Duration(seconds: 30),
            headers: {
              if (AppEnv.openaiApiKey.isNotEmpty) 'Authorization': 'Bearer ${AppEnv.openaiApiKey}',
              'Content-Type': 'application/json',
            },
          ),
        );

  final Dio _dio;

  Future<String> chat(String userText) async {
    print('OpenAI API Key: ${AppEnv.openaiApiKey}');
    print('OpenAI Base URL: ${AppEnv.openaiBaseUrl}');
    print('OpenAI Model: ${AppEnv.openaiModel}');
    
    if (AppEnv.openaiApiKey.isEmpty) {
      return 'OpenAI API key가 설정되지 않았습니다. 환경변수를 확인해주세요.';
    }
    
    try {
      final Response<dynamic> res = await _dio.post(
        '/chat/completions',
        data: {
          'model': AppEnv.openaiModel,
          'messages': [
            {'role': 'system', 'content': 'You are a concise Korean assistant.'},
            {'role': 'user', 'content': userText},
          ],
          'temperature': 0.7,
        },
      );
      
      print('OpenAI Response Status: ${res.statusCode}');
      print('OpenAI Response Data: ${res.data}');
      
      final dynamic choices = res.data['choices'];
      if (choices is List && choices.isNotEmpty) {
        final dynamic msg = choices.first['message'];
        final String content = (msg?['content'] as String?) ?? '';
        return content.isEmpty ? '응답이 비어 있습니다.' : content.trim();
      }
      return '응답 형식이 올바르지 않습니다.';
    } catch (e) {
      print('OpenAI Error: $e');
      if (e.toString().contains('CORS')) {
        return 'CORS 오류가 발생했습니다. 브라우저에서 직접 OpenAI API를 호출할 수 없습니다.';
      }
      return 'OpenAI API 호출 중 오류가 발생했습니다: $e';
    }
  }
}


