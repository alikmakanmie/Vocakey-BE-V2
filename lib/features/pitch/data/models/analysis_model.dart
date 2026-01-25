import '../../domain/entities/analysis_result.dart';

/// Model untuk response API analisis vokal
/// ✅ UPDATED: Compatible dengan K-S Algorithm backend (v3.0)
class AnalysisModel extends AnalysisResult {
  const AnalysisModel({
    required String baseNote,
    required double baseFrequency,
    required String songKey,
    required String songScale,
    required double keyConfidence,
    required List<SongRecommendation> recommendations,
  }) : super(
          baseNote: baseNote,
          baseFrequency: baseFrequency,
          songKey: songKey,
          songScale: songScale,
          keyConfidence: keyConfidence,
          recommendations: recommendations,
        );

  /// ✅ FIXED: Parse dari JSON response backend K-S algorithm
  factory AnalysisModel.fromJson(Map<String, dynamic> json) {
    print('=== PARSING ANALYSIS RESULT (K-S v3.0) ===');

    // Parse data object
    final data = json['data'] as Map<String, dynamic>? ?? {};

    // ✅ Extract base note & frequency
    final String baseNote = data['base_note'] as String? ?? 'Unknown';
    final double baseFrequency =
        (data['base_frequency'] as num?)?.toDouble() ?? 0.0;

    // ✅ FIXED: Parse song_key object (nested structure)
    final songKeyData = data['song_key'] as Map<String, dynamic>? ?? {};
    
    // Get full key string (e.g., "G major")
    final String fullKey = songKeyData['full_key'] as String? ?? 
                           songKeyData['key'] as String? ?? 
                           'Unknown major';
    
    // Split "G major" into key="G" and scale="major"
    final keyParts = fullKey.trim().split(' ');
    final String songKey = keyParts.isNotEmpty ? keyParts[0] : 'Unknown';
    final String songScale = keyParts.length > 1 ? keyParts[1] : 'major';

    // ✅ FIXED: Get confidence from song_key object
    final double keyConfidence =
        (songKeyData['confidence'] as num?)?.toDouble() ?? 0.0;

    // ✅ Parse recommendations from data.recommendations
    List<SongRecommendation> recommendations = [];
    if (data['recommendations'] != null) {
      try {
        final recs = data['recommendations'] as List;
        recommendations = recs.map((song) {
          return SongRecommendation.fromJson(song as Map<String, dynamic>);
        }).toList();
        print('✓ Parsed ${recommendations.length} recommendations');
      } catch (e) {
        print('❌ Error parsing recommendations: $e');
      }
    }

    print('Parsed data:');
    print('   - Base Note: $baseNote');
    print('   - Base Frequency: $baseFrequency Hz');
    print('   - Full Key: $fullKey');
    print('   - Song Key: $songKey');
    print('   - Song Scale: $songScale');
    print('   - Key Confidence: ${(keyConfidence * 100).toStringAsFixed(1)}%');
    print('   - Recommendations: ${recommendations.length} songs');
    print('=====================================');

    return AnalysisModel(
      baseNote: baseNote,
      baseFrequency: baseFrequency,
      songKey: songKey,
      songScale: songScale,
      keyConfidence: keyConfidence,
      recommendations: recommendations,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'data': {
        'base_note': baseNote,
        'base_frequency': baseFrequency,
        'song_key': {
          'key': '$songKey $songScale',
          'full_key': '$songKey $songScale',
          'confidence': keyConfidence,
        },
        'recommendations': recommendations.map((r) => r.toJson()).toList(),
      },
    };
  }

  @override
  String toString() {
    return 'AnalysisModel(baseNote: $baseNote, songKey: $songKey $songScale, recommendations: ${recommendations.length})';
  }
}
