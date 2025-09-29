import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;
import 'dart:async';
import '../../auth/state/auth_provider.dart';
import '../../chat/models/chat_models.dart';
import '../../chat/ui/chat_bubble.dart';
import '../service/openai_service.dart';
import '../service/flutter_tts_service.dart';
import 'tts_settings_page.dart';
import '../../notification/state/notification_provider.dart';
import '../../notification/ui/notification_badge.dart';
import '../../notification/ui/notification_dialog.dart';
import '../../notification/models/notification_models.dart';

class VoiceInterfacePage extends StatefulWidget {
  const VoiceInterfacePage({super.key});

  @override
  State<VoiceInterfacePage> createState() => _VoiceInterfacePageState();
}

class _VoiceInterfacePageState extends State<VoiceInterfacePage>
    with TickerProviderStateMixin {
  late AnimationController _waveController;
  late AnimationController _buttonController;
  late Animation<double> _waveAnimation;
  late Animation<double> _buttonAnimation;

  bool _isButtonPressed = false;
  bool _showMenuButtons = false;
  bool _isVoiceInputActive = false;
  bool _isProcessingVoiceInput = false;
  bool _isTtsPlaying = false;
  Timer? _buttonHoldTimer;
  Timer? _voiceProcessingTimer;
  
  final SpeechToText _speechToText = SpeechToText();
  final OpenAiService _openAiService = OpenAiService();
  final FlutterTtsService _ttsService = FlutterTtsService();
  bool _speechEnabled = false;
  String _lastWords = '';
  List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    
    // 음파 애니메이션
    _waveController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _waveAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _waveController,
      curve: Curves.easeInOut,
    ));

    // 버튼 애니메이션
    _buttonController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _buttonAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _buttonController,
      curve: Curves.easeInOut,
    ));

    // STT 초기화
    _initSpeech();
    
    // TTS 콜백 설정
    _ttsService.setCallbacks(
      onComplete: () {
        print('TTS 재생 완료 - STT 활성화');
        setState(() {
          _isTtsPlaying = false;
        });
      },
      onError: () {
        print('TTS 재생 오류 - STT 활성화');
        setState(() {
          _isTtsPlaying = false;
        });
      },
    );
    
    // 알림 연결 초기화
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initNotifications();
    });
  }

  void _initNotifications() {
    final authProvider = context.read<AuthProvider>();
    if (authProvider.isLoggedIn && authProvider.userId != null) {
      context.read<NotificationProvider>().connect(authProvider.userId!);
    }
  }

  // 알림 다이얼로그 표시
  void _showNotificationDialog(NotificationMessage message) {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return NotificationDialog(
          message: message,
          onClose: () {
            Navigator.of(context).pop();
          },
          onViewDetails: () {
            Navigator.of(context).pop();
            // 알림 목록 페이지로 이동
            context.push('/notifications');
          },
        );
      },
    );
  }

  void _initSpeech() async {
    _speechEnabled = await _speechToText.initialize();
    setState(() {});
  }

  @override
  void dispose() {
    _waveController.dispose();
    _buttonController.dispose();
    _speechToText.stop();
    _ttsService.dispose();
    _scrollController.dispose();
    _buttonHoldTimer?.cancel();
    _voiceProcessingTimer?.cancel();
    super.dispose();
  }

  void _onVoiceButtonPress() {
    if (_isTtsPlaying) {
      print('TTS 재생 중 - 음성 입력 비활성화');
      return; // TTS 재생 중에는 음성 입력 비활성화
    }
    
    if (_isVoiceInputActive) {
      _stopListening();
    } else {
      _startListening();
    }
  }

  void _startListening() async {
    if (!_speechEnabled || _isTtsPlaying) {
      print('STT 시작 실패 - speechEnabled: $_speechEnabled, isTtsPlaying: $_isTtsPlaying');
      return;
    }
    
    setState(() {
      _isVoiceInputActive = true;
    });
    
    await _speechToText.listen(
      onResult: (result) {
        setState(() {
          _lastWords = result.recognizedWords;
        });
        
        // 실시간으로 메시지 업데이트
        _updateRealtimeMessage(result.recognizedWords);
        
        // 최종 결과가 나왔을 때 AI 응답 요청
        if (result.finalResult) {
          _processVoiceInput(result.recognizedWords);
        } else {
          // 실시간 처리 (중간 결과)
          _scheduleVoiceProcessing(result.recognizedWords);
        }
      },
    );
  }

  void _scheduleVoiceProcessing(String text) {
    _voiceProcessingTimer?.cancel();
    _voiceProcessingTimer = Timer(const Duration(milliseconds: 1000), () {
      if (!_isProcessingVoiceInput && text.isNotEmpty) {
        _processVoiceInput(text);
      }
    });
  }

  void _updateRealtimeMessage(String text) {
    if (text.isNotEmpty) {
      // 기존 실시간 메시지가 있으면 업데이트, 없으면 새로 추가
      if (_messages.isNotEmpty && _messages.last.isLoading) {
        _messages.last = ChatMessage(
          id: _messages.last.id,
          text: text,
          isUser: true,
          timestamp: DateTime.now(),
          isLoading: false,
        );
      } else {
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: text,
          isUser: true,
          timestamp: DateTime.now(),
          isLoading: false,
        ));
      }
      
      // 스크롤을 맨 아래로
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  void _processVoiceInput(String text) async {
    if (_isProcessingVoiceInput || text.isEmpty) return;
    
    setState(() {
      _isProcessingVoiceInput = true;
    });

    try {
      // AI 응답 요청
      final response = await _openAiService.chat(text);
      
      if (response != null && response.isNotEmpty) {
        // AI 응답을 메시지에 추가
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: response,
          isUser: false,
          timestamp: DateTime.now(),
          isLoading: false,
        ));
        
        // TTS로 응답 재생
        await _playTtsResponse(response);
      }
    } catch (e) {
      print('AI 응답 오류: $e');
    } finally {
      setState(() {
        _isProcessingVoiceInput = false;
      });
    }
  }

  void _stopListening() async {
    await _speechToText.stop();
    setState(() {
      _isVoiceInputActive = false;
    });
  }

  void _onBackgroundTap() {
    if (_isVoiceInputActive) {
      _stopListening();
    }
  }

  void _onMenuButtonPress() {
    setState(() {
      _showMenuButtons = !_showMenuButtons;
    });
  }

  Future<void> _playTtsResponse(String text) async {
    try {
      // STT 완전 중지
      if (_isVoiceInputActive) {
        await _speechToText.stop();
        setState(() {
          _isVoiceInputActive = false;
        });
      }
      
      setState(() {
        _isTtsPlaying = true;
      });
      
      print('TTS 시작: $text');
      await _ttsService.speak(text);
      print('TTS Audio playing: $text');

      // TTS 재생 완료는 콜백에서 처리됨
    } catch (e) {
      print('TTS Error: $e');
      setState(() {
        _isTtsPlaying = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<NotificationProvider>(
      builder: (context, notificationProvider, child) {
        // 새 알림이 있으면 다이얼로그 표시
        if (notificationProvider.messages.isNotEmpty) {
          final latestMessage = notificationProvider.messages.first;
          // 다이얼로그가 이미 표시되었는지 확인하는 로직 추가 필요
          WidgetsBinding.instance.addPostFrameCallback((_) {
            _showNotificationDialog(latestMessage);
          });
        }
        
        return Scaffold(
          backgroundColor: Colors.black,
          body: GestureDetector(
            onTap: _onBackgroundTap,
            child: Stack(
              children: [
                // 음파형 배경
                _buildWaveBackground(),
                
                // 메인 컨텐츠
                SafeArea(
                  child: Column(
                    children: [
                      // 상단 사용자 정보
                      _buildUserInfo(),
                      
                      // 중앙 음파 시각화
                      Expanded(
                        child: Center(
                          child: _buildWaveVisualization(),
                        ),
                      ),
                      
                      // 중앙 음성 입력 버튼
                      _buildCenterVoiceButton(),
                      
                      const SizedBox(height: 50),
                    ],
                  ),
                ),
                
                // 메뉴 버튼
                _buildMenuButton(),
                
                // 메뉴 오버레이
                _buildMenuOverlay(),
                
                // 채팅 영역
                _buildChatArea(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildWaveBackground() {
    return AnimatedBuilder(
      animation: _waveAnimation,
      builder: (context, child) {
        return CustomPaint(
          size: Size.infinite,
          painter: WaveBackgroundPainter(_waveAnimation.value),
        );
      },
    );
  }

  Widget _buildUserInfo() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // 알림 버튼
          NotificationBadge(
            onTap: () {
              context.push('/notifications');
            },
            child: IconButton(
              onPressed: () {
                context.push('/notifications');
              },
              icon: const Icon(
                Icons.notifications,
                color: Colors.white,
                size: 28,
              ),
            ),
          ),
          // TTS 설정 버튼
          IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const TtsSettingsPage(),
                ),
              );
            },
            icon: const Icon(
              Icons.settings_voice,
              color: Colors.white,
              size: 28,
            ),
          ),
          // 사용자 정보 버튼
          IconButton(
            onPressed: () {
              final authProvider = context.read<AuthProvider>();
              context.push('/users/${authProvider.userId}');
            },
            icon: const Icon(
              Icons.person,
              color: Colors.white,
              size: 28,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWaveVisualization() {
    return AnimatedBuilder(
      animation: _waveAnimation,
      builder: (context, child) {
        return CustomPaint(
          size: const Size(300, 200),
          painter: WaveVisualizationPainter(_waveAnimation.value),
        );
      },
    );
  }

  Widget _buildCenterVoiceButton() {
    return Center(
      child: GestureDetector(
        onTap: _isTtsPlaying ? null : _onVoiceButtonPress, // TTS 재생 중에는 터치 비활성화
        child: AnimatedBuilder(
          animation: _buttonAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _isVoiceInputActive ? 1.3 : 1.0,
              child: Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _isTtsPlaying 
                      ? Colors.grey[600] // TTS 재생 중에는 회색
                      : _isVoiceInputActive 
                          ? Colors.blue.withOpacity(0.3)
                          : Colors.blue[600],
                  boxShadow: [
                    BoxShadow(
                      color: _isTtsPlaying 
                          ? Colors.grey.withOpacity(0.3)
                          : Colors.blue.withOpacity(0.5),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Icon(
                  _isTtsPlaying 
                      ? Icons.volume_up // TTS 재생 중에는 스피커 아이콘
                      : _isVoiceInputActive 
                          ? Icons.mic 
                          : Icons.mic_none,
                  color: _isTtsPlaying 
                      ? Colors.grey[300] // TTS 재생 중에는 연한 회색
                      : Colors.white,
                  size: 40,
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildMenuButton() {
    return Positioned(
      bottom: 30,
      right: 30,
      child: GestureDetector(
        onTap: _onMenuButtonPress,
        child: AnimatedBuilder(
          animation: _buttonAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _showMenuButtons ? 1.2 : 1.0,
              child: Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _showMenuButtons ? Colors.red[600] : Colors.blue[600],
                  boxShadow: [
                    BoxShadow(
                      color: _showMenuButtons 
                          ? Colors.red.withOpacity(0.5)
                          : Colors.blue.withOpacity(0.5),
                      blurRadius: 15,
                      spreadRadius: 3,
                    ),
                  ],
                ),
                child: Icon(
                  _showMenuButtons ? Icons.close : Icons.menu,
                  color: Colors.white,
                  size: 28,
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildMenuOverlay() {
    if (!_showMenuButtons) return const SizedBox.shrink();
    
    return Positioned(
      bottom: 120,
      right: 30,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildMenuOptionButton(
            '나의 소지품 찾기',
            Icons.search,
            () {
              setState(() {
                _showMenuButtons = false;
              });
              context.push('/items');
            },
          ),
          const SizedBox(height: 8),
          _buildMenuOptionButton(
            '메시지',
            Icons.message,
            () {
              setState(() {
                _showMenuButtons = false;
              });
              context.push('/messages');
            },
          ),
          const SizedBox(height: 8),
          _buildMenuOptionButton(
            '긴급/응급 신고',
            Icons.emergency,
            () {
              setState(() {
                _showMenuButtons = false;
              });
              context.push('/emergency');
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMenuOptionButton(String label, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: () {
        print('메뉴 옵션 버튼 터치됨: $label');
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(25),
          border: Border.all(color: Colors.grey[700]!),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 10,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 12),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChatArea() {
    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      height: 200,
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.black.withOpacity(0.0),
              Colors.black.withOpacity(0.3),
              Colors.black.withOpacity(0.8),
            ],
          ),
        ),
        child: _messages.isEmpty
            ? _buildEmptyChatState()
            : ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  return ChatBubble(message: _messages[index]);
                },
              ),
      ),
    );
  }

  Widget _buildEmptyChatState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            color: Colors.grey[600],
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            '음성 입력 버튼을 눌러 대화를 시작하세요',
            style: TextStyle(
              color: Colors.grey[400],
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '음성 인식이 활성화되면 실시간으로 텍스트가 표시됩니다',
            style: TextStyle(
              color: Colors.grey[500],
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// 음파 배경 페인터
class WaveBackgroundPainter extends CustomPainter {
  final double animationValue;

  WaveBackgroundPainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    final centerY = size.height / 2;
    final waveCount = 3;

    for (int i = 0; i < waveCount; i++) {
      final path = Path();
      final amplitude = 30.0 + (i * 10);
      final frequency = 0.05 + (i * 0.02);
      final phase = (animationValue * 2 * math.pi) + (i * math.pi / 3);

      for (double x = 0; x <= size.width; x += 2) {
        final y = centerY + 
            math.sin((x * frequency) + phase) * amplitude * 
            (1 - (i / waveCount) * 0.3);
        
        if (x == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }

      paint.color = Colors.blue.withOpacity(0.8 - (i * 0.15));
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// 음파 시각화 페인터
class WaveVisualizationPainter extends CustomPainter {
  final double animationValue;

  WaveVisualizationPainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;

    final centerY = size.height / 2;
    final waveCount = 3;

    for (int i = 0; i < waveCount; i++) {
      final path = Path();
      final amplitude = 30.0 + (i * 10);
      final frequency = 0.05 + (i * 0.02);
      final phase = (animationValue * 2 * math.pi) + (i * math.pi / 3);

      for (double x = 0; x <= size.width; x += 2) {
        final y = centerY + 
            math.sin((x * frequency) + phase) * amplitude *
            (1 - (i / waveCount) * 0.3);

        if (x == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }

      paint.color = Colors.blue.withOpacity(0.8 - (i * 0.15));
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}