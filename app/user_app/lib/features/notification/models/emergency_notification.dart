import 'package:flutter/material.dart';

/// 긴급 알림 모델
class EmergencyNotification {
  final String id;
  final String kind; // system, schedule, info, contact, marketing, inbound
  final String severity; // green, blue, yellow, orange, red
  final String title;
  final String message;
  final DateTime timestamp;
  final bool isRead;
  final Map<String, dynamic>? metadata;

  const EmergencyNotification({
    required this.id,
    required this.kind,
    required this.severity,
    required this.title,
    required this.message,
    required this.timestamp,
    this.isRead = false,
    this.metadata,
  });

  /// 위기 단계 5단계 알림인지 확인
  /// kind: system, severity: red 조건
  bool get isEmergencyLevel5 {
    return kind == 'system' && severity == 'red';
  }

  /// 긴급 알림인지 확인 (위기 단계 4-5단계)
  bool get isEmergency {
    return isEmergencyLevel5 || 
           (kind == 'system' && severity == 'orange');
  }

  /// 알림 색상 반환
  Color get alertColor {
    switch (severity) {
      case 'green':
        return Colors.green;
      case 'blue':
        return Colors.blue;
      case 'yellow':
        return Colors.yellow[600]!;
      case 'orange':
        return Colors.orange[600]!;
      case 'red':
        return Colors.red[600]!;
      default:
        return Colors.grey;
    }
  }

  /// 알림 우선순위 반환 (숫자가 높을수록 우선순위 높음)
  int get priority {
    if (isEmergencyLevel5) return 5;
    if (kind == 'system' && severity == 'orange') return 4;
    if (kind == 'system' && severity == 'yellow') return 3;
    if (kind == 'system' && severity == 'blue') return 2;
    if (kind == 'system' && severity == 'green') return 1;
    return 0;
  }

  factory EmergencyNotification.fromJson(Map<String, dynamic> json) {
    return EmergencyNotification(
      id: json['id'] as String,
      kind: json['kind'] as String,
      severity: json['severity'] as String,
      title: json['title'] as String,
      message: json['message'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      isRead: json['isRead'] as bool? ?? false,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'kind': kind,
      'severity': severity,
      'title': title,
      'message': message,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
      'metadata': metadata,
    };
  }

  EmergencyNotification copyWith({
    String? id,
    String? kind,
    String? severity,
    String? title,
    String? message,
    DateTime? timestamp,
    bool? isRead,
    Map<String, dynamic>? metadata,
  }) {
    return EmergencyNotification(
      id: id ?? this.id,
      kind: kind ?? this.kind,
      severity: severity ?? this.severity,
      title: title ?? this.title,
      message: message ?? this.message,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      metadata: metadata ?? this.metadata,
    );
  }
}
