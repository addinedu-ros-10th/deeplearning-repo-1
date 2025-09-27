import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../voice/state/voice_provider.dart';
import 'math_helper.dart';

class VoicePage extends StatelessWidget {
  const VoicePage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Voice Interface', style: theme.textTheme.titleLarge?.copyWith(color: Colors.white70)),
              const SizedBox(height: 16),
              Expanded(
                child: Center(
                  child: AspectRatio(
                    aspectRatio: 3,
                    child: Consumer<VoiceProvider>(
                      builder: (context, vp, _) => CustomPaint(
                        painter: _WaveformPainter(level: vp.volumeLevel),
                        child: const SizedBox.expand(),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Consumer<VoiceProvider>(
                builder: (context, vp, _) => Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            'TTS Server: '
                            '${vp.ttsHealthStatus == null ? '(Not checked)' : vp.ttsHealthStatus}'
                            '${vp.ttsHealthBackend == null ? '' : ' / ${vp.ttsHealthBackend}'}',
                            style: TextStyle(
                              color: vp.ttsHealthStatus == 'ok'
                                  ? Colors.lightGreenAccent
                                  : (vp.ttsHealthStatus == null ? Colors.white54 : Colors.redAccent),
                            ),
                          ),
                        ),
                        IconButton(
                          onPressed: vp.checkTtsHealth,
                          icon: const Icon(Icons.refresh, color: Colors.white70),
                          tooltip: 'Check TTS Server',
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // STT/TTS information
                    Text(vp.sttInfoText, style: const TextStyle(color: Colors.white54)),
                    const SizedBox(height: 8),
                    if (vp.availableEngines.isNotEmpty)
                      Text(vp.engineInfoText, style: const TextStyle(color: Colors.white54)),
                    if (vp.availableEngines.isNotEmpty) const SizedBox(height: 8),
                    Text(vp.backendInfoText, style: const TextStyle(color: Colors.white54)),
                    const SizedBox(height: 8),
                    Text(vp.voiceInfoText, style: const TextStyle(color: Colors.white54)),
                    const SizedBox(height: 4),
                    Text(vp.modelVoiceInfoText, style: const TextStyle(color: Colors.white54)),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: FilledButton(
                            onPressed: vp.isListening ? vp.stopListening : vp.startListening,
                            style: FilledButton.styleFrom(backgroundColor: Colors.grey[850]),
                            child: Text(vp.isListening ? 'Stop' : 'Listen', style: const TextStyle(color: Colors.white)),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: FilledButton(
                            onPressed: vp.sendToAssistant,
                            style: FilledButton.styleFrom(backgroundColor: Colors.grey[700]),
                            child: const Text('Ask + Speak', style: TextStyle(color: Colors.white)),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (vp.availableEngines.isNotEmpty)
                      Row(
                        children: [
                          Expanded(
                            child: DropdownButtonFormField<String>(
                              dropdownColor: Colors.black,
                              value: vp.selectedEngine?.toString().isEmpty == true ? null : vp.selectedEngine,
                              items: vp.availableEngines
                                  .map((e) => DropdownMenuItem<String>(
                                        value: e,
                                        child: Text(e, style: const TextStyle(color: Colors.white70)),
                                      ))
                                  .toList(),
                              onChanged: (String? engine) {
                                if (engine != null) {
                                  vp.selectEngine(engine);
                                }
                              },
                              decoration: const InputDecoration(
                                labelText: 'TTS Engine',
                                labelStyle: TextStyle(color: Colors.white54),
                                enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white24)),
                                focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white54)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    if (vp.availableEngines.isNotEmpty) const SizedBox(height: 12),
                    // Backend (Piper/Mimic3/OpenTTS/System)
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            dropdownColor: Colors.black,
                            value: vp.selectedBackend,
                            items: vp.availableBackends
                                .map((b) => DropdownMenuItem<String>(
                                      value: b,
                                      child: Text(b, style: const TextStyle(color: Colors.white70)),
                                    ))
                                .toList(),
                            onChanged: (String? b) {
                              if (b != null) {
                                vp.selectBackend(b);
                              }
                            },
                            decoration: const InputDecoration(
                              labelText: 'Korean TTS Backend',
                              labelStyle: TextStyle(color: Colors.white54),
                              enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white24)),
                              focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white54)),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (vp.selectedBackend == 'piper')
                      Row(
                        children: [
                          Expanded(
                            child: DropdownButtonFormField<String>(
                              dropdownColor: Colors.black,
                              value: vp.selectedModelVoice,
                              items: vp.availableModelVoices
                                  .map((mv) => DropdownMenuItem<String>(
                                        value: mv,
                                        child: Text(mv, style: const TextStyle(color: Colors.white70)),
                                      ))
                                  .toList(),
                              onChanged: (String? mv) {
                                if (mv != null) {
                                  vp.setModelVoice(mv);
                                }
                              },
                              decoration: const InputDecoration(
                                labelText: 'Piper Voice (ko_KR)',
                                labelStyle: TextStyle(color: Colors.white54),
                                enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white24)),
                                focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white54)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    if (vp.selectedBackend == 'piper') const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            dropdownColor: Colors.black,
                            value: vp.selectedVoice?['name']?.toString(),
                            items: vp.availableVoices
                                .map((v) => DropdownMenuItem<String>(
                                      value: v['name']?.toString(),
                                      child: Text(v['name']?.toString() ?? 'unknown', style: const TextStyle(color: Colors.white70)),
                                    ))
                                .toList(),
                            onChanged: (String? name) {
                              if (name != null) {
                                vp.selectVoiceByName(name);
                              }
                            },
                            decoration: const InputDecoration(
                              labelText: 'Voice',
                              labelStyle: TextStyle(color: Colors.white54),
                              enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white24)),
                              focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white54)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Text('Rate: ${vp.ttsRate.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white54)),
                              Slider(
                                value: vp.ttsRate,
                                min: 0.1,
                                max: 1.5,
                                onChanged: (v) => vp.setTtsRate(v),
                              ),
                              Text('Pitch: ${vp.ttsPitch.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white54)),
                              Slider(
                                value: vp.ttsPitch,
                                min: 0.5,
                                max: 2.0,
                                onChanged: (v) => vp.setTtsPitch(v),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Consumer<VoiceProvider>(
                builder: (context, vp, _) => Text(
                  'TXT: ${vp.transcript}\nRES: ${vp.responseText}',
                  style: const TextStyle(color: Colors.white54),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _WaveformPainter extends CustomPainter {
  _WaveformPainter({required this.level});
  final double level;

  @override
  void paint(Canvas canvas, Size size) {
    final Paint grid = Paint()
      ..color = Colors.white12
      ..strokeWidth = 1;
    final Paint wave = Paint()
      ..color = Colors.white70
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    // center line
    canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), grid);

    // simple grayscale waveform; use math sin
    final Path path = Path();
    const int points = 120;
    for (int i = 0; i <= points; i++) {
      final double x = size.width * (i / points);
      final double y = size.height / 2 + (MathHelper.sin(i / 4)) * (size.height / 3) * level;
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, wave);
  }

  @override
  bool shouldRepaint(covariant _WaveformPainter oldDelegate) => oldDelegate.level != level;
}


