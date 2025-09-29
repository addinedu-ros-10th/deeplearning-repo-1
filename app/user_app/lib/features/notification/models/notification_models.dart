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
    return NotificationMessage(
      id: json['message_id'] ?? '',
      kind: json['kind'] ?? '',
      severity: json['severity'] ?? '',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      recipients: [], // 서버에서는 recipients가 별도로 관리됨
      channel: 'websocket', // 기본값
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
      metadata: json['data'],
    );
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
