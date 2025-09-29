import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppEnv {
  AppEnv._();

  static String get appEnv => const String.fromEnvironment('APP_ENV', defaultValue: 'dev');
  static const bool _useDotenv = bool.fromEnvironment('USE_DOTENV', defaultValue: true);

  static Future<void> load() async {
    if (_useDotenv) {
      try {
        final String fileName = appEnv == 'prod' ? 'assets/env/.env.prod' : 'assets/env/.env.dev';
        await dotenv.load(fileName: fileName, mergeWith: {});
      } catch (_) {
        // no-op; web may not package .env assets
      }
    }
  }

  static String _safeMaybeGet(String key) {
    try {
      return dotenv.maybeGet(key) ?? '';
    } catch (_) {
      return '';
    }
  }

  static String get apiBaseUrl {
    const String envValue = String.fromEnvironment('IOT_BASE_URL');
    if (envValue.isNotEmpty) return envValue;
    final dotenvValue = _safeMaybeGet('IOT_BASE_URL');
    if (dotenvValue.isNotEmpty) return dotenvValue;
    return 'http://ec2-13-125-249-77.ap-northeast-2.compute.amazonaws.com';
  }

  static String get wsUrl {
    const String envValue = String.fromEnvironment('WS_URL');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('WS_URL');
  }

  static String get authToken {
    const String envValue = String.fromEnvironment('AUTH_TOKEN');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('AUTH_TOKEN');
  }

  // TTS backend endpoints and defaults
  static String get ttsBackend { // piper | mimic3 | opentts | system
    const String envValue = String.fromEnvironment('TTS_BACKEND');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('TTS_BACKEND');
  }

  static String get ttsBaseUrl { // http(s)://host:port
    const String envValue = String.fromEnvironment('TTS_BASE_URL');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('TTS_BASE_URL');
  }

  static String get ttsDefaultVoice { // e.g., ko_KR-pml_high or ko-KR-Standard-A
    const String envValue = String.fromEnvironment('TTS_DEFAULT_VOICE');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('TTS_DEFAULT_VOICE');
  }

  // OpenAI API Configuration
  static String get openaiApiKey {
    const String envValue = String.fromEnvironment('OPENAI_API_KEY');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('OPENAI_API_KEY');
  }

  static String get openaiBaseUrl {
    const String envValue = String.fromEnvironment('OPENAI_BASE_URL');
    if (envValue.isNotEmpty) return envValue;
    final dotenvValue = _safeMaybeGet('OPENAI_BASE_URL');
    if (dotenvValue.isNotEmpty) return dotenvValue;
    return 'https://api.openai.com/v1';
  }

  static String get openaiModel {
    const String envValue = String.fromEnvironment('OPENAI_MODEL');
    if (envValue.isNotEmpty) return envValue;
    final dotenvValue = _safeMaybeGet('OPENAI_MODEL');
    if (dotenvValue.isNotEmpty) return dotenvValue;
    return 'gpt-4o-mini';
  }

  // 알림 시스템 설정
  static String get notifyBaseUrl {
    const String envValue = String.fromEnvironment('NOTIFY_BASE_URL');
    if (envValue.isNotEmpty) return envValue;
    final dotenvValue = _safeMaybeGet('NOTIFY_BASE_URL');
    if (dotenvValue.isNotEmpty) return dotenvValue;
    // 기본값으로 API 서버와 동일한 URL 사용
    return apiBaseUrl;
  }

  // DL 서버 설정 (알림 서버)
  static String get dlBaseUrl {
    const String envValue = String.fromEnvironment('DL_BASE_URL');
    if (envValue.isNotEmpty) return envValue;
    final dotenvValue = _safeMaybeGet('DL_BASE_URL');
    if (dotenvValue.isNotEmpty) return dotenvValue;
    // 기본값으로 제공된 DL 서버 URL 사용
    return 'http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com';
  }

  static bool get notifyEnabled {
    const String envValue = String.fromEnvironment('NOTIFY_ENABLE');
    if (envValue.isNotEmpty) return envValue.toLowerCase() == 'true';
    final dotenvValue = _safeMaybeGet('NOTIFY_ENABLE');
    if (dotenvValue.isNotEmpty) return dotenvValue.toLowerCase() == 'true';
    return true; // 기본적으로 활성화
  }
}


