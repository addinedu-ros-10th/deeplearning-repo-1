import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../state/auth_provider.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _passwordController = TextEditingController(text: '1234');
  bool _rememberMe = false;
  bool _autoLogin = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadLoginOptions();
  }

  @override
  void dispose() {
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _loadLoginOptions() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _rememberMe = prefs.getBool('remember_me') ?? false;
      _autoLogin = prefs.getBool('auto_login') ?? false;
    });
  }

  Future<void> _saveLoginOptions() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('remember_me', _rememberMe);
    await prefs.setBool('auto_login', _autoLogin);
  }

  Future<void> _handleLogin() async {
    if (_passwordController.text.isEmpty) {
      _showErrorDialog('비밀번호를 입력해주세요.');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    await context.read<AuthProvider>().login(
      password: _passwordController.text,
      rememberMe: _rememberMe,
      autoLogin: _autoLogin,
    );

    setState(() {
      _isLoading = false;
    });

    if (mounted) {
      if (context.read<AuthProvider>().isLoggedIn) {
        // 로그인 성공 시 옵션 값 저장
        await _saveLoginOptions();
        // 음성 인터페이스로 이동
        context.go('/voice');
      } else {
        _showErrorDialog(context.read<AuthProvider>().errorMessage);
      }
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Text(
          '로그인 실패',
          style: TextStyle(color: Colors.white),
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 앱 로고/제목
              const Icon(
                Icons.mic,
                size: 80,
                color: Colors.white,
              ),
              const SizedBox(height: 24),
              const Text(
                '음성 인터페이스',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '돌봄 서비스',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 48),

              // 비밀번호 입력
              Container(
                decoration: BoxDecoration(
                  color: Colors.grey[900],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white, fontSize: 18),
                  decoration: const InputDecoration(
                    hintText: '비밀번호 (기본: 1234)',
                    hintStyle: TextStyle(color: Colors.grey),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.all(20),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // 옵션 체크박스
              Row(
                children: [
                  Checkbox(
                    value: _rememberMe,
                    onChanged: (value) async {
                      setState(() {
                        _rememberMe = value ?? false;
                      });
                      await _saveLoginOptions();
                    },
                    activeColor: Colors.blue,
                  ),
                  const Text(
                    '로그인 정보 기억하기',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ],
              ),
              Row(
                children: [
                  Checkbox(
                    value: _autoLogin,
                    onChanged: (value) async {
                      setState(() {
                        _autoLogin = value ?? false;
                      });
                      await _saveLoginOptions();
                    },
                    activeColor: Colors.blue,
                  ),
                  const Text(
                    '자동 로그인',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ],
              ),
              const SizedBox(height: 32),

              // 로그인 버튼
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[700],
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          '로그인',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
              const SizedBox(height: 16),

              // 안내 텍스트
              const Text(
                '첫 번째 사용자로 자동 로그인됩니다',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
