import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/services/local_storage_service.dart';
import '../../domain/entities/analysis_result.dart';
import '../../../music/presentation/pages/simple_audio_player_page.dart';

class PitchResultPage extends StatefulWidget {
  final AnalysisResult result;

  const PitchResultPage({
    Key? key,
    required this.result,
  }) : super(key: key);

  @override
  State<PitchResultPage> createState() => _PitchResultPageState();
}

class _PitchResultPageState extends State<PitchResultPage> {
  YoutubePlayerController? youtubeController;
  int selectedSongIndex = 0;

  @override
  void initState() {
    super.initState();
    printResultToConsole();
    saveAnalysisResult();
    initializeYoutubePlayer();
  }

  void printResultToConsole() {
    print('============================================================');
    print('🎵 PITCH ANALYSIS RESULT (v2.0)');
    print('============================================================');
    print('📌 Base Note      : ${widget.result.baseNote}');
    print('📊 Base Frequency : ${widget.result.baseFrequency} Hz');
    print('🎹 Song Key       : ${widget.result.fullKey}');
    print('🎯 Confidence     : ${widget.result.confidencePercentage.toStringAsFixed(1)}%');
    print('🎼 Recommendations: ${widget.result.recommendations.length} songs');

    if (widget.result.recommendations.isNotEmpty) {
      print('📀 Recommended Songs:');
      for (int i = 0; i < widget.result.recommendations.length; i++) {
        final song = widget.result.recommendations[i];
        print('   ${i + 1}. ${song.title} - ${song.artist} (Score: ${song.matchScore.toStringAsFixed(1)})');
      }
    }
    print('============================================================');
  }

  Future<void> saveAnalysisResult() async {
    try {
      await LocalStorageService.saveLastAnalysis(
        note: widget.result.fullKey, // ✅ Save song key instead of base note
        vocalRange: widget.result.fullKey,
        accuracy: widget.result.confidencePercentage,
        vocalType: 'Unknown',
      );
      print('✅ Analysis result saved to local storage');
    } catch (e) {
      print('Error saving analysis result: $e');
    }
  }

  void initializeYoutubePlayer() {
    if (widget.result.recommendations.isNotEmpty) {
      final firstSong = widget.result.recommendations[0];
      final videoId = firstSong.videoId;

      if (videoId != null && videoId.isNotEmpty) {
        youtubeController = YoutubePlayerController(
          initialVideoId: videoId,
          flags: const YoutubePlayerFlags(
            autoPlay: false,
            mute: false,
            enableCaption: false,
          ),
        );
      }
    }
  }

  void changeSong(int index) {
    final song = widget.result.recommendations[index];
    final videoId = song.videoId;

    if (videoId != null && videoId.isNotEmpty) {
      setState(() {
        selectedSongIndex = index;
      });
      youtubeController?.load(videoId);
    }
  }

