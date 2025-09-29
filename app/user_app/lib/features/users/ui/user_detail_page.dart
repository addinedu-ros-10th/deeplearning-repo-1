import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;
import '../models/user_models.dart';
import '../service/users_service.dart';
import '../../auth/state/auth_provider.dart';

class UserDetailPage extends StatefulWidget {
  final String userId;

  const UserDetailPage({
    super.key,
    required this.userId,
  });

  @override
  State<UserDetailPage> createState() => _UserDetailPageState();
}

class _UserDetailPageState extends State<UserDetailPage> {
  final UsersService _usersService = UsersService();
  UserProfile? _profile;
  List<UserRelationship> _relationships = [];
  bool _isLoading = true;
  String? _errorMessage;
  bool _showNetworkView = false;
  String? _selectedNodeUserId;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await Future.wait([
        _usersService.getUserProfile(widget.userId),
        _usersService.getUserRelationships(widget.userId),
      ]);

      setState(() {
        _profile = results[0] as UserProfile;
        _relationships = results[1] as List<UserRelationship>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '사용자 정보를 불러오는데 실패했습니다: $e';
        _isLoading = false;
      });
    }
  }

  String _getGenderText(String gender) {
    switch (gender.toLowerCase()) {
      case 'male':
        return '남성';
      case 'female':
        return '여성';
      default:
        return gender;
    }
  }

  String _getStatusText(String status) {
    switch (status.toLowerCase()) {
      case 'active':
        return '활성';
      case 'inactive':
        return '비활성';
      default:
        return status;
    }
  }

  String _getRelationshipTypeText(String type) {
    switch (type.toLowerCase()) {
      case 'admin':
        return '관리자';
      case 'caregiver':
        return '돌봄사';
      case 'family':
        return '가족';
      default:
        return type;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case '주의':
        return Colors.orange;
      case '정상':
        return Colors.green;
      case '위험':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('사용자 상세정보'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white70,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadUserData,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _showLogoutDialog,
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
              onPressed: _loadUserData,
              child: const Text('다시 시도'),
            ),
          ],
        ),
      );
    }

    if (_profile == null) {
      return const Center(
        child: Text(
          '사용자 정보를 찾을 수 없습니다',
          style: TextStyle(color: Colors.grey),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildProfileCard(),
          const SizedBox(height: 16),
          _buildRelationshipsCard(),
        ],
      ),
    );
  }

  Widget _buildProfileCard() {
    return Card(
      color: Colors.grey[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.blue[700],
                  child: Text(
                    _profile!.userName.substring(_profile!.userName.length - 1),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _profile!.userName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: _getStatusColor(_profile!.currentStatus),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          _profile!.currentStatus,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            _buildInfoRow('생년월일', _profile!.dateOfBirth.toString().split(' ')[0]),
            _buildInfoRow('성별', _getGenderText(_profile!.gender)),
            _buildInfoRow('주소', '${_profile!.address} ${_profile!.addressDetail}'),
            if (_profile!.medicalHistory.isNotEmpty)
              _buildInfoRow('의료 이력', _profile!.medicalHistory),
            if (_profile!.significantNotes.isNotEmpty)
              _buildInfoRow('특이사항', _profile!.significantNotes),
            _buildInfoRow('등록일', _profile!.createdAt.toString().split(' ')[0]),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
          ),
          const SizedBox(width: 16),
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

  Widget _buildRelationshipsCard() {
    return Card(
      color: Colors.grey[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  '인적 자원 네트워크',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {
                    setState(() {
                      _showNetworkView = !_showNetworkView;
                    });
                  },
                  icon: Icon(
                    _showNetworkView ? Icons.list : Icons.account_tree,
                    color: Colors.blue,
                  ),
                  label: Text(
                    _showNetworkView ? '목록 보기' : '네트워크 보기',
                    style: const TextStyle(color: Colors.blue),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_showNetworkView)
              _buildNetworkView()
            else if (_relationships.isEmpty)
              const Text(
                '등록된 관계자가 없습니다',
                style: TextStyle(color: Colors.grey),
              )
            else
              ..._relationships.map((relationship) => _buildRelationshipItem(relationship)),
          ],
        ),
      ),
    );
  }

  Widget _buildRelationshipItem(UserRelationship relationship) {
    return GestureDetector(
      onTap: () => _showRelationshipInfoDialog(relationship),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.grey[800],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: Colors.grey[600]!,
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _getRelationshipTypeColor(relationship.relationshipType),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _getRelationshipTypeText(relationship.relationshipType),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ID: ${relationship.subjectUserId.substring(0, 8)}...',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    '상태: ${_getStatusText(relationship.status)}',
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              color: Colors.grey,
              size: 16,
            ),
          ],
        ),
      ),
    );
  }

  Color _getRelationshipTypeColor(String type) {
    switch (type.toLowerCase()) {
      case 'admin':
        return Colors.red[700]!;
      case 'caregiver':
        return Colors.blue[700]!;
      case 'family':
        return Colors.green[700]!;
      default:
        return Colors.grey[700]!;
    }
  }

  Widget _buildNetworkView() {
    if (_relationships.isEmpty) {
      return const SizedBox(
        height: 200,
        child: Center(
          child: Text(
            '관계자가 없어 네트워크를 표시할 수 없습니다',
            style: TextStyle(color: Colors.grey),
          ),
        ),
      );
    }

    return SizedBox(
      height: 400, // 높이 증가
      child: _buildSimpleNetworkView(),
    );
  }

  Widget _buildSimpleNetworkView() {
    return SizedBox(
      height: 400, // 높이 증가
      child: CustomPaint(
        painter: NetworkPainter(
          relationships: _relationships,
          selectedNodeId: _selectedNodeUserId,
          getRelationshipTypeColor: _getRelationshipTypeColor,
        ),
        child: Stack(
          children: [
            // 중앙 노드 (현재 사용자)
            Positioned(
              left: 160, // (400 - 80) / 2
              top: 160,  // (400 - 80) / 2
              child: GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedNodeUserId = _selectedNodeUserId == widget.userId 
                        ? null 
                        : widget.userId;
                  });
                },
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.blue[700],
                    border: _selectedNodeUserId == widget.userId
                        ? Border.all(color: Colors.yellow, width: 3)
                        : null,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.blue.withOpacity(0.3),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Text(
                      '나',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
            ),
            
            // 관계자 노드들 (원형 배치)
            ..._buildRelationshipNodes(),
            
            // 하단 안내 텍스트
            const Positioned(
              bottom: 20,
              left: 0,
              right: 0,
              child: Center(
                child: Text(
                  '관계자 노드를 터치하여 선택하세요',
                  style: TextStyle(
                    color: Colors.grey,
                    fontSize: 14,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildRelationshipNodes() {
    final centerX = 200.0; // 400 / 2
    final centerY = 200.0; // 400 / 2
    final radius = 100.0; // 반지름 증가
    
    return _relationships.asMap().entries.map((entry) {
      final index = entry.key;
      final relationship = entry.value;
      final angle = (index * 2 * math.pi) / _relationships.length;
      final x = centerX + radius * math.cos(angle) - 30; // 60/2 = 30 (노드 반지름)
      final y = centerY + radius * math.sin(angle) - 30;
      
      return Positioned(
        left: x,
        top: y,
        child: GestureDetector(
          onTap: () => _showRelationshipInfoDialog(relationship),
          child: Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _getRelationshipTypeColor(relationship.relationshipType),
              border: _selectedNodeUserId == relationship.subjectUserId
                  ? Border.all(color: Colors.yellow, width: 3)
                  : null,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 5,
                  spreadRadius: 1,
                ),
              ],
            ),
            child: Center(
              child: Text(
                _getRelationshipTypeText(relationship.relationshipType)[0],
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ),
      );
    }).toList();
  }

  void _showRelationshipInfoDialog(UserRelationship relationship) async {
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
      // 관계자의 프로필 정보 조회
      final profile = await UsersService().getUserProfile(relationship.subjectUserId);
      
      // 로딩 다이얼로그 닫기
      Navigator.of(context).pop();
      
      // 프로필 정보 다이얼로그 표시
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _getRelationshipTypeColor(relationship.relationshipType),
                ),
                child: Center(
                  child: Text(
                    _getRelationshipTypeText(relationship.relationshipType)[0],
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  _getRelationshipTypeText(relationship.relationshipType),
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
                _buildInfoRow('성별', profile.gender == 'male' ? '남성' : '여성'),
                _buildInfoRow('생년월일', profile.dateOfBirth.toString().split(' ')[0]),
                _buildInfoRow('주소', profile.address),
                _buildInfoRow('상세주소', profile.addressDetail),
                if (profile.medicalHistory != null)
                  _buildInfoRow('의료기록', profile.medicalHistory!),
                if (profile.significantNotes != null)
                  _buildInfoRow('특이사항', profile.significantNotes!),
                _buildInfoRow('현재상태', profile.currentStatus),
                _buildInfoRow('관계유형', _getRelationshipTypeText(relationship.relationshipType)),
                _buildInfoRow('관계상태', _getStatusText(relationship.status)),
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


  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Text(
          '로그아웃',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          '정말 로그아웃하시겠습니까?',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(
              '취소',
              style: TextStyle(color: Colors.grey),
            ),
          ),
          TextButton(
            onPressed: () async {
              await context.read<AuthProvider>().logout();
              if (mounted) {
                context.go('/login');
              }
            },
            child: const Text(
              '로그아웃',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

}

// 네트워크 페인터 (엣지 그리기)
class NetworkPainter extends CustomPainter {
  final List<UserRelationship> relationships;
  final String? selectedNodeId;
  final Color Function(String) getRelationshipTypeColor;

  NetworkPainter({
    required this.relationships,
    required this.selectedNodeId,
    required this.getRelationshipTypeColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // 실제 중앙 노드 위치 (Positioned 기준) - 400x400 크기에 맞게 조정
    final centerNodeX = 200.0; // 160 + 40 (노드 반지름)
    final centerNodeY = 200.0; // 160 + 40 (노드 반지름)
    final centerNodePosition = Offset(centerNodeX, centerNodeY);
    
    // 관계자 노드들의 위치 계산 (Positioned 기준과 정확히 일치)
    final nodePositions = <String, Offset>{};
    final angleStep = 2 * 3.14159 / relationships.length;
    final radius = 100.0; // 반지름 증가
    
    for (int i = 0; i < relationships.length; i++) {
      final angle = i * angleStep;
      // Positioned 위젯의 실제 위치 계산과 동일하게
      final x = 200.0 + radius * math.cos(angle) - 30; // centerX + radius * cos - 30
      final y = 200.0 + radius * math.sin(angle) - 30; // centerY + radius * sin - 30
      // 노드 중심점으로 변환 (30은 노드 반지름)
      nodePositions[relationships[i].subjectUserId] = Offset(x + 30, y + 30);
    }
    
    // 엣지 그리기
    for (final relationship in relationships) {
      final targetPos = nodePositions[relationship.subjectUserId];
      if (targetPos != null) {
        // 기본 엣지 (더 굵고 명확하게)
        final paint = Paint()
          ..color = getRelationshipTypeColor(relationship.relationshipType).withOpacity(0.9)
          ..strokeWidth = 4.0
          ..style = PaintingStyle.stroke
          ..strokeCap = StrokeCap.round;
        
        // 중앙 노드에서 관계자 노드로 선 그리기
        canvas.drawLine(centerNodePosition, targetPos, paint);
        
        // 선택된 노드인 경우 더 굵은 선
        if (selectedNodeId == relationship.subjectUserId) {
          final selectedPaint = Paint()
            ..color = Colors.yellow
            ..strokeWidth = 6.0
            ..style = PaintingStyle.stroke
            ..strokeCap = StrokeCap.round;
          canvas.drawLine(centerNodePosition, targetPos, selectedPaint);
        }
        
        // 엣지 중앙에 화살표 그리기
        _drawArrow(canvas, centerNodePosition, targetPos, getRelationshipTypeColor(relationship.relationshipType));
        
        // 관계 타입 라벨 그리기
        _drawRelationshipLabel(canvas, centerNodePosition, targetPos, relationship.relationshipType);
      }
    }
  }

  void _drawArrow(Canvas canvas, Offset from, Offset to, Color color) {
    final direction = (to - from).direction;
    final arrowLength = 15.0;
    final arrowAngle = 0.5;
    
    final arrowPoint1 = Offset(
      to.dx - arrowLength * math.cos(direction - arrowAngle),
      to.dy - arrowLength * math.sin(direction - arrowAngle),
    );
    
    final arrowPoint2 = Offset(
      to.dx - arrowLength * math.cos(direction + arrowAngle),
      to.dy - arrowLength * math.sin(direction + arrowAngle),
    );
    
    final arrowPaint = Paint()
      ..color = color.withOpacity(0.8)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    
    // 화살표 그리기
    canvas.drawLine(to, arrowPoint1, arrowPaint);
    canvas.drawLine(to, arrowPoint2, arrowPaint);
  }

  void _drawRelationshipLabel(Canvas canvas, Offset from, Offset to, String relationshipType) {
    final midPoint = Offset(
      (from.dx + to.dx) / 2,
      (from.dy + to.dy) / 2,
    );
    
    final textPainter = TextPainter(
      text: TextSpan(
        text: _getRelationshipTypeText(relationshipType),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    
    textPainter.layout();
    
    // 배경 원 그리기
    final backgroundPaint = Paint()
      ..color = Colors.black.withOpacity(0.7)
      ..style = PaintingStyle.fill;
    
    canvas.drawCircle(
      midPoint,
      textPainter.width / 2 + 8,
      backgroundPaint,
    );
    
    // 텍스트 그리기
    textPainter.paint(
      canvas,
      Offset(
        midPoint.dx - textPainter.width / 2,
        midPoint.dy - textPainter.height / 2,
      ),
    );
  }

  String _getRelationshipTypeText(String type) {
    switch (type) {
      case 'family':
        return '가족';
      case 'caregiver':
        return '돌봄';
      case 'administrator':
        return '관리자';
      default:
        return type;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return oldDelegate is NetworkPainter &&
        (oldDelegate.relationships != relationships ||
         oldDelegate.selectedNodeId != selectedNodeId);
  }
}
