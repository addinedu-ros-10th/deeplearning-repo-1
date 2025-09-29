import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../service/flutter_tts_service.dart';

class TtsSettingsPage extends StatefulWidget {
  const TtsSettingsPage({super.key});

  @override
  State<TtsSettingsPage> createState() => _TtsSettingsPageState();
}

class _TtsSettingsPageState extends State<TtsSettingsPage> {
  final FlutterTtsService _ttsService = FlutterTtsService();
  List<String> _availableVoices = [];
  String _selectedVoice = 'alloy';
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadVoices();
  }

  Future<void> _loadVoices() async {
    try {
      final voices = await _ttsService.getAvailableVoices();
      setState(() {
        _availableVoices = voices;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => context.pop(),
        ),
        title: const Text(
          'TTS 설정',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '음성 선택',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            
            if (_isLoading)
              const Center(
                child: CircularProgressIndicator(color: Colors.blue),
              )
            else
              Expanded(
                child: ListView.builder(
                  itemCount: _availableVoices.length,
                  itemBuilder: (context, index) {
                    final voice = _availableVoices[index];
                    final isSelected = voice == _selectedVoice;
                    
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      decoration: BoxDecoration(
                        color: isSelected ? Colors.blue[700] : Colors.grey[800],
                        borderRadius: BorderRadius.circular(12),
                        border: isSelected 
                            ? Border.all(color: Colors.blue[400]!, width: 2)
                            : null,
                      ),
                      child: ListTile(
                        title: Text(
                          voice.toUpperCase(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        subtitle: Text(
                          _getVoiceDescription(voice),
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                        trailing: isSelected
                            ? const Icon(Icons.check_circle, color: Colors.white)
                            : const Icon(Icons.radio_button_unchecked, color: Colors.grey),
                        onTap: () {
                          setState(() {
                            _selectedVoice = voice;
                          });
                        },
                      ),
                    );
                  },
                ),
              ),
            
            const SizedBox(height: 20),
            
            // 테스트 버튼
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => _testVoice(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[600],
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  '음성 테스트',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 12),
            
            // 저장 버튼
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => _saveSettings(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green[600],
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  '설정 저장',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getVoiceDescription(String voice) {
    switch (voice.toLowerCase()) {
      case 'alloy':
        return '자연스럽고 부드러운 음성';
      case 'echo':
        return '명확하고 강한 음성';
      case 'fable':
        return '따뜻하고 친근한 음성';
      case 'onyx':
        return '깊고 진중한 음성';
      case 'nova':
        return '밝고 활기찬 음성';
      case 'shimmer':
        return '우아하고 세련된 음성';
      default:
        return '기본 음성';
    }
  }

  Future<void> _testVoice() async {
    try {
      // 음성 설정
      await _ttsService.setVoice(_selectedVoice);
      
      // 테스트 음성 재생
      await _ttsService.speak('안녕하세요. 이것은 ${_selectedVoice} 음성 테스트입니다.');
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${_selectedVoice} 음성 테스트가 재생됩니다.'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('음성 테스트 오류: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _saveSettings() {
    // TODO: SharedPreferences에 설정 저장
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('설정이 저장되었습니다.'),
        backgroundColor: Colors.green,
      ),
    );
    context.pop();
  }
}
