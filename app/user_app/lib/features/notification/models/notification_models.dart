class NotificationMessage {
  final String id;
  final String kind;
  final String severity;
  final String title;
  final String body;
  final List<String> recipients;
  final String channel;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  NotificationMessage({
    required this.id,
    required this.kind,
    required this.severity,
    required this.title,
    required this.body,
    required this.recipients,
    required this.channel,
    required this.createdAt,
    this.updatedAt,
    this.metadata,
  });

  factory NotificationMessage.fromJson(Map<String, dynamic> json) {
    print('=== NotificationMessage.fromJson 파싱 시작 ===');
    print('입력 JSON: $json');
    
    // ID 파싱 (다양한 필드명 지원)
    final id = _extractString(json, ['message_id', 'id', 'notification_id']) ?? 
                DateTime.now().millisecondsSinceEpoch.toString();
    
    // kind 파싱 (다양한 위치에서 찾기)
    final kind = _extractKind(json);
    
    // severity 파싱 (다양한 위치에서 찾기)
    final severity = _extractSeverity(json);
    
    // title 파싱
    final title = _extractString(json, ['title', 'subject', 'heading']) ?? '알림';
    
    // body 파싱
    final body = _extractString(json, ['body', 'message', 'content', 'text']) ?? '';
    
    // createdAt 파싱
    final createdAt = _extractDateTime(json, ['created_at', 'timestamp', 'created']) ?? 
                      DateTime.now();
    
    // updatedAt 파싱
    final updatedAt = _extractDateTime(json, ['updated_at', 'modified_at']);
    
    // metadata 파싱
    final metadata = json['data'] ?? json['metadata'] ?? json['payload'];
    
    print('파싱 결과:');
    print('  id: $id');
    print('  kind: $kind');
    print('  severity: $severity');
    print('  title: $title');
    print('  body: $body');
    print('  createdAt: $createdAt');
    print('  updatedAt: $updatedAt');
    print('  metadata: $metadata');
    print('==========================================');
    
    return NotificationMessage(
      id: id,
      kind: kind,
      severity: severity,
      title: title,
      body: body,
      recipients: [], // 서버에서는 recipients가 별도로 관리됨
      channel: 'websocket', // 기본값
      createdAt: createdAt,
      updatedAt: updatedAt,
      metadata: metadata,
    );
  }
  
  // kind 값 추출 (다양한 위치에서 찾기)
  static String _extractKind(Map<String, dynamic> json) {
    // 1. 직접 필드에서 찾기
    final directKind = _extractString(json, ['kind', 'type', 'category']);
    if (directKind != null && directKind.isNotEmpty) {
      return directKind;
    }
    
    // 2. data/metadata 객체 안에서 찾기
    final data = json['data'] ?? json['metadata'] ?? json['payload'];
    if (data is Map<String, dynamic>) {
      final dataKind = _extractString(data, ['kind', 'type', 'category']);
      if (dataKind != null && dataKind.isNotEmpty) {
        return dataKind;
      }
    }
    
    // 3. 기본값 (정보 알림으로 가정)
    return 'info';
  }
  
  // severity 값 추출 (다양한 위치에서 찾기)
  static String _extractSeverity(Map<String, dynamic> json) {
    // 1. 직접 필드에서 찾기
    final directSeverity = _extractString(json, ['severity', 'level', 'priority']);
    if (directSeverity != null && directSeverity.isNotEmpty) {
      return directSeverity;
    }
    
    // 2. data/metadata 객체 안에서 찾기
    final data = json['data'] ?? json['metadata'] ?? json['payload'];
    if (data is Map<String, dynamic>) {
      final dataSeverity = _extractString(data, ['severity', 'level', 'priority']);
      if (dataSeverity != null && dataSeverity.isNotEmpty) {
        return dataSeverity;
      }
    }
    
    // 3. 기본값 (정상 수준으로 가정)
    return 'green';
  }
  
  // 문자열 값 추출 (여러 필드명 시도)
  static String? _extractString(Map<String, dynamic> json, List<String> fieldNames) {
    for (final fieldName in fieldNames) {
      final value = json[fieldName];
      if (value != null && value.toString().isNotEmpty) {
        return value.toString();
      }
    }
    return null;
  }
  
  // DateTime 값 추출
  static DateTime? _extractDateTime(Map<String, dynamic> json, List<String> fieldNames) {
    for (final fieldName in fieldNames) {
      final value = json[fieldName];
      if (value != null) {
        try {
          if (value is String) {
            return DateTime.parse(value);
          } else if (value is int) {
            return DateTime.fromMillisecondsSinceEpoch(value);
          }
        } catch (e) {
          print('DateTime 파싱 오류 ($fieldName): $e');
        }
      }
    }
    return null;
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'kind': kind,
      'severity': severity,
      'title': title,
      'body': body,
      'recipients': recipients,
      'channel': channel,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'metadata': metadata,
    };
  }
}

class NotificationQueueRequest {
  final String kind;
  final String severity;
  final String title;
  final String body;
  final List<String> recipients;
  final String channel;
  final Map<String, dynamic>? metadata;

  NotificationQueueRequest({
    required this.kind,
    required this.severity,
    required this.title,
    required this.body,
    required this.recipients,
    required this.channel,
    this.metadata,
  });

  Map<String, dynamic> toJson() {
    return {
      'kind': kind,
      'severity': severity,
      'title': title,
      'body': body,
      'recipients': recipients,
      'channel': channel,
      'metadata': metadata,
    };
  }
}

class NotificationQueueResponse {
  final String messageId;
  final int deliveryCount;
  final String status;

  NotificationQueueResponse({
    required this.messageId,
    required this.deliveryCount,
    required this.status,
  });

  factory NotificationQueueResponse.fromJson(Map<String, dynamic> json) {
    return NotificationQueueResponse(
      messageId: json['message_id'] ?? '',
      deliveryCount: json['queued_count'] ?? 0,
      status: 'queued',
    );
  }
}

// 알림 종류 enum
enum NotificationKind {
  system('system'),
  schedule('schedule'),
  info('info'),
  contact('contact'),
  marketing('marketing'),
  inbound('inbound');

  const NotificationKind(this.value);
  final String value;
}

// 알림 심각도 enum
enum NotificationSeverity {
  green('green'),
  blue('blue'),
  yellow('yellow'),
  orange('orange'),
  red('red');

  const NotificationSeverity(this.value);
  final String value;
}
