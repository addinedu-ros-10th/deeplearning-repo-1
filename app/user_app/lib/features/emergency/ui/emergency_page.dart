import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:vibration/vibration.dart';
import 'dart:async';

class EmergencyPage extends StatefulWidget {
  const EmergencyPage({super.key});

  @override
  State<EmergencyPage> createState() => _EmergencyPageState();
}

class _EmergencyPageState extends State<EmergencyPage>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _shakeController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _shakeAnimation;

  bool _isAlertActive = true;
  Timer? _alertTimer;

  @override
  void initState() {
    super.initState();
    
    // 펄스 애니메이션 (빨간색 깜빡임)
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    )..repeat(reverse: true);
    
    _pulseAnimation = Tween<double>(
      begin: 0.3,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // 흔들림 애니메이션
    _shakeController = AnimationController(
      duration: const Duration(milliseconds: 100),
      vsync: this,
    );

    _shakeAnimation = Tween<double>(
      begin: -5.0,
      end: 5.0,
    ).animate(CurvedAnimation(
      parent: _shakeController,
      curve: Curves.elasticIn,
    ));

    // 진동 및 소리 시작
    _startAlert();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _shakeController.dispose();
    _alertTimer?.cancel();
    super.dispose();
  }

  void _startAlert() {
    // 진동 시작
    _vibrate();
    
    // 주기적으로 진동 반복
    _alertTimer = Timer.periodic(const Duration(seconds: 2), (timer) {
      if (_isAlertActive) {
        _vibrate();
        _shakeController.forward().then((_) {
          _shakeController.reverse();
        });
      }
    });
  }

  void _vibrate() async {
    if (await Vibration.hasVibrator() ?? false) {
      Vibration.vibrate(duration: 1000);
    }
  }

  void _cancelEmergency() {
    setState(() {
      _isAlertActive = false;
    });
    
    _alertTimer?.cancel();
    _pulseController.stop();
    
    // 음성 인터페이스로 돌아가기
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: AnimatedBuilder(
        animation: _pulseAnimation,
        builder: (context, child) {
          return Container(
            decoration: BoxDecoration(
              gradient: RadialGradient(
                colors: [
                  Colors.red.withOpacity(_pulseAnimation.value * 0.3),
                  Colors.black,
                ],
                stops: const [0.0, 1.0],
              ),
            ),
            child: SafeArea(
              child: Column(
                children: [
                  // 상단 상태바
                  Container(
                    padding: const EdgeInsets.all(20),
                    child: Row(
                      children: [
                        Icon(
                          Icons.emergency,
                          color: Colors.red.withOpacity(_pulseAnimation.value),
                          size: 30,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          '긴급신고 접수',
                          style: TextStyle(
                            color: Colors.red.withOpacity(_pulseAnimation.value),
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // 중앙 메시지 영역
                  Expanded(
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // 경고 아이콘
                          AnimatedBuilder(
                            animation: _shakeAnimation,
                            builder: (context, child) {
                              return Transform.translate(
                                offset: Offset(_shakeAnimation.value, 0),
                                child: Icon(
                                  Icons.warning,
                                  color: Colors.red.withOpacity(_pulseAnimation.value),
                                  size: 120,
                                ),
                              );
                            },
                          ),
                          const SizedBox(height: 40),
                          
                          // 메인 메시지
                          Container(
                            padding: const EdgeInsets.all(30),
                            margin: const EdgeInsets.symmetric(horizontal: 20),
                            decoration: BoxDecoration(
                              color: Colors.red.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: Colors.red.withOpacity(_pulseAnimation.value),
                                width: 3,
                              ),
                            ),
                            child: Column(
                              children: [
                                Text(
                                  '긴급/응급 출동 서비스로 신고가 접수됩니다.',
                                  style: TextStyle(
                                    color: Colors.red.withOpacity(_pulseAnimation.value),
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 20),
                                Text(
                                  '원치 않으면 취소를 눌러주세요.',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.9),
                                    fontSize: 18,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  // 하단 취소 버튼
                  Container(
                    padding: const EdgeInsets.all(30),
                    child: Column(
                      children: [
                        // 취소 버튼
                        AnimatedBuilder(
                          animation: _pulseAnimation,
                          builder: (context, child) {
                            return Container(
                              width: double.infinity,
                              height: 80,
                              decoration: BoxDecoration(
                                color: Colors.red.withOpacity(_pulseAnimation.value),
                                borderRadius: BorderRadius.circular(20),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.red.withOpacity(_pulseAnimation.value * 0.5),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ],
                              ),
                              child: Material(
                                color: Colors.transparent,
                                child: InkWell(
                                  onTap: _cancelEmergency,
                                  borderRadius: BorderRadius.circular(20),
                                  child: Center(
                                    child: Text(
                                      '신고 취소',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 28,
                                        fontWeight: FontWeight.bold,
                                        shadows: [
                                          Shadow(
                                            color: Colors.black.withOpacity(0.5),
                                            offset: const Offset(2, 2),
                                            blurRadius: 4,
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                        const SizedBox(height: 20),
                        
                        // 안내 텍스트
                        Text(
                          '실수로 신고하신 경우에만 취소하세요',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.6),
                            fontSize: 14,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