  Future<void> openInYouTube(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Tidak dapat membuka YouTube')),
        );
      }
    }
  }

  void playRecommendedSong(SongRecommendation song) {
    final title = song.title;
    final artist = song.artist;
    final detectedKey = song.detectedKey ?? 'Unknown';

    String audioPath = song.audioPath ?? '';
    print('Raw audiopath from recommendation: $audioPath');

    String audioUrl = '';
    if (audioPath.isNotEmpty && audioPath != '') {
      final filename = audioPath.split('/').last;
      audioUrl = 'audio/$filename';
      print('Using audiopath filename: $filename');
    } else {
      String filename = '${title}_$artist.mp3'
          .replaceAll(' ', '_')
          .replaceAll(RegExp(r'[^a-zA-Z0-9_.]'), '');
      audioUrl = 'audio/$filename';
      print('Generated filename: $filename');
    }

    if (audioUrl.startsWith('/') && ApiConstants.baseUrl.endsWith('/')) {
      audioUrl = audioUrl.substring(1);
    }

    final String fullAudioUrl = audioUrl.startsWith('http')
        ? audioUrl
        : '${ApiConstants.baseUrl}$audioUrl';

    print('Opening audio player for: $title');
    print('Full Audio URL: $fullAudioUrl');

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SimpleAudioPlayerPage(
          audioUrl: fullAudioUrl,
          title: title,
          artist: artist,
          originalKey: detectedKey,
        ),
      ),
    );
  }

  @override
  void dispose() {
    youtubeController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final hasRecommendations = widget.result.recommendations.isNotEmpty;

    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppColors.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Column(
                    children: [
                      const SizedBox(height: 20),
                      _buildResultCard(),
                      const SizedBox(height: 24),
                      if (hasRecommendations && youtubeController != null)
                        _buildVideoPlayer(),
                      const SizedBox(height: 16),
                      if (hasRecommendations)
                        _buildRecommendationsList()
                      else
                        _buildNoRecommendations(),
                      const SizedBox(height: 32),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => Navigator.pop(context),
          ),
          const SizedBox(width: 8),
          const Text(
            'Hasil Analisis',
            style: TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.home, color: Colors.white),
            onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
          ),
        ],
      ),
    );
  }

  Widget _buildResultCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.white.withOpacity(0.95),
            Colors.white.withOpacity(0.9),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF6B9FE8).withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.music_note_rounded,
              size: 48,
              color: Color(0xFF6B9FE8),
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Kunci Lagu Anda',
            style: TextStyle(
              color: Colors.black54,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          // ✅ Display fullKey (G# major) instead of baseNote (C2)
          Text(
            widget.result.fullKey,
            style: const TextStyle(
              color: Colors.black87,
              fontSize: 48,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 8),
          // ✅ Show base note as subtitle
          Text(
            'Nada Dasar: ${widget.result.baseNote} (${widget.result.baseFrequency.toStringAsFixed(2)} Hz)',
            style: const TextStyle(
              color: Colors.black54,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 24),
          Container(height: 1, color: Colors.black12),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildInfoChip(
                icon: Icons.piano,
                label: 'Kunci',
                value: widget.result.fullKey,
              ),
              _buildInfoChip(
                icon: Icons.bar_chart,
                label: 'Kepercayaan',
                value: '${widget.result.confidencePercentage.toStringAsFixed(0)}%',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoChip({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, color: const Color(0xFF6B9FE8), size: 28),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(
            color: Colors.black54,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.black87,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildVideoPlayer() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: YoutubePlayer(
          controller: youtubeController!,
          showVideoProgressIndicator: true,
          progressIndicatorColor: const Color(0xFF6B9FE8),
          bottomActions: [
            CurrentPosition(),
            ProgressBar(
              isExpanded: true,
              colors: const ProgressBarColors(
                playedColor: Color(0xFF6B9FE8),
                handleColor: Color(0xFF6B9FE8),
              ),
            ),
            RemainingDuration(),
            FullScreenButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationsList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Row(
            children: [
              const Icon(
                Icons.queue_music_rounded,
                color: Colors.white,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'Lagu yang Direkomendasikan (${widget.result.recommendations.length})',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20),
          itemCount: widget.result.recommendations.length,
          itemBuilder: (context, index) {
            final song = widget.result.recommendations[index];
            final isSelected = index == selectedSongIndex;
            return _buildSongCard(song, index, isSelected);
          },
        ),
      ],
    );
  }

  Widget _buildSongCard(SongRecommendation song, int index, bool isSelected) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isSelected
            ? const Color(0xFF6B9FE8).withOpacity(0.3)
            : Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isSelected
              ? const Color(0xFF6B9FE8)
              : Colors.white.withOpacity(0.2),
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => playRecommendedSong(song),
          onLongPress: () => changeSong(index),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: song.hasThumbnail
                      ? Image.network(
                          song.thumbnail!,
                          width: 60,
                          height: 60,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => _buildPlaceholderImage(),
                        )
                      : _buildPlaceholderImage(),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        song.title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        song.artist,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.7),
                          fontSize: 14,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Icon(
                            Icons.piano,
                            size: 14,
                            color: Colors.white.withOpacity(0.6),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            song.detectedKey ?? 'Unknown',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.6),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Icon(
                            Icons.stars,
                            size: 14,
                            color: Colors.yellow.shade700,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            song.matchScore.toStringAsFixed(0),
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Column(
                  children: [
                    IconButton(
                      icon: const Icon(
                        Icons.play_circle_filled,
                        color: Colors.white,
                        size: 32,
                      ),
                      onPressed: () => playRecommendedSong(song),
                      tooltip: 'Putar audio',
                    ),
                    IconButton(
                      icon: const Icon(
                        Icons.open_in_new,
                        color: Colors.white70,
                        size: 20,
                      ),
                      onPressed: () => openInYouTube(song.youtubeWatchUrl),
                      tooltip: 'Buka di YouTube',
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholderImage() {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: const Color(0xFF6B9FE8).withOpacity(0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(
        Icons.music_note,
        color: Colors.white,
        size: 32,
      ),
    );
  }

  Widget _buildNoRecommendations() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(
            Icons.music_off,
            color: Colors.white.withOpacity(0.5),
            size: 64,
          ),
          const SizedBox(height: 16),
          Text(
            'Tidak Ada Rekomendasi',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Coba rekam lagi dengan suara yang lebih jelas',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white.withOpacity(0.6),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
