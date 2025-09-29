import 'package:shared_preferences/shared_preferences.dart';
import 'package:logging/logging.dart';
import '../models/auth_models.dart';
import '../../users/service/users_service.dart';

class AuthService {
  AuthService._internal();
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;

  static final Logger _logger = Logger('AuthService');
  final UsersService _usersService = UsersService();

  static const String _keyIsLoggedIn = 'is_logged_in';
  static const String _keyUserId = 'user_id';
  static const String _keyUserName = 'user_name';
  static const String _keyRememberMe = 'remember_me';
  static const String _keyAutoLogin = 'auto_login';

  /// 로그인 (첫 번째 사용자로 자동 로그인)
  Future<LoginResponse> login({
    required String password,
    required bool rememberMe,
    required bool autoLogin,
  }) async {
    try {
      _logger.info('Attempting login with password: $password');
      
      // 첫 번째 사용자 정보 가져오기
      final usersResponse = await _usersService.getUsersList(
        page: 1,
        size: 1,
        role: 'care_target',
      );

      if (usersResponse.users.isEmpty) {
        return const LoginResponse(
          success: false,
          message: '사용자를 찾을 수 없습니다.',
          userId: '',
          userName: '',
        );
      }

      final firstUser = usersResponse.users.first;
      
      // 비밀번호 검증 (임시로 1234)
      if (password != '1234') {
        return const LoginResponse(
          success: false,
          message: '비밀번호가 올바르지 않습니다.',
          userId: '',
          userName: '',
        );
      }

      // 로그인 성공 시 정보 저장
      if (rememberMe || autoLogin) {
        await _saveLoginInfo(
          userId: firstUser.userId,
          userName: firstUser.userName,
          rememberMe: rememberMe,
          autoLogin: autoLogin,
        );
      }

      _logger.info('Login successful for user: ${firstUser.userName}');
      
      return LoginResponse(
        success: true,
        message: '로그인 성공',
        userId: firstUser.userId,
        userName: firstUser.userName,
      );
    } catch (e) {
      _logger.severe('Login error: $e');
      return LoginResponse(
        success: false,
        message: '로그인 중 오류가 발생했습니다: $e',
        userId: '',
        userName: '',
      );
    }
  }

  /// 저장된 로그인 정보 확인
  Future<AuthState> checkStoredLogin() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      final isLoggedIn = prefs.getBool(_keyIsLoggedIn) ?? false;
      final userId = prefs.getString(_keyUserId) ?? '';
      final userName = prefs.getString(_keyUserName) ?? '';
      final rememberMe = prefs.getBool(_keyRememberMe) ?? false;
      final autoLogin = prefs.getBool(_keyAutoLogin) ?? false;

      if (isLoggedIn && userId.isNotEmpty) {
        _logger.info('Found stored login for user: $userName');
        return AuthState(
          isLoggedIn: true,
          isLoading: false,
          userId: userId,
          userName: userName,
          rememberMe: rememberMe,
          autoLogin: autoLogin,
          errorMessage: '',
        );
      }

      return AuthState.initial();
    } catch (e) {
      _logger.severe('Error checking stored login: $e');
      return AuthState.initial();
    }
  }

  /// 로그인 정보 저장
  Future<void> _saveLoginInfo({
    required String userId,
    required String userName,
    required bool rememberMe,
    required bool autoLogin,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_keyIsLoggedIn, true);
      await prefs.setString(_keyUserId, userId);
      await prefs.setString(_keyUserName, userName);
      await prefs.setBool(_keyRememberMe, rememberMe);
      await prefs.setBool(_keyAutoLogin, autoLogin);
      
      _logger.info('Login info saved for user: $userName');
    } catch (e) {
      _logger.severe('Error saving login info: $e');
    }
  }

  /// 로그아웃
  Future<void> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_keyIsLoggedIn);
      await prefs.remove(_keyUserId);
      await prefs.remove(_keyUserName);
      await prefs.remove(_keyRememberMe);
      await prefs.remove(_keyAutoLogin);
      
      _logger.info('User logged out');
    } catch (e) {
      _logger.severe('Error during logout: $e');
    }
  }
}
