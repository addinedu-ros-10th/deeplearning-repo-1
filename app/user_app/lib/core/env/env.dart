import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppEnv {
  AppEnv._();

  static String get appEnv => const String.fromEnvironment('APP_ENV', defaultValue: 'dev');
  static const bool _useDotenv = bool.fromEnvironment('USE_DOTENV', defaultValue: false);

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
    const String envValue = String.fromEnvironment('API_BASE_URL');
    if (envValue.isNotEmpty) return envValue;
    return _safeMaybeGet('API_BASE_URL');
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
}


