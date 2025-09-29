import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/notification_provider.dart';
import '../models/notification_models.dart';
import '../../../core/env/env.dart';
import '../../auth/state/auth_provider.dart';

class SendMessagePage extends StatefulWidget {
  const SendMessagePage({super.key});

  @override
  State<SendMessagePage> createState() => _SendMessagePageState();
}

class _SendMessagePageState extends State<SendMessagePage> {
  final _titleController = TextEditingController();
  final _bodyController = TextEditingController();
  final _recipientsController = TextEditingController();
  
  NotificationKind _selectedKind = NotificationKind.info;
  NotificationSeverity _selectedSeverity = NotificationSeverity.blue;
  bool _isSending = false;

  @override
  void dispose() {
    _titleController.dispose();
    _bodyController.dispose();
    _recipientsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final currentUserId = authProvider.userId ?? '로그인 필요';
    
    // 알림 시스템이 비활성화된 경우
    if (!AppEnv.notifyEnabled) {
      return Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          title: const Text('메시지 전송'),
          backgroundColor: Colors.black,
          foregroundColor: Colors.white70,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ),
        body: Center(
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
                '메시지 전송 기능을 사용할 수 없습니다',
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
        ),
      );
    }

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('메시지 전송'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white70,
        actions: [
          TextButton(
            onPressed: _isSending ? null : _sendMessage,
            child: _isSending
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('전송'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 사용자 ID 표시
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[900],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '현재 사용자 ID: $currentUserId',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // 제목 입력
            const Text(
              '제목',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _titleController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: '메시지 제목을 입력하세요',
                hintStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: Colors.grey[900],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // 내용 입력
            const Text(
              '내용',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _bodyController,
              maxLines: 4,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: '메시지 내용을 입력하세요',
                hintStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: Colors.grey[900],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // 수신자 입력
            const Text(
              '수신자 (쉼표로 구분)',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _recipientsController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'user1, user2, user3',
                hintStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: Colors.grey[900],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // 알림 종류 선택
            const Text(
              '알림 종류',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: NotificationKind.values.map((kind) {
                return ChoiceChip(
                  label: Text(_getKindLabel(kind)),
                  selected: _selectedKind == kind,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() {
                        _selectedKind = kind;
                      });
                    }
                  },
                  selectedColor: Colors.blue.withOpacity(0.3),
                  labelStyle: TextStyle(
                    color: _selectedKind == kind ? Colors.white : Colors.grey,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // 심각도 선택
            const Text(
              '심각도',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: NotificationSeverity.values.map((severity) {
                return ChoiceChip(
                  label: Text(_getSeverityLabel(severity)),
                  selected: _selectedSeverity == severity,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() {
                        _selectedSeverity = severity;
                      });
                    }
                  },
                  selectedColor: _getSeverityColor(severity).withOpacity(0.3),
                  labelStyle: TextStyle(
                    color: _selectedSeverity == severity ? Colors.white : Colors.grey,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 32),

            // 전송 버튼
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isSending ? null : _sendMessage,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[700],
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: _isSending
                    ? const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          ),
                          SizedBox(width: 8),
                          Text('전송 중...'),
                        ],
                      )
                    : const Text(
                        '메시지 전송',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getKindLabel(NotificationKind kind) {
    switch (kind) {
      case NotificationKind.system:
        return '시스템';
      case NotificationKind.schedule:
        return '일정';
      case NotificationKind.info:
        return '정보';
      case NotificationKind.contact:
        return '연락';
      case NotificationKind.marketing:
        return '마케팅';
      case NotificationKind.inbound:
        return '메시지';
    }
  }

  String _getSeverityLabel(NotificationSeverity severity) {
    switch (severity) {
      case NotificationSeverity.green:
        return '정상';
      case NotificationSeverity.blue:
        return '일반';
      case NotificationSeverity.yellow:
        return '주의';
      case NotificationSeverity.orange:
        return '고위험';
      case NotificationSeverity.red:
        return '위급';
    }
  }

  Color _getSeverityColor(NotificationSeverity severity) {
    switch (severity) {
      case NotificationSeverity.green:
        return Colors.green;
      case NotificationSeverity.blue:
        return Colors.blue;
      case NotificationSeverity.yellow:
        return Colors.yellow;
      case NotificationSeverity.orange:
        return Colors.orange;
      case NotificationSeverity.red:
        return Colors.red;
    }
  }

  Future<void> _sendMessage() async {
    if (_titleController.text.trim().isEmpty) {
      _showErrorDialog('제목을 입력해주세요.');
      return;
    }

    if (_bodyController.text.trim().isEmpty) {
      _showErrorDialog('내용을 입력해주세요.');
      return;
    }

    final recipientsText = _recipientsController.text.trim();
    if (recipientsText.isEmpty) {
      _showErrorDialog('수신자를 입력해주세요.');
      return;
    }

    final recipients = recipientsText
        .split(',')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    if (recipients.isEmpty) {
      _showErrorDialog('올바른 수신자를 입력해주세요.');
      return;
    }

    setState(() {
      _isSending = true;
    });

    try {
      final success = await context.read<NotificationProvider>().sendNotification(
        recipients: recipients,
        title: _titleController.text.trim(),
        body: _bodyController.text.trim(),
        kind: _selectedKind,
        severity: _selectedSeverity,
      );

      if (success) {
        _showSuccessDialog();
        _clearForm();
      } else {
        _showErrorDialog('메시지 전송에 실패했습니다.');
      }
    } catch (e) {
      _showErrorDialog('오류가 발생했습니다: $e');
    } finally {
      setState(() {
        _isSending = false;
      });
    }
  }

  void _clearForm() {
    _titleController.clear();
    _bodyController.clear();
    _recipientsController.clear();
    setState(() {
      _selectedKind = NotificationKind.info;
      _selectedSeverity = NotificationSeverity.blue;
    });
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green),
            SizedBox(width: 8),
            Text(
              '전송 완료',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
        content: const Text(
          '메시지가 성공적으로 전송되었습니다.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Row(
          children: [
            Icon(Icons.error, color: Colors.red),
            SizedBox(width: 8),
            Text(
              '오류',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
        content: Text(
          message,
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }
}
