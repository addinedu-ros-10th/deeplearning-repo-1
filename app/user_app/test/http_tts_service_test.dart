import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:user_app/features/voice/service/http_tts_service.dart';

void main() {
  group('HttpTtsService', () {
    test('health: ok with backend name', () async {
      final Dio dio = Dio(BaseOptions(baseUrl: 'http://localhost:5502'));
      final DioAdapter adapter = DioAdapter(dio: dio);
      dio.httpClientAdapter = adapter;

      adapter.onGet(
        '/healthz',
        (server) => server.reply(200, <String, dynamic>{'status': 'ok', 'backend': 'piper'}),
      );

      final HttpTtsService svc = HttpTtsService(dio: dio);
      final Map<String, dynamic> info = await svc.health();
      expect(info['status'], 'ok');
      expect(info['backend'], 'piper');
    });
    test('Piper: POST success returns WAV bytes', () async {
      final Dio dio = Dio(BaseOptions(baseUrl: 'http://localhost:5502'));
      final DioAdapter adapter = DioAdapter(dio: dio);
      dio.httpClientAdapter = adapter;

      final List<int> wavBytes = <int>[82, 73, 70, 70]; // 'RIFF' header start
      adapter.onPost(
        '/api/tts',
        (server) => server.reply(200, wavBytes, headers: <String, dynamic>{'content-type': 'audio/wav'}),
        queryParameters: <String, dynamic>{'voice': 'ko_KR-pml_high'},
        data: <String, dynamic>{'text': '안녕하세요'},
      );

      final HttpTtsService svc = HttpTtsService(dio: dio);
      final Uint8List res = await svc.synthesize('안녕하세요', voice: 'ko_KR-pml_high', backend: 'piper');
      expect(res.isNotEmpty, true);
      expect(res[0], 82); // 'R'
    });

    test('Piper: POST 405 fallback to GET', () async {
      final Dio dio = Dio(BaseOptions(baseUrl: 'http://localhost:5502'));
      final DioAdapter adapter = DioAdapter(dio: dio);
      dio.httpClientAdapter = adapter;

      adapter.onPost(
        '/api/tts',
        (server) => server.throws(405, DioException(requestOptions: RequestOptions(path: '/api/tts'), response: Response(requestOptions: RequestOptions(path: '/api/tts'), statusCode: 405))),
        queryParameters: <String, dynamic>{'voice': 'ko_KR-pml_high'},
        data: <String, dynamic>{'text': '테스트'},
      );

      final List<int> wavBytes = <int>[82, 73, 70, 70];
      adapter.onGet(
        '/api/tts',
        (server) => server.reply(200, wavBytes, headers: <String, dynamic>{'content-type': 'audio/wav'}),
        queryParameters: <String, dynamic>{'voice': 'ko_KR-pml_high', 'text': '테스트'},
      );

      final HttpTtsService svc = HttpTtsService(dio: dio);
      final Uint8List res = await svc.synthesize('테스트', voice: 'ko_KR-pml_high', backend: 'piper');
      expect(res.length, wavBytes.length);
    });

    test('Mimic3/OpenTTS: GET success returns WAV bytes', () async {
      final Dio dio = Dio(BaseOptions(baseUrl: 'http://localhost:5502'));
      final DioAdapter adapter = DioAdapter(dio: dio);
      dio.httpClientAdapter = adapter;

      final List<int> wavBytes = <int>[82, 73, 70, 70];
      adapter.onGet(
        '/api/tts',
        (server) => server.reply(200, wavBytes, headers: <String, dynamic>{'content-type': 'audio/wav'}),
        queryParameters: <String, dynamic>{'voice': 'ko_KR-pml_high', 'text': 'Hello'},
      );

      final HttpTtsService svc = HttpTtsService(dio: dio);
      final Uint8List res = await svc.synthesize('Hello', voice: 'ko_KR-pml_high', backend: 'mimic3');
      expect(res[1], 73); // 'I'
    });

    test('Mimic3/OpenTTS: GET 405 fallback to POST', () async {
      final Dio dio = Dio(BaseOptions(baseUrl: 'http://localhost:5502'));
      final DioAdapter adapter = DioAdapter(dio: dio);
      dio.httpClientAdapter = adapter;

      adapter.onGet(
        '/api/tts',
        (server) => server.throws(405, DioException(requestOptions: RequestOptions(path: '/api/tts'), response: Response(requestOptions: RequestOptions(path: '/api/tts'), statusCode: 405))),
        queryParameters: <String, dynamic>{'voice': 'ko_KR-pml_high', 'text': 'Hello'},
      );

      final List<int> wavBytes = <int>[82, 73, 70, 70];
      adapter.onPost(
        '/api/tts',
        (server) => server.reply(200, wavBytes, headers: <String, dynamic>{'content-type': 'audio/wav'}),
        queryParameters: <String, dynamic>{'voice': 'ko_KR-pml_high'},
        data: <String, dynamic>{'text': 'Hello'},
      );

      final HttpTtsService svc = HttpTtsService(dio: dio);
      final Uint8List res = await svc.synthesize('Hello', voice: 'ko_KR-pml_high', backend: 'opentts');
      expect(res[2], 70); // 'F'
    });
  });
}


