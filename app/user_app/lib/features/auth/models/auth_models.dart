import 'package:meta/meta.dart';

@immutable
class LoginRequest {
  const LoginRequest({
    required this.userId,
    required this.password,
    required this.rememberMe,
    required this.autoLogin,
  });

  final String userId;
  final String password;
  final bool rememberMe;
  final bool autoLogin;

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'password': password,
      'remember_me': rememberMe,
      'auto_login': autoLogin,
    };
  }
}

@immutable
class LoginResponse {
  const LoginResponse({
    required this.success,
    required this.message,
    required this.userId,
    required this.userName,
  });

  final bool success;
  final String message;
  final String userId;
  final String userName;

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      success: json['success'] as bool? ?? false,
      message: json['message'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      userName: json['user_name'] as String? ?? '',
    );
  }
}

@immutable
class AuthState {
  const AuthState({
    required this.isLoggedIn,
    required this.isLoading,
    required this.userId,
    required this.userName,
    required this.rememberMe,
    required this.autoLogin,
    required this.errorMessage,
  });

  final bool isLoggedIn;
  final bool isLoading;
  final String userId;
  final String userName;
  final bool rememberMe;
  final bool autoLogin;
  final String errorMessage;

  AuthState copyWith({
    bool? isLoggedIn,
    bool? isLoading,
    String? userId,
    String? userName,
    bool? rememberMe,
    bool? autoLogin,
    String? errorMessage,
  }) {
    return AuthState(
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      isLoading: isLoading ?? this.isLoading,
      userId: userId ?? this.userId,
      userName: userName ?? this.userName,
      rememberMe: rememberMe ?? this.rememberMe,
      autoLogin: autoLogin ?? this.autoLogin,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  factory AuthState.initial() {
    return const AuthState(
      isLoggedIn: false,
      isLoading: false,
      userId: '',
      userName: '',
      rememberMe: false,
      autoLogin: false,
      errorMessage: '',
    );
  }
}
