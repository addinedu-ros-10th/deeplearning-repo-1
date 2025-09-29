import 'package:meta/meta.dart';

@immutable
class UserSummary {
  const UserSummary({
    required this.userId,
    required this.userName,
    required this.email,
    required this.phoneNumber,
    required this.userRole,
    required this.createdAt,
  });

  final String userId;
  final String userName;
  final String email;
  final String phoneNumber;
  final String userRole;
  final DateTime createdAt;

  factory UserSummary.fromJson(Map<String, dynamic> json) {
    return UserSummary(
      userId: json['user_id'] as String,
      userName: json['user_name'] as String,
      email: json['email'] as String,
      phoneNumber: json['phone_number'] as String,
      userRole: json['user_role'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

@immutable
class UsersListResponse {
  const UsersListResponse({
    required this.users,
    required this.total,
    required this.page,
    required this.size,
  });

  final List<UserSummary> users;
  final int total;
  final int page;
  final int size;

  factory UsersListResponse.fromJson(Map<String, dynamic> json) {
    final List<dynamic> rawUsers = json['users'] as List<dynamic>? ?? <dynamic>[];
    return UsersListResponse(
      users: rawUsers.map((e) => UserSummary.fromJson(e as Map<String, dynamic>)).toList(),
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      size: json['size'] as int? ?? rawUsers.length,
    );
  }
}

@immutable
class UserProfile {
  const UserProfile({
    required this.userId,
    required this.userName,
    required this.dateOfBirth,
    required this.gender,
    required this.address,
    required this.addressDetail,
    required this.medicalHistory,
    required this.significantNotes,
    required this.currentStatus,
    required this.createdAt,
    required this.updatedAt,
  });

  final String userId;
  final String userName;
  final DateTime dateOfBirth;
  final String gender;
  final String address;
  final String addressDetail;
  final String medicalHistory;
  final String significantNotes;
  final String currentStatus;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['user_id'] as String,
      userName: json['user_name'] as String? ?? 'Unknown User',
      dateOfBirth: DateTime.parse(json['date_of_birth'] as String),
      gender: json['gender'] as String? ?? '',
      address: json['address'] as String? ?? '',
      addressDetail: json['address_detail'] as String? ?? '',
      medicalHistory: json['medical_history'] as String? ?? '',
      significantNotes: json['significant_notes'] as String? ?? '',
      currentStatus: json['current_status'] as String? ?? '',
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}

@immutable
class UserRelationship {
  const UserRelationship({
    required this.subjectUserId,
    required this.targetUserId,
    required this.relationshipType,
    required this.status,
    required this.relationshipId,
    required this.createdAt,
    required this.updatedAt,
  });

  final String subjectUserId;
  final String targetUserId;
  final String relationshipType;
  final String status;
  final String relationshipId;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory UserRelationship.fromJson(Map<String, dynamic> json) {
    return UserRelationship(
      subjectUserId: json['subject_user_id'] as String,
      targetUserId: json['target_user_id'] as String,
      relationshipType: json['relationship_type'] as String,
      status: json['status'] as String,
      relationshipId: json['relationship_id'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}


