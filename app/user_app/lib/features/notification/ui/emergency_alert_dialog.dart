import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:async';

/// 긴급 알림 다이얼로그
/// 위기 단계 5단계 (낙상 등 심각한 상황) 알림을 표시하는 다이얼로그
class EmergencyAlertDialog extends StatefulWidget {
  final String title;
  final String message;
  final VoidCallback? onConfirm;
  final VoidCallback? onCancel;

  const EmergencyAlertDialog({
    Key? key,
    required this.title,
    required this.message,
    this.onConfirm,
    this.onCancel,
  }) : super(key: key);

  @override
  State<EmergencyAlertDialog> createState() => _EmergencyAlertDialogState();
}

class _EmergencyAlertDialogState extends State<EmergencyAlertDialog>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _shakeController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _shakeAnimation;
  
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isPlaying = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _playEmergencySound();
    _startVibration();
  }

  void _initializeAnimations() {
    // 펄스 애니메이션 (빨간색 깜빡임)
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // 흔들림 애니메이션
    _shakeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _shakeAnimation = Tween<double>(
      begin: -10.0,
      end: 10.0,
    ).animate(CurvedAnimation(
      parent: _shakeController,
      curve: Curves.elasticIn,
    ));

    // 애니메이션 시작
    _pulseController.repeat(reverse: true);
    _shakeController.repeat(reverse: true);
  }

  Future<void> _playEmergencySound() async {
    try {
      if (!_isPlaying) {
        setState(() {
          _isPlaying = true;
        });
        
        // 긴급 알림음 재생 (실제로는 서버에서 받은 오디오 파일 사용)
        await _audioPlayer.play(AssetSource('sounds/emergency_alert.wav'));
        
        // 3초마다 반복 재생
        Timer.periodic(const Duration(seconds: 3), (timer) {
          if (mounted) {
            _audioPlayer.play(AssetSource('sounds/emergency_alert.wav'));
          } else {
            timer.cancel();
          }
        });
      }
    } catch (e) {
      print('긴급 알림음 재생 오류: $e');
    }
  }

  void _startVibration() {
    // 진동 패턴: 긴 진동 - 짧은 진동 - 긴 진동
    HapticFeedback.heavyImpact();
    
    Timer.periodic(const Duration(seconds: 2), (timer) {
      if (mounted) {
        HapticFeedback.heavyImpact();
      } else {
        timer.cancel();
      }
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _shakeController.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async => false, // 뒤로가기 비활성화
      child: Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(20),
        child: Container(
          width: double.infinity,
          height: double.infinity,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.red[900]!.withOpacity(0.9),
                Colors.red[800]!.withOpacity(0.8),
                Colors.black.withOpacity(0.9),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.red[400]!,
              width: 3,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.red.withOpacity(0.5),
                blurRadius: 30,
                spreadRadius: 10,
              ),
            ],
          ),
          child: Stack(
            children: [
              // 배경 펄스 효과
              AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _pulseAnimation.value,
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  );
                },
              ),
              
              // 메인 컨텐츠
              Padding(
                padding: const EdgeInsets.all(30),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 위험 아이콘
                    AnimatedBuilder(
                      animation: _shakeAnimation,
                      builder: (context, child) {
                        return Transform.translate(
                          offset: Offset(_shakeAnimation.value, 0),
                          child: Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.red[600],
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.red.withOpacity(0.8),
                                  blurRadius: 20,
                                  spreadRadius: 5,
                                ),
                              ],
                            ),
                            child: const Icon(
                              Icons.warning,
                              color: Colors.white,
                              size: 60,
                            ),
                          ),
                        );
                      },
                    ),
                    
                    const SizedBox(height: 30),
                    
                    // 제목
                    Text(
                      widget.title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        shadows: [
                          Shadow(
                            color: Colors.black,
                            blurRadius: 10,
                            offset: Offset(2, 2),
                          ),
                        ],
                      ),
                      textAlign: TextAlign.center,
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // 메시지
                    Text(
                      widget.message,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        height: 1.5,
                        shadows: [
                          Shadow(
                            color: Colors.black,
                            blurRadius: 5,
                            offset: Offset(1, 1),
                          ),
                        ],
                      ),
                      textAlign: TextAlign.center,
                    ),
                    
                    const SizedBox(height: 50),
                    
                    // 사용자 의식 확인 버튼
                    _buildConfirmButton(),
                    
                    const SizedBox(height: 30),
                    
                    // 취소 버튼 (작게)
                    _buildCancelButton(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildConfirmButton() {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _pulseAnimation.value * 0.1 + 0.9, // 펄스 효과 적용
          child: Container(
            width: 280,
            height: 80,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.green[600]!,
                  Colors.green[700]!,
                ],
              ),
              borderRadius: BorderRadius.circular(40),
              boxShadow: [
                BoxShadow(
                  color: Colors.green.withOpacity(0.6),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () {
                  // 진동 피드백
                  HapticFeedback.heavyImpact();
                  
                  // 알림음 중지
                  _audioPlayer.stop();
                  
                  // 애니메이션 중지
                  _pulseController.stop();
                  _shakeController.stop();
                  
                  // 콜백 실행
                  widget.onConfirm?.call();
                  
                  // 다이얼로그 닫기
                  Navigator.of(context).pop();
                },
                borderRadius: BorderRadius.circular(40),
                child: Center(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.check_circle,
                        color: Colors.white,
                        size: 30,
                      ),
                      const SizedBox(width: 15),
                      const Text(
                        '사용자 의식 있음 확인',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildCancelButton() {
    return Container(
      width: 200,
      height: 50,
      decoration: BoxDecoration(
        color: Colors.grey[800]!.withOpacity(0.7),
        borderRadius: BorderRadius.circular(25),
        border: Border.all(
          color: Colors.grey[600]!,
          width: 1,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            // 진동 피드백
            HapticFeedback.lightImpact();
            
            // 알림음 중지
            _audioPlayer.stop();
            
            // 애니메이션 중지
            _pulseController.stop();
            _shakeController.stop();
            
            // 콜백 실행
            widget.onCancel?.call();
            
            // 다이얼로그 닫기
            Navigator.of(context).pop();
          },
          borderRadius: BorderRadius.circular(25),
          child: const Center(
            child: Text(
              '나중에 확인',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// 긴급 알림 다이얼로그 표시 함수
Future<void> showEmergencyAlertDialog(
  BuildContext context, {
  required String title,
  required String message,
  VoidCallback? onConfirm,
  VoidCallback? onCancel,
}) {
  return showDialog<void>(
    context: context,
    barrierDismissible: false, // 외부 터치로 닫기 비활성화
    builder: (BuildContext context) {
      return EmergencyAlertDialog(
        title: title,
        message: message,
        onConfirm: onConfirm,
        onCancel: onCancel,
      );
    },
  );
}
