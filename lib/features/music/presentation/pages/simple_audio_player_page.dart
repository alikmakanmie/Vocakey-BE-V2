import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';

class SimpleAudioPlayerPage extends StatefulWidget {
  final String audioUrl;
  final String title;
  final String artist;
  final String originalKey;

  const SimpleAudioPlayerPage({
    Key? key,
    required this.audioUrl,
    required this.title,
    required this.artist,
    required this.originalKey,
  }) : super(key: key);

  @override
  State<SimpleAudioPlayerPage> createState() => _SimpleAudioPlayerPageState();
}

class _SimpleAudioPlayerPageState extends State<SimpleAudioPlayerPage> {
  late AudioPlayer _audioPlayer;
  bool _isLoading = true;
  bool _hasError = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _audioPlayer = AudioPlayer();
    _initAudio();
  }

  Future<void> _initAudio() async {
    try {
      print('🎵 Loading audio from: ${widget.audioUrl}');
      
      // Set audio source
      await _audioPlayer.setUrl(widget.audioUrl);
      
      setState(() {
        _isLoading = false;
      });
      
      print('✅ Audio loaded successfully');
      
      // Auto-play
      _audioPlayer.play();
    } catch (e) {
      print('❌ Error loading audio: $e');
      setState(() {
        _isLoading = false;
        _hasError = true;
        _errorMessage = e.toString();
      });
    }
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  String _formatDuration(Duration? duration) {
    if (duration == null) return '0:00';
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds.remainder(60);
    return '$minutes:${twoDigits(seconds)}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Now Playing',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF1A1A2E),
              Color(0xFF16213E),
              Color(0xFF0F3460),
            ],
          ),
        ),
        child: SafeArea(
          child: _isLoading
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(color: Colors.white),
                      SizedBox(height: 16),
                      Text(
                        'Loading audio...',
                        style: TextStyle(color: Colors.white70, fontSize: 16),
                      ),
                    ],
                  ),
                )
              : _hasError
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.error_outline,
                              color: Colors.red,
                              size: 64,
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'Failed to load audio',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _errorMessage,
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                color: Colors.white70,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 24),
                            ElevatedButton(
                              onPressed: () => Navigator.pop(context),
                              child: const Text('Go Back'),
                            ),
                          ],
                        ),
                      ),
                    )
                  : Column(
                      children: [
                        const SizedBox(height: 40),
                        
                        // Album Art Placeholder
                        Container(
                          width: 280,
                          height: 280,
                          decoration: BoxDecoration(
                            color: const Color(0xFF6B9FE8).withOpacity(0.3),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Icon(
                            Icons.music_note,
                            size: 120,
                            color: Colors.white,
                          ),
                        ),
                        
                        const SizedBox(height: 40),
                        
                        // Song Info
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 32),
                          child: Column(
                            children: [
                              Text(
                                widget.title,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                widget.artist,
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.7),
                                  fontSize: 18,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF6B9FE8).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Text(
                                  'Key: ${widget.originalKey}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        
                        const Spacer(),
                        
                        // Progress Bar & Time
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 32),
                          child: StreamBuilder<Duration?>(
                            stream: _audioPlayer.positionStream,
                            builder: (context, snapshot) {
                              final position = snapshot.data ?? Duration.zero;
                              final duration = _audioPlayer.duration ?? Duration.zero;
                              
                              return Column(
                                children: [
                                  SliderTheme(
                                    data: SliderTheme.of(context).copyWith(
                                      trackHeight: 4,
                                      thumbShape: const RoundSliderThumbShape(
                                        enabledThumbRadius: 6,
                                      ),
                                    ),
                                    child: Slider(
                                      value: position.inSeconds.toDouble(),
                                      max: duration.inSeconds.toDouble() > 0
                                          ? duration.inSeconds.toDouble()
                                          : 1.0,
                                      activeColor: Colors.white,
                                      inactiveColor: Colors.white.withOpacity(0.3),
                                      onChanged: (value) {
                                        _audioPlayer.seek(
                                          Duration(seconds: value.toInt()),
                                        );
                                      },
                                    ),
                                  ),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        _formatDuration(position),
                                        style: TextStyle(
                                          color: Colors.white.withOpacity(0.7),
                                          fontSize: 12,
                                        ),
                                      ),
                                      Text(
                                        _formatDuration(duration),
                                        style: TextStyle(
                                          color: Colors.white.withOpacity(0.7),
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              );
                            },
                          ),
                        ),
                        
                        const SizedBox(height: 32),
                        
                        // Play/Pause Controls
                        StreamBuilder<PlayerState>(
                          stream: _audioPlayer.playerStateStream,
                          builder: (context, snapshot) {
                            final playerState = snapshot.data;
                            final isPlaying = playerState?.playing ?? false;
                            final processingState = playerState?.processingState;
                            
                            return Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                // Previous (disabled for now)
                                IconButton(
                                  iconSize: 48,
                                  icon: Icon(
                                    Icons.skip_previous,
                                    color: Colors.white.withOpacity(0.3),
                                  ),
                                  onPressed: null,
                                ),
                                
                                const SizedBox(width: 20),
                                
                                // Play/Pause
                                Container(
                                  width: 80,
                                  height: 80,
                                  decoration: const BoxDecoration(
                                    color: Colors.white,
                                    shape: BoxShape.circle,
                                  ),
                                  child: IconButton(
                                    iconSize: 48,
                                    icon: Icon(
                                      processingState == ProcessingState.loading ||
                                              processingState == ProcessingState.buffering
                                          ? Icons.hourglass_empty
                                          : isPlaying
                                              ? Icons.pause
                                              : Icons.play_arrow,
                                      color: const Color(0xFF0F3460),
                                    ),
                                    onPressed: () {
                                      if (isPlaying) {
                                        _audioPlayer.pause();
                                      } else {
                                        _audioPlayer.play();
                                      }
                                    },
                                  ),
                                ),
                                
                                const SizedBox(width: 20),
                                
                                // Next (disabled for now)
                                IconButton(
                                  iconSize: 48,
                                  icon: Icon(
                                    Icons.skip_next,
                                    color: Colors.white.withOpacity(0.3),
                                  ),
                                  onPressed: null,
                                ),
                              ],
                            );
                          },
                        ),
                        
                        const SizedBox(height: 60),
                      ],
                    ),
        ),
      ),
    );
  }
}
