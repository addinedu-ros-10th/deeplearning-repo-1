import 'package:web_socket_channel/web_socket_channel.dart';
import '../env/env.dart';

class WsClient {
  WsClient._internal();
  static final WsClient _instance = WsClient._internal();
  factory WsClient() => _instance;

  WebSocketChannel? _channel;

  WebSocketChannel connect() {
    _channel ??= WebSocketChannel.connect(Uri.parse(AppEnv.wsUrl));
    return _channel!;
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}


