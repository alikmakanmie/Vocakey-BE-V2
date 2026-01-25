import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:noise_meter/noise_meter.dart';
import 'package:percent_indicator/percent_indicator.dart';

import '../../../../core/constants/app_colors.dart';
import '../../../../core/services/permission_service.dart';
import '../bloc/pitch_bloc.dart';
import '../bloc/pitch_event.dart';
import '../bloc/pitch_state.dart';
import 'pitch_result_page.dart';

class PitchRecordingPage extends StatefulWidget {
  const PitchRecordingPage({Key? key}) : super(key: key);

  @override
  State<PitchRecordingPage> createState() => _PitchRecordingPageState();
}

class _PitchRecordingPageState extends State<PitchRecordingPage>
    with SingleTickerProviderStateMixin {
  final AudioRecorder _audioRecorder = AudioRecorder();
  final PermissionService _permissionService = PermissionService();

  bool _isRecording = false;
  bool _isAnalyzing = false;
  int _recordDuration = 0;
  Timer? _timer;
  String? _audioPath;
  StreamSubscription<PitchState>? _blocSubscription;

  // Real-time audio amplitude
  NoiseMeter? _noiseMeter;
  StreamSubscription<NoiseReading>? _noiseSubscription;
  List<double> _amplitudes = List.filled(12, 0.2);
  double _currentDecibel = 0;

  // ✅ NEW: Max recording duration (30 seconds)
  static const int maxRecordingDuration = 30;

  @override
  void initState() {
    super.initState();
    _listenToBlocState();
    _noiseMeter = NoiseMeter();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _blocSubscription?.cancel();
    _noiseSubscription?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  void _listenToBlocState() {
    _blocSubscription = context.read<PitchBloc>().stream.listen((state) {
      if (!mounted) return;

      if (state is PitchAnalysisSuccess) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => PitchResultPage(result: state.result),
          ),
        );
      } else if (state is PitchAnalysisError) {
        setState(() {
          _isAnalyzing = false;
        });
        _showErrorDialog(state.message);
      }
    });
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.error_outline, color: Colors.red, size: 28),
            SizedBox(width: 12),
            Text('Recording Failed', style: TextStyle(fontSize: 18)),
          ],
        ),
        content: Text(
          message.isEmpty
              ? 'Voice not detected. Make sure you hum clearly.'
              : message,
          style: const TextStyle(fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _startRecording();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF6B9FE8),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }

  Future<void> _startRecording() async {
    try {
      // Request permission
      bool hasPermission = await _permissionService.requestMicrophonePermission();
      if (!hasPermission) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Microphone permission is required'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      if (await _audioRecorder.hasPermission()) {
        final Directory appDocumentsDir = await getApplicationDocumentsDirectory();
        final String filePath =
            '${appDocumentsDir.path}/recording_${DateTime.now().millisecondsSinceEpoch}.wav';

        await _audioRecorder.start(
          const RecordConfig(
            encoder: AudioEncoder.wav,
            bitRate: 128000,
            sampleRate: 44100,
            numChannels: 1,
          ),
          path: filePath,
        );

        _startNoiseMonitoring();

        setState(() {
          _isRecording = true;
          _isAnalyzing = false;
          _recordDuration = 0;
        });

        _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
          if (!mounted) {
            timer.cancel();
            return;
          }

          setState(() {
            _recordDuration++;
          });

          // ✅ Auto stop at max duration
          if (_recordDuration >= maxRecordingDuration) {
            timer.cancel();
            _stopRecording();
          }
        });
      }
    } catch (e) {
      print('Error starting recording: $e');
      if (mounted) {
        _showErrorDialog('Failed to start recording: $e');
      }
    }
  }

  void _startNoiseMonitoring() {
    try {
      _noiseSubscription = _noiseMeter?.noise.listen(
        (NoiseReading noiseReading) {
          if (!mounted) return;
          setState(() {
            _currentDecibel = noiseReading.meanDecibel;
            double normalizedDb = (_currentDecibel - 20).clamp(0, 70) / 70;
            
            for (int i = _amplitudes.length - 1; i > 0; i--) {
              _amplitudes[i] = _amplitudes[i - 1];
            }
            _amplitudes[0] = 0.2 + (normalizedDb * 0.8);
          });
        },
        onError: (error) {
          print('Noise meter error: $error');
        },
      );
    } catch (e) {
      print('Error starting noise monitoring: $e');
    }
  }

  Future<void> _stopRecording() async {
    try {
      _timer?.cancel();
      _noiseSubscription?.cancel();
      final path = await _audioRecorder.stop();

      setState(() {
        _isRecording = false;
        _audioPath = path;
        _isAnalyzing = true;
        _amplitudes = List.filled(12, 0.2);
      });

      if (path != null && mounted) {
        context.read<PitchBloc>().add(AnalyzeAudioEvent(path));
      }
    } catch (e) {
      print('Error stopping recording: $e');
      setState(() {
        _isAnalyzing = false;
      });
      if (mounted) {
        _showErrorDialog('Failed to stop recording: $e');
      }
    }
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final progress = _recordDuration / maxRecordingDuration;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppColors.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: _isAnalyzing || _isRecording
                          ? null
                          : () => Navigator.pop(context),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'Record Your Voice',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(flex: 1),

              // Title
              const Text(
                'Determine Your\nBase Note',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                _isAnalyzing
                    ? 'Analyzing your voice...'
                    : _isRecording
                        ? 'Recording in progress...'
                        : 'Tap the button to start',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.9),
                  fontSize: 16,
                ),
              ),

              const Spacer(flex: 1),

              // ✅ Audio Spectrum Visualizer (only when recording)
              if (_isRecording)
                _AudioSpectrumVisualizer(
                  amplitudes: _amplitudes,
                  isRecording: _isRecording,
                )
              else
                const SizedBox(height: 150),

              const Spacer(flex: 1),

              // ✅ MAIN RECORDING BUTTON WITH PROGRESS
              Stack(
                alignment: Alignment.center,
                children: [
                  // Circular Progress Indicator (when recording)
                  if (_isRecording)
                    CircularPercentIndicator(
                      radius: 90.0,
                      lineWidth: 8.0,
                      percent: progress.clamp(0.0, 1.0),
                      center: Container(
                        width: 160,
                        height: 160,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.mic,
                          size: 70,
                          color: Colors.red,
                        ),
                      ),
                      progressColor: Colors.red,
                      backgroundColor: Colors.white.withOpacity(0.3),
                      circularStrokeCap: CircularStrokeCap.round,
                    )
                  else
                    // Static button (when not recording)
                    GestureDetector(
                      onTap: !_isAnalyzing ? _startRecording : null,
                      child: Container(
                        width: 160,
                        height: 160,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: _isAnalyzing
                            ? const Center(
                                child: CircularProgressIndicator(
                                  color: Color(0xFF6B9FE8),
                                  strokeWidth: 4,
                                ),
                              )
                            : const Icon(
                                Icons.mic,
                                size: 70,
                                color: Color(0xFF6B9FE8),
                              ),
                      ),
                    ),
                ],
              ),

              const SizedBox(height: 24),

              // ✅ TIMER DISPLAY (when recording)
