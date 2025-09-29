import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/notification_provider.dart';
import '../models/notification_models.dart';
import '../../../core/env/env.dart';
import '../../auth/state/auth_provider.dart';

class NotificationListPage extends StatefulWidget {
  const NotificationListPage({super.key});

  @override
  State<NotificationListPage> createState() => _NotificationListPageState();
}

class _NotificationListPageState extends State<NotificationListPage> {
  @override
  void initState() {
    super.initState();
    // 페이지 로드 시 메시지 새로고침
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<NotificationProvider>().notifyListeners();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('알림'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white70,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<NotificationProvider>().notifyListeners();
            },
          ),
          IconButton(
            icon: const Icon(Icons.clear_all),
            onPressed: () {
              _showClearDialog();
            },
          ),
        ],
      ),
      body: Consumer2<NotificationProvider, AuthProvider>(
        builder: (context, notificationProvider, authProvider, _) {
          // 사용자 ID 표시
          final currentUserId = authProvider.userId ?? '로그인 필요';
          
          // 알림 시스템이 비활성화된 경우
          if (!AppEnv.notifyEnabled) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.notifications_off,
                    size: 64,
                    color: Colors.orange,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '알림 시스템이 비활성화되어 있습니다',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '서버 관리자에게 문의하세요',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '현재 사용자 ID: $currentUserId',
                    style: const TextStyle(
                      color: Colors.blue,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            );
          }

          if (notificationProvider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (notificationProvider.messages.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.notifications_none,
                    size: 64,
                    color: Colors.grey,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '알림이 없습니다',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '현재 사용자 ID: $currentUserId',
                    style: const TextStyle(
                      color: Colors.blue,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: notificationProvider.messages.length,
            itemBuilder: (context, index) {
              final message = notificationProvider.messages[index];
              return _buildNotificationCard(message);
            },
          );
        },
      ),
    );
  }

  Widget _buildNotificationCard(NotificationMessage message) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: Colors.grey[900],
      child: ListTile(
        leading: _buildSeverityIcon(message.severity),
        title: Text(
          message.title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              message.body,
              style: const TextStyle(color: Colors.white70),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                _buildKindChip(message.kind),
                const SizedBox(width: 8),
                Text(
                  _formatDateTime(message.createdAt),
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.close, color: Colors.grey),
          onPressed: () {
            context.read<NotificationProvider>().removeMessage(message.id);
          },
        ),
        onTap: () {
          _showMessageDetail(message);
        },
      ),
    );
  }

  Widget _buildSeverityIcon(String severity) {
    IconData icon;
    Color color;

    switch (severity) {
      case 'green':
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case 'blue':
        icon = Icons.info;
        color = Colors.blue;
        break;
      case 'yellow':
        icon = Icons.warning;
        color = Colors.yellow;
        break;
      case 'orange':
        icon = Icons.warning_amber;
        color = Colors.orange;
        break;
      case 'red':
        icon = Icons.error;
        color = Colors.red;
        break;
      default:
        icon = Icons.notifications;
        color = Colors.grey;
    }

    return Icon(icon, color: color, size: 24);
  }

  Widget _buildKindChip(String kind) {
    String label;
    Color color;

    switch (kind) {
      case 'system':
        label = '시스템';
        color = Colors.blue;
        break;
      case 'schedule':
        label = '일정';
        color = Colors.green;
        break;
      case 'info':
        label = '정보';
        color = Colors.cyan;
        break;
      case 'contact':
        label = '연락';
        color = Colors.orange;
        break;
      case 'marketing':
        label = '마케팅';
        color = Colors.purple;
        break;
      case 'inbound':
        label = '메시지';
        color = Colors.teal;
        break;
      default:
        label = kind;
        color = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 0) {
      return '${difference.inDays}일 전';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}시간 전';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}분 전';
    } else {
      return '방금 전';
    }
  }

  void _showMessageDetail(NotificationMessage message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: Row(
          children: [
            _buildSeverityIcon(message.severity),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                message.title,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.body,
              style: const TextStyle(color: Colors.white70),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _buildKindChip(message.kind),
                const SizedBox(width: 8),
                Text(
                  '심각도: ${message.severity}',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '수신자: ${message.recipients.join(', ')}',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 8),
            Text(
              '시간: ${_formatDateTime(message.createdAt)}',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('닫기'),
          ),
          TextButton(
            onPressed: () {
              context.read<NotificationProvider>().removeMessage(message.id);
              Navigator.of(context).pop();
            },
            child: const Text('삭제'),
          ),
        ],
      ),
    );
  }

  void _showClearDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Text(
          '모든 알림 삭제',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          '모든 알림을 삭제하시겠습니까?',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () {
              context.read<NotificationProvider>().clearMessages();
              Navigator.of(context).pop();
            },
            child: const Text('삭제'),
          ),
        ],
      ),
    );
  }
}
