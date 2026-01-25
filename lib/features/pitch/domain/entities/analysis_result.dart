import 'package:equatable/equatable.dart';

/// Entity untuk hasil analisis vokal (Domain Layer)
///
/// ✅ UPDATED v3.0 - Compatible dengan K-S Algorithm Backend:
/// - Support format backend baru (K-S database)
/// - Keep backward compatibility dengan format lama (YouTube Music)
class AnalysisResult extends Equatable {
  /// Nada dasar dari humming (e.g., "G4", "C#5")
  final String baseNote;

  /// Frekuensi nada dasar dalam Hz (e.g., 392.00)
  final double baseFrequency;

  /// Key lagu yang terdeteksi (e.g., "G", "C#")
  final String songKey;

  /// Scale lagu (major/minor)
  final String songScale;

  /// Confidence score key detection (0.0 - 1.0)
  final double keyConfidence;

  /// List rekomendasi lagu
  final List<SongRecommendation> recommendations;

  const AnalysisResult({
    required this.baseNote,
    required this.baseFrequency,
    required this.songKey,
    required this.songScale,
    required this.keyConfidence,
    required this.recommendations,
  });

  /// Full key description (e.g., "G major", "C# minor")
  String get fullKey => '$songKey $songScale';

  /// Confidence dalam persentase (0-100%)
  double get confidencePercentage => keyConfidence * 100;

  @override
  List<Object?> get props => [
        baseNote,
        baseFrequency,
        songKey,
        songScale,
        keyConfidence,
        recommendations,
      ];

  @override
  String toString() {
    return 'AnalysisResult(baseNote: $baseNote, songKey: $fullKey, recommendations: ${recommendations.length} songs)';
  }
}

/// Entity untuk song recommendation
/// ✅ UPDATED: Support both YouTube Music API and K-S Database format
class SongRecommendation extends Equatable {
  final String title;
  final String artist;
  final String youtubeUrl;
  final String youtubeWatchUrl;
  final String duration;
  final String? thumbnail;
  final String? album;
  final double matchScore;
  
  // ✅ NEW: Additional fields for K-S format
  final String? detectedKey;      // Detected key dari backend (e.g., "G major")
  final String? audioPath;        // Audio file path di server

  const SongRecommendation({
    required this.title,
    required this.artist,
    required this.youtubeUrl,
    required this.youtubeWatchUrl,
    required this.duration,
    this.thumbnail,
    this.album,
    required this.matchScore,
    this.detectedKey,
    this.audioPath,
  });

  /// ✅ UPDATED: Parse dari JSON dengan support 2 format
  factory SongRecommendation.fromJson(Map<String, dynamic> json) {
    // Detect format type
    final bool isNewFormat = json.containsKey('detected_key'); // K-S format
    final bool isYouTubeMusicFormat = json.containsKey('youtube_watch_url'); // Old format

    if (isNewFormat) {
      // ✅ NEW FORMAT (dari K-S database)
      print('   [Song] Parsing K-S format: ${json['title']}');
      return SongRecommendation(
        title: json['title'] as String? ?? 'Unknown',
        artist: json['artist'] as String? ?? 'Unknown',
        // ✅ NEW: audio_path stored in both youtubeUrl and audioPath
        youtubeUrl: json['audio_path'] as String? ?? '',
        // ✅ Real YouTube link (if available)
        youtubeWatchUrl: json['youtube_url'] as String? ?? '',
        duration: 'Unknown', // Backend belum return duration untuk K-S format
        thumbnail: null, // Backend belum return thumbnail untuk K-S format
        album: null,
        matchScore: (json['compatibility_score'] as num?)?.toDouble() ?? 
                    (json['match_score'] as num?)?.toDouble() ?? 0.0,
        // ✅ NEW: K-S specific fields
        detectedKey: json['detected_key'] as String?,
        audioPath: json['audio_path'] as String?,
      );
    } else if (isYouTubeMusicFormat) {
      // OLD FORMAT (YouTube Music API - backward compatibility)
      print('   [Song] Parsing YouTube Music format: ${json['title']}');
      return SongRecommendation(
        title: json['title'] as String? ?? 'Unknown',
        artist: json['artist'] as String? ?? 'Unknown',
        youtubeUrl: json['youtube_url'] as String? ?? '',
        youtubeWatchUrl: json['youtube_watch_url'] as String? ?? '',
        duration: json['duration'] as String? ?? 'Unknown',
        thumbnail: json['thumbnail'] as String?,
        album: json['album'] as String?,
        matchScore: (json['match_score'] as num?)?.toDouble() ?? 0.0,
        detectedKey: null,
        audioPath: null,
      );
    } else {
      // FALLBACK: Minimal parsing
      print('   [Song] Parsing unknown format: ${json['title']}');
      return SongRecommendation(
        title: json['title'] as String? ?? 'Unknown',
        artist: json['artist'] as String? ?? 'Unknown',
        youtubeUrl: json['youtube_url'] as String? ?? '',
        youtubeWatchUrl: json['youtube_url'] as String? ?? '',
        duration: json['duration'] as String? ?? 'Unknown',
        thumbnail: json['thumbnail'] as String?,
        album: json['album'] as String?,
        matchScore: (json['match_score'] as num?)?.toDouble() ?? 0.0,
        detectedKey: null,
        audioPath: null,
      );
    }
  }

  /// ✅ toJson method untuk serialization
  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'artist': artist,
      'youtube_url': youtubeUrl,
      'youtube_watch_url': youtubeWatchUrl,
      'duration': duration,
      'thumbnail': thumbnail,
      'album': album,
      'match_score': matchScore,
      'detected_key': detectedKey,
      'audio_path': audioPath,
    };
  }

  /// Extract YouTube video ID
  String? get videoId {
    try {
      final uri = Uri.parse(youtubeWatchUrl);
      return uri.queryParameters['v'];
    } catch (e) {
      return null;
    }
  }

  /// Check if thumbnail available
  bool get hasThumbnail => thumbnail != null && thumbnail!.isNotEmpty;

  /// Match score in percentage (0-100%)
  int get matchPercentage => (matchScore * 100).round();

  @override
  List<Object?> get props => [
        title,
        artist,
        youtubeUrl,
        youtubeWatchUrl,
        duration,
        thumbnail,
        album,
        matchScore,
        detectedKey,
        audioPath,
      ];

  @override
  String toString() {
    return 'SongRecommendation(title: $title, artist: $artist, matchScore: ${matchScore.toStringAsFixed(1)})';
  }
}
