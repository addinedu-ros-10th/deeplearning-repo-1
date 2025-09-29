import 'package:flutter/foundation.dart';
import '../models/auth_models.dart';
import '../service/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  AuthProvider() {
    _checkStoredLogin();
  }

  final AuthService _authService = AuthService();
  AuthState _state = AuthState.initial();

  AuthState get state => _state;

  bool get isLoggedIn => _state.isLoggedIn;
  bool get isLoading => _state.isLoading;
  String get userId => _state.userId;
  String get userName => _state.userName;
  String get errorMessage => _state.errorMessage;

  /// 저장된 로그인 정보 확인
  Future<void> _checkStoredLogin() async {
    _updateState(_state.copyWith(isLoading: true));
    
    final storedState = await _authService.checkStoredLogin();
    _updateState(storedState);
  }

  /// 로그인
  Future<void> login({
    required String password,
    required bool rememberMe,
    required bool autoLogin,
  }) async {
    _updateState(_state.copyWith(isLoading: true, errorMessage: ''));
    
    final response = await _authService.login(
      password: password,
      rememberMe: rememberMe,
      autoLogin: autoLogin,
    );

    if (response.success) {
      _updateState(AuthState(
        isLoggedIn: true,
        isLoading: false,
        userId: response.userId,
        userName: response.userName,
        rememberMe: rememberMe,
        autoLogin: autoLogin,
        errorMessage: '',
      ));
    } else {
      _updateState(_state.copyWith(
        isLoading: false,
        errorMessage: response.message,
      ));
    }
  }

  /// 로그아웃
  Future<void> logout() async {
    await _authService.logout();
    _updateState(AuthState.initial());
  }

  /// 상태 업데이트
  void _updateState(AuthState newState) {
    _state = newState;
    notifyListeners();
  }
}
