import 'package:dio/dio.dart';
import 'package:logging/logging.dart';
import '../../../core/net/api_client.dart';
import '../models/user_models.dart';

class UsersService {
  UsersService._internal();
  static final UsersService _instance = UsersService._internal();
  factory UsersService() => _instance;

  static final Logger _logger = Logger('UsersService');
  final ApiClient _apiClient = ApiClient();

  /// 사용자 목록 조회 (care_target 역할)
  Future<UsersListResponse> getUsersList({
    int page = 1,
    int size = 100,
    String role = 'care_target',
  }) async {
    try {
      _logger.info('Fetching users list: page=$page, size=$size, role=$role');
      
      final response = await _apiClient.client.get(
        '/api/users/list',
        queryParameters: {
          'page': page,
          'size': size,
          'role': role,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        return UsersListResponse.fromJson(data);
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          message: 'Failed to fetch users list: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      _logger.severe('Error fetching users list: ${e.message}');
      rethrow;
    } catch (e) {
      _logger.severe('Unexpected error fetching users list: $e');
      throw Exception('Failed to fetch users list: $e');
    }
  }

  /// 특정 사용자 프로필 조회
  Future<UserProfile> getUserProfile(String userId) async {
    try {
      _logger.info('Fetching user profile for: $userId');
      
      final response = await _apiClient.client.get(
        '/api/user-profiles/$userId',
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        return UserProfile.fromJson(data);
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          message: 'Failed to fetch user profile: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      _logger.severe('Error fetching user profile: ${e.message}');
      rethrow;
    } catch (e) {
      _logger.severe('Unexpected error fetching user profile: $e');
      throw Exception('Failed to fetch user profile: $e');
    }
  }

  /// 사용자의 관계자 목록 조회
  Future<List<UserRelationship>> getUserRelationships(String userId) async {
    try {
      _logger.info('Fetching user relationships for: $userId');
      
      final response = await _apiClient.client.get(
        '/api/user-relationships/user/$userId/as-target',
      );

      if (response.statusCode == 200) {
        final data = response.data as List<dynamic>;
        return data
            .map((item) => UserRelationship.fromJson(item as Map<String, dynamic>))
            .toList();
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          message: 'Failed to fetch user relationships: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      _logger.severe('Error fetching user relationships: ${e.message}');
      rethrow;
    } catch (e) {
      _logger.severe('Unexpected error fetching user relationships: $e');
      throw Exception('Failed to fetch user relationships: $e');
    }
  }
}
