import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/utils/responsive_helper.dart';
import 'song_detail_page.dart';

class SongListPage extends StatefulWidget {
  const SongListPage({Key? key}) : super(key: key);

  @override
  State<SongListPage> createState() => _SongListPageState();
}

class _SongListPageState extends State<SongListPage> {
  List<dynamic> _songs = [];
  List<dynamic> _filteredSongs = [];
  bool _isLoading = true;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchSongs();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _fetchSongs() async {
    setState(() => _isLoading = true);
    
    try {
      final response = await http.get(
        Uri.parse('http://72.61.143.174:5000///api/songs'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          setState(() {
            _songs = data['songs'] ?? [];
            _filteredSongs = _songs;
            _isLoading = false;
          });
        }
      } else {
        throw Exception('Failed to load songs');
      }
    } catch (e) {
      print('Error loading songs: $e');
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal memuat lagu: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _filterSongs(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredSongs = _songs;
      } else {
        _filteredSongs = _songs.where((song) {
          final title = song['title']?.toString().toLowerCase() ?? '';
          final artist = song['artist']?.toString().toLowerCase() ?? '';
          final searchLower = query.toLowerCase();
          return title.contains(searchLower) || artist.contains(searchLower);
        }).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: AppColors.backgroundGradient,
      ),
      child: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: EdgeInsets.all(ResponsiveHelper.mediumSpacing),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Daftar Lagu',
                    style: TextStyle(
                      color: AppColors.textWhite,
                      fontSize: ResponsiveHelper.fontSize(24),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: ResponsiveHelper.mediumSpacing),
                  
                  // Search Bar
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(
                        ResponsiveHelper.radius(12),
                      ),
                    ),
                    child: TextField(
                      controller: _searchController,
                      onChanged: _filterSongs,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Cari lagu atau artis...',
                        hintStyle: TextStyle(
                          color: Colors.white.withOpacity(0.6),
                        ),
                        prefixIcon: const Icon(
                          Icons.search,
                          color: Colors.white,
                        ),
                        suffixIcon: _searchController.text.isNotEmpty
                            ? IconButton(
                                icon: const Icon(
                                  Icons.clear,
                                  color: Colors.white,
                                ),
                                onPressed: () {
                                  _searchController.clear();
                                  _filterSongs('');
                                },
                              )
                            : null,
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(
                          horizontal: ResponsiveHelper.mediumSpacing,
                          vertical: ResponsiveHelper.mediumSpacing,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Song List
            Expanded(
              child: _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(
                        color: Colors.white,
                      ),
                    )
                  : _filteredSongs.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.music_off,
                                size: 64,
                                color: Colors.white.withOpacity(0.5),
                              ),
                              SizedBox(height: ResponsiveHelper.mediumSpacing),
                              Text(
                                _searchController.text.isEmpty
                                    ? 'Belum ada lagu'
                                    : 'Lagu tidak ditemukan',
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.7),
                                  fontSize: ResponsiveHelper.fontSize(16),
                                ),
                              ),
                            ],
                          ),
                        )
                      : RefreshIndicator(
  onRefresh: _fetchSongs,
  color: AppColors.cardLight, // Atau AppColors.textDark
  child: ListView.builder(
    padding: EdgeInsets.symmetric(
      horizontal: ResponsiveHelper.mediumSpacing,
    ),
    itemCount: _filteredSongs.length,
    itemBuilder: (context, index) {
      final song = _filteredSongs[index];
      return _buildSongCard(song);
    },
  ),
),

            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSongCard(Map<String, dynamic> song) {
    return Container(
      margin: EdgeInsets.only(bottom: ResponsiveHelper.mediumSpacing),
      decoration: BoxDecoration(
        color: AppColors.cardDark,
        borderRadius: BorderRadius.circular(ResponsiveHelper.radius(12)),
      ),
      child: ListTile(
        contentPadding: EdgeInsets.all(ResponsiveHelper.mediumSpacing),
        leading: Container(
          width: ResponsiveHelper.width(50),
          height: ResponsiveHelper.width(50),
          decoration: BoxDecoration(
            color: AppColors.cardLight.withOpacity(0.3),
            borderRadius: BorderRadius.circular(ResponsiveHelper.radius(8)),
          ),
          child: Icon(
            Icons.music_note,
            color: AppColors.textWhite,
            size: ResponsiveHelper.largeIcon,
          ),
        ),
        title: Text(
          song['title'] ?? 'Unknown Title',
          style: TextStyle(
            color: AppColors.textWhite,
            fontSize: ResponsiveHelper.fontSize(16),
            fontWeight: FontWeight.w600,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          song['artist'] ?? 'Unknown Artist',
          style: TextStyle(
            color: AppColors.textWhite.withOpacity(0.7),
            fontSize: ResponsiveHelper.fontSize(14),
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Icon(
          Icons.chevron_right,
          color: AppColors.textWhite,
          size: ResponsiveHelper.largeIcon,
        ),
        onTap: () {
          Navigator.pushNamed(
            context,
            '/song-detail',
            arguments: SongDetailArguments(
              songTitle: song['title'] ?? 'Unknown',
              realArtist: song['artist'] ?? 'Unknown Artist',
              realOriginalKey: song['original_key'] ?? 'C major',
              realUserKey: 'C major', // TODO: Get from user preferences
              coverImageUrl: null,
              audioUrl: song['audio_url'],
            ),
          );
        },
      ),
    );
  }
}
