import 'package:dio/dio.dart';
import 'package:logging/logging.dart';
import '../env/env.dart';

class ApiClient {
  ApiClient._internal()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppEnv.apiBaseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 30),
            headers: {
              if (AppEnv.authToken.isNotEmpty) 'Authorization': 'Bearer ${AppEnv.authToken}',
              'Content-Type': 'application/json',
            },
          ),
        ) {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          _logger.fine('➡️ ${options.method} ${options.uri}');
          return handler.next(options);
        },
        onResponse: (response, handler) {
          _logger.fine('✅ ${response.statusCode} ${response.requestOptions.uri}');
          return handler.next(response);
        },
        onError: (error, handler) {
          _logger.warning('❌ ${error.response?.statusCode} ${error.requestOptions.uri}: ${error.message}');
          return handler.next(error);
        },
      ),
    );
  }

  static final Logger _logger = Logger('ApiClient');
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  final Dio _dio;

  Dio get client => _dio;
}


