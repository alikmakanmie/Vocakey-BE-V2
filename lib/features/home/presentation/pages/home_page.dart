import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/utils/responsive_helper.dart';
import '../bloc/home_bloc.dart';
import '../bloc/home_event.dart';
import '../bloc/home_state.dart';
import '../widgets/song_card.dart';
import '../../../music/presentation/pages/simple_audio_player_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<dynamic> _songs = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    // ✅ Load last analysis
    context.read<HomeBloc>().add(LoadLastAnalysisEvent());
    _fetchSongs();
  }

  Future<void> _fetchSongs() async {
    try {
      print('🔄 Fetching songs from backend...');
      
      final response = await http.get(
        Uri.parse('${ApiConstants.baseUrl}api/songs?limit=30'),
      );

      print('📥 Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        if (data['success'] == true) {
          setState(() {
            _songs = data['songs'] ?? [];
            _isLoading = false;
          });
          print('✅ Loaded ${_songs.length} songs');
        }
      }
    } catch (e) {
      print('❌ Error loading songs: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: double.infinity,
      decoration: const BoxDecoration(
        gradient: AppColors.backgroundGradient,
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: EdgeInsets.only(
            left: ResponsiveHelper.mediumSpacing,
            right: ResponsiveHelper.mediumSpacing,
            top: ResponsiveHelper.mediumSpacing,
            bottom: 100,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Center(
                child: Text(
                  'VocaKey',
                  style: TextStyle(
                    color: AppColors.textWhite,
                    fontSize: ResponsiveHelper.fontSize(28),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(height: ResponsiveHelper.largeSpacing),

              // Riwayat Nada Dasar Title
              Text(
                'Riwayat Nada Dasar',
                style: TextStyle(
                  color: AppColors.textWhite,
                  fontSize: ResponsiveHelper.fontSize(18),
                  fontWeight: FontWeight.w600,
                ),
              ),
              SizedBox(height: ResponsiveHelper.mediumSpacing),

              // ✅ BlocBuilder untuk display data
              BlocBuilder<HomeBloc, HomeState>(
                builder: (context, state) {
                  String displayNote = 'C2';
                  String displaySubtext = 'Unknown major • 0.0%';

                  if (state is HomeAnalysisLoaded) {
                    displayNote = state.note;
                    if (state.vocalRange != 'Belum Dianalisis' &&
                        state.vocalRange != 'Unknown') {
                      displaySubtext =
                          '${state.vocalRange} • ${state.accuracy.toStringAsFixed(1)}%';
                    }
                  }

                  return Container(
                    width: double.infinity,
                    padding: EdgeInsets.all(ResponsiveHelper.largeSpacing),
                    decoration: BoxDecoration(
                      color: AppColors.cardLight,
                      borderRadius: BorderRadius.circular(
                        ResponsiveHelper.radius(20),
                      ),
                    ),
                    child: Column(
                      children: [
                        Text(
                          displaySubtext,
                          style: TextStyle(
                            color: AppColors.textDark.withOpacity(0.7),
                            fontSize: ResponsiveHelper.fontSize(14),
                          ),
                        ),
                        SizedBox(height: ResponsiveHelper.smallSpacing),
                        Text(
                          displayNote,
                          style: TextStyle(
                            color: AppColors.textDark,
                            fontSize: ResponsiveHelper.fontSize(36),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
              SizedBox(height: ResponsiveHelper.xLargeSpacing),

              // Daftar Lagu Section
              Text(
                'Daftar Lagu Popular',
                style: TextStyle(
                  color: AppColors.textWhite,
                  fontSize: ResponsiveHelper.fontSize(18),
                  fontWeight: FontWeight.w600,
                ),
              ),
              SizedBox(height: ResponsiveHelper.mediumSpacing),

              // Horizontal Scrollable Song Cards
              _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(color: Colors.white),
                    )
                  : _songs.isEmpty
                      ? Center(
                          child: Text(
                            'No songs available',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.7),
                              fontSize: 16,
                            ),
                          ),
                        )
                      : SizedBox(
                          height: ResponsiveHelper.height(200),
                          child: ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: _songs.length,
                            itemBuilder: (context, index) {
                              final song = _songs[index];
                              return Padding(
                                padding: EdgeInsets.only(
                                  right: ResponsiveHelper.mediumSpacing,
                                ),
                                child: SongCard(
                                  title: song['title'] ?? 'Unknown',
                                  artist: song['artist'] ?? 'Unknown Artist',
                                  onTap: () => _onSongTap(song),
                                ),
                              );
                            },
                          ),
                        ),
            ],
          ),
        ),
      ),
    );
  }

  // ✅ Handle song tap with proper audio URL generation
  void _onSongTap(Map<String, dynamic> song) {
    final title = song['title'] ?? 'Unknown';
    final artist = song['artist'] ?? 'Unknown Artist';
    String audioUrl = song['audio_url'] ?? '';
    final originalNote = song['original_note'] ?? 'Unknown';

    print('🔍 Raw audio_url from backend: "$audioUrl"');

    // ✅ FALLBACK: Generate audio URL if empty
    if (audioUrl.isEmpty || audioUrl == '/') {
      // Try to match filename pattern from server
      // Format: "Title_Artist.mp3" with proper capitalization
      String filename = '${title}_${artist}.mp3'
          .replaceAll(' ', '_')
          .replaceAll(RegExp(r'[^a-zA-Z0-9_.]'), '');
      
      audioUrl = '/audio/$filename';
      print('🔧 Generated audio URL: $audioUrl');
    }

    // Remove leading slash if baseUrl already has trailing slash
    if (audioUrl.startsWith('/') && ApiConstants.baseUrl.endsWith('/')) {
      audioUrl = audioUrl.substring(1);
    }

    // Construct full audio URL
    final String fullAudioUrl = audioUrl.startsWith('http')
        ? audioUrl
        : '${ApiConstants.baseUrl}$audioUrl';

    print('🎵 Opening player for: $title');
    print('🎵 Full Audio URL: $fullAudioUrl');

    // ✅ Navigate to audio player
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SimpleAudioPlayerPage(
          audioUrl: fullAudioUrl,
          title: title,
          artist: artist,
          originalKey: originalNote,
        ),
      ),
    );
  }
}
