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
    )..repeat();
    
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

  void _initSpeech() async {
    _speechEnabled = await _speechToText.initialize();
    setState(() {});
  }

  @override
  void dispose() {
    _waveController.dispose();
    _buttonController.dispose();
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
        
        // 실시간으로 사용자 메시지 업데이트
        if (result.recognizedWords.isNotEmpty) {
          _updateRealtimeMessage(result.recognizedWords);
          
          // 음성 인식이 완료되면 즉시 처리
          if (result.finalResult) {
            _processVoiceInput(result.recognizedWords);
          } else {
            // 실시간으로도 AI 응답 요청 (중복 방지를 위해 타이머 사용)
            _scheduleVoiceProcessing(result.recognizedWords);
          }
        }
      },
    );
  }

  void _stopListening() async {
    setState(() {
      _isVoiceInputActive = false;
    });
    
    await _speechToText.stop();
    
    // 타이머 정리
    _voiceProcessingTimer?.cancel();
    
    // 마지막으로 인식된 텍스트가 있으면 처리
    if (_lastWords.trim().isNotEmpty) {
      _processVoiceInput(_lastWords);
    }
  }

  void _updateRealtimeMessage(String text) {
    setState(() {
      // 실시간 메시지가 이미 있는지 확인
      if (_messages.isNotEmpty && _messages.last.isUser) {
        // 마지막 사용자 메시지를 업데이트
        _messages[_messages.length - 1] = ChatMessage.user(text);
      } else {
        // 새로운 실시간 메시지 추가
        _messages.add(ChatMessage.user(text));
      }
    });
    _scrollToBottom();
  }

  void _scheduleVoiceProcessing(String text) {
    // 기존 타이머 취소
    _voiceProcessingTimer?.cancel();
    
    // 1.5초 후에 AI 응답 요청 (중복 방지)
    _voiceProcessingTimer = Timer(const Duration(milliseconds: 1500), () {
      if (_isVoiceInputActive && text.trim().isNotEmpty) {
        _processVoiceInput(text);
      }
    });
  }

  void _processVoiceInput(String text) async {
    if (text.trim().isEmpty) return;
    
    // 중복 처리를 방지하기 위한 플래그 확인
    if (_isProcessingVoiceInput) return;
    _isProcessingVoiceInput = true;
    
    // 실시간 메시지를 최종 메시지로 확정
    if (_messages.isNotEmpty && _messages.last.isUser) {
      setState(() {
        _messages[_messages.length - 1] = ChatMessage.user(text);
      });
    } else {
      // 사용자 메시지 추가
      final userMessage = ChatMessage.user(text);
      setState(() {
        _messages.add(userMessage);
      });
    }
    
    _scrollToBottom();
    
    // AI 응답 생성
    final aiMessage = ChatMessage.ai('', isLoading: true);
    setState(() {
      _messages.add(aiMessage);
    });
    
    _scrollToBottom();
    
    try {
      final response = await _openAiService.chat(text);
      
      // 로딩 메시지를 실제 응답으로 교체
      setState(() {
        _messages.removeLast();
        _messages.add(ChatMessage.ai(response));
      });
      
      _scrollToBottom();
      
      // TTS로 응답 재생
      _playTtsResponse(response);
    } catch (e) {
      setState(() {
        _messages.removeLast();
        _messages.add(ChatMessage.ai('죄송합니다. 응답을 생성하는 중 오류가 발생했습니다.'));
      });
      
      _scrollToBottom();
    } finally {
      _isProcessingVoiceInput = false;
    }
  }

  void _scrollToBottom() {
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

  void _onMenuButtonPress() {
    setState(() {
      _showMenuButtons = true;
    });
  }

  void _onBackgroundTap() {
    setState(() {
      _showMenuButtons = false;
      if (_isVoiceInputActive) {
        _stopListening();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
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
                  
                ],
              ),
            ),
            
            // 중앙 음성 입력 버튼
            _buildCenterVoiceButton(),
            
            // 채팅 영역
            _buildChatArea(),
            
            // 메뉴 버튼들 (오버레이) - 채팅 영역 위에 배치
            if (_showMenuButtons) _buildMenuOverlay(),
            
            // 우측 하단 메뉴 버튼 (최상단)
            _buildMenuButton(),
          ],
        ),
      ),
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
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          CircleAvatar(
            radius: 25,
            backgroundColor: Colors.blue[700],
            child: const Icon(
              Icons.person,
              color: Colors.white,
              size: 30,
            ),
          ),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '돌봄대상자',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '음성 인터페이스 활성화',
                  style: TextStyle(
                    color: Colors.grey,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          Row(
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
      right: 20,
      bottom: 20,
      child: GestureDetector(
        onTap: _onMenuButtonPress,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: _showMenuButtons ? 80 : 60,
          height: _showMenuButtons ? 80 : 60,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: _showMenuButtons ? Colors.red[600] : Colors.white,
            boxShadow: [
              BoxShadow(
                color: (_showMenuButtons ? Colors.red : Colors.grey).withOpacity(0.3),
                blurRadius: 10,
                spreadRadius: 2,
              ),
            ],
          ),
          child: Icon(
            _showMenuButtons ? Icons.emergency : Icons.menu,
            color: _showMenuButtons ? Colors.white : Colors.grey[800],
            size: _showMenuButtons ? 40 : 30,
          ),
        ),
      ),
    );
  }

  Widget _buildMenuOverlay() {
    return Positioned(
      right: 20,
      bottom: 120, // 메뉴 버튼과 겹치지 않도록 조정
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.5),
              blurRadius: 15,
              spreadRadius: 3,
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildMenuOptionButton(
              icon: Icons.search,
              label: '나의 소지품 찾기',
              onTap: () {
                print('소지품 찾기 버튼 클릭됨');
                setState(() {
                  _showMenuButtons = false;
                });
                context.push('/items');
              },
            ),
            const SizedBox(height: 8),
            _buildMenuOptionButton(
              icon: Icons.message,
              label: '메시지',
              onTap: () {
                print('메시지 버튼 클릭됨');
                setState(() {
                  _showMenuButtons = false;
                });
                context.push('/messages');
              },
            ),
            const SizedBox(height: 8),
            _buildMenuOptionButton(
              icon: Icons.emergency,
              label: '긴급/응급 신고',
              onTap: () {
                print('긴급신고 버튼 클릭됨');
                setState(() {
                  _showMenuButtons = false;
                });
                context.push('/emergency');
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuOptionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: () {
        print('메뉴 옵션 버튼 터치됨: $label');
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: Colors.grey[800],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: Colors.grey[600]!,
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.white, size: 24),
            const SizedBox(width: 12),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChatArea() {
    return Positioned(
      left: 0,
      right: 0,
      bottom: 0,
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.transparent,
              Colors.black.withOpacity(0.3),
              Colors.black.withOpacity(0.6),
              Colors.black.withOpacity(0.8),
              Colors.black.withOpacity(0.95),
            ],
            stops: const [0.0, 0.3, 0.6, 0.8, 1.0],
          ),
        ),
        child: Stack(
          children: [
            // Fadeout 효과를 위한 오버레이
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              height: 30,
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.black.withOpacity(0.8),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),
            // 채팅 메시지 리스트 또는 빈 상태 메시지
            _messages.isEmpty 
                ? _buildEmptyChatState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.only(top: 20, bottom: 10),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      return ChatBubble(message: _messages[index]);
                    },
                  ),
          ],
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