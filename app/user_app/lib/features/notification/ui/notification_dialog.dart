import 'package:flutter/material.dart';
import '../models/notification_models.dart';

class NotificationDialog extends StatelessWidget {
  final NotificationMessage message;
  final VoidCallback? onClose;
  final VoidCallback? onViewDetails;

  const NotificationDialog({
    super.key,
    required this.message,
    this.onClose,
    this.onViewDetails,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Row(
        children: [
          // 알림 아이콘
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: _getSeverityColor(message.severity).withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(
              _getKindIcon(message.kind),
              color: _getSeverityColor(message.severity),
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          // 제목
          Expanded(
            child: Text(
              message.title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 시간
            Text(
              _formatDateTime(message.createdAt),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 16),
            
            // 메시지 내용
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey[200]!),
              ),
              child: Text(
                message.body,
                style: const TextStyle(
                  fontSize: 14,
                  height: 1.4,
                ),
              ),
            ),
            
            // 메타데이터 (있는 경우)
            if (message.metadata != null && message.metadata!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '추가 정보',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatMetadata(message.metadata!),
                      style: const TextStyle(
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: onClose,
          child: const Text('닫기'),
        ),
        ElevatedButton(
          onPressed: onViewDetails,
          style: ElevatedButton.styleFrom(
            backgroundColor: _getSeverityColor(message.severity),
            foregroundColor: Colors.white,
          ),
          child: const Text('상세보기'),
        ),
      ],
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'red':
        return Colors.red;
      case 'orange':
        return Colors.orange;
      case 'yellow':
        return Colors.yellow[700]!;
      case 'green':
        return Colors.green;
      case 'blue':
        return Colors.blue;
      case 'purple':
        return Colors.purple;
      default:
        return Colors.blue;
    }
  }

  IconData _getKindIcon(String kind) {
    switch (kind.toLowerCase()) {
      case 'info':
        return Icons.info_outline;
      case 'warning':
        return Icons.warning_outlined;
      case 'error':
        return Icons.error_outline;
      case 'success':
        return Icons.check_circle_outline;
      case 'emergency':
        return Icons.emergency;
      default:
        return Icons.notifications_outlined;
    }
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return '방금 전';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}분 전';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}시간 전';
    } else {
      return '${dateTime.month}/${dateTime.day} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    }
  }

  String _formatMetadata(Map<String, dynamic> metadata) {
    final List<String> items = [];
    
    if (metadata['sender'] != null) {
      items.add('발신자: ${metadata['sender']}');
    }
    
    if (metadata['timestamp'] != null) {
      try {
        final timestamp = DateTime.parse(metadata['timestamp']);
        items.add('시간: ${_formatDateTime(timestamp)}');
      } catch (e) {
        items.add('시간: ${metadata['timestamp']}');
      }
    }
    
    // 기타 메타데이터
    metadata.forEach((key, value) {
      if (key != 'sender' && key != 'timestamp' && value != null) {
        items.add('$key: $value');
      }
    });
    
    return items.join('\n');
  }
}
