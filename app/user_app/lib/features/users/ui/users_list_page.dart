import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../models/user_models.dart';
import '../service/users_service.dart';

class UsersListPage extends StatefulWidget {
  const UsersListPage({super.key});

  @override
  State<UsersListPage> createState() => _UsersListPageState();
}

class _UsersListPageState extends State<UsersListPage> {
  final UsersService _usersService = UsersService();
  List<UserSummary> _users = [];
  bool _isLoading = true;
  String? _errorMessage;
  final int _currentPage = 1;
  final int _pageSize = 100;

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  Future<void> _loadUsers() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await _usersService.getUsersList(
        page: _currentPage,
        size: _pageSize,
        role: 'care_target',
      );
      
      setState(() {
        _users = response.users;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '사용자 목록을 불러오는데 실패했습니다: $e';
        _isLoading = false;
      });
    }
  }

  void _navigateToUserDetail(String userId) {
    context.push('/users/$userId');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('돌봄대상자 목록'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white70,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadUsers,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadUsers,
              child: const Text('다시 시도'),
            ),
          ],
        ),
      );
    }

    if (_users.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.people_outline,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              '등록된 돌봄대상자가 없습니다',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _users.length,
      itemBuilder: (context, index) {
        final user = _users[index];
        return _buildUserCard(user);
      },
    );
  }

  Widget _buildUserCard(UserSummary user) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: Colors.grey[900],
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: CircleAvatar(
          backgroundColor: Colors.blue[700],
          child: Text(
            user.userName.substring(user.userName.length - 1),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          user.userName,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w500,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              user.email,
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 2),
            Text(
              user.phoneNumber,
              style: const TextStyle(color: Colors.grey),
            ),
          ],
        ),
        trailing: const Icon(
          Icons.arrow_forward_ios,
          color: Colors.grey,
          size: 16,
        ),
        onTap: () => _showUserProfileDialog(user),
      ),
    );
  }

  void _showUserProfileDialog(UserSummary user) async {
    // 로딩 다이얼로그 표시
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        content: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: Colors.blue),
            SizedBox(width: 16),
            Text(
              '사용자 정보를 불러오는 중...',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
    );

    try {
      // 사용자의 프로필 정보 조회
      final profile = await UsersService().getUserProfile(user.userId);
      
      // 로딩 다이얼로그 닫기
      Navigator.of(context).pop();
      
      // 프로필 정보 다이얼로그 표시
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              CircleAvatar(
                backgroundColor: Colors.blue[700],
                child: Text(
                  user.userName.substring(user.userName.length - 1),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  user.userName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildInfoRow('이름', profile.userName ?? '정보 없음'),
                _buildInfoRow('이메일', user.email),
                _buildInfoRow('전화번호', user.phoneNumber),
                _buildInfoRow('성별', profile.gender == 'male' ? '남성' : '여성'),
                _buildInfoRow('생년월일', profile.dateOfBirth.toString().split(' ')[0]),
                _buildInfoRow('주소', profile.address),
                _buildInfoRow('상세주소', profile.addressDetail),
                if (profile.medicalHistory != null)
                  _buildInfoRow('의료기록', profile.medicalHistory!),
                if (profile.significantNotes != null)
                  _buildInfoRow('특이사항', profile.significantNotes!),
                _buildInfoRow('현재상태', profile.currentStatus),
                _buildInfoRow('가입일', user.createdAt.toString().split(' ')[0]),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text(
                '닫기',
                style: TextStyle(color: Colors.blue),
              ),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                context.push('/users/${user.userId}');
              },
              child: const Text(
                '상세보기',
                style: TextStyle(color: Colors.green),
              ),
            ),
          ],
        ),
      );
    } catch (e) {
      // 로딩 다이얼로그 닫기
      Navigator.of(context).pop();
      
      // 에러 다이얼로그 표시
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          backgroundColor: Colors.grey[900],
          title: const Text(
            '오류',
            style: TextStyle(color: Colors.red),
          ),
          content: Text(
            '사용자 정보를 불러오는 중 오류가 발생했습니다: $e',
            style: const TextStyle(color: Colors.white),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text(
                '닫기',
                style: TextStyle(color: Colors.blue),
              ),
            ),
          ],
        ),
      );
    }
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