if (_isRecording)
  Container(
    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
    decoration: BoxDecoration(
      color: Colors.white.withOpacity(0.2),
      borderRadius: BorderRadius.circular(20),
    ),
    child: Text(
      _formatDuration(_recordDuration),
      style: const TextStyle(
        color: Colors.white,
        fontSize: 28,
        fontWeight: FontWeight.bold,
        // ✅ FIXED: Removed fontFeatureSettings
      ),
    ),
  )
else
  const SizedBox(height: 48),


              const SizedBox(height: 20),

              // ✅ STOP BUTTON (visible only when recording)
              if (_isRecording)
                ElevatedButton.icon(
                  onPressed: _stopRecording,
                  icon: const Icon(Icons.stop, size: 24),
                  label: const Text(
                    'STOP RECORDING',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                    elevation: 8,
                  ),
                )
              else if (!_isAnalyzing)
                Text(
                  'Hum or sing clearly for best results',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 14,
                  ),
                ),

              const Spacer(flex: 2),
            ],
          ),
        ),
      ),
    );
  }
}

// ✅ Real-time Audio Spectrum Visualizer
class _AudioSpectrumVisualizer extends StatelessWidget {
  final List<double> amplitudes;
  final bool isRecording;

  const _AudioSpectrumVisualizer({
    required this.amplitudes,
    required this.isRecording,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 150,
      width: 220,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background Circle
          Container(
            width: 160,
            height: 160,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white.withOpacity(0.1),
            ),
          ),
          // Spectrum Bars
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: List.generate(12, (index) {
              final amplitude = amplitudes[index];
              final height = 20 + (amplitude * 70);
              return AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                curve: Curves.easeOut,
                margin: const EdgeInsets.symmetric(horizontal: 3),
                width: 7,
                height: height,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(4),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.white.withOpacity(0.5),
                      blurRadius: 4,
                    ),
                  ],
                ),
              );
            }),
          ),
          // Music note icon
          Positioned(
            top: 5,
            right: 20,
            child: Icon(
              Icons.music_note_rounded,
              color: Colors.white.withOpacity(0.8),
              size: 28,
            ),
          ),
        ],
      ),
    );
  }
}
