class ApiConstants {
  // Base URL - Cloudflare Tunnel (tanpa trailing slash)
  static const String baseUrl = 'http://72.61.143.174:5000/';
  
  // Endpoints
  static const String analyzeEndpoint = '/api/analyze'; // ✅ CORRECT
  static const String songsEndpoint = '/api/songs';        // ✅ NEW
  
  // Full URLs
  static String get analyzePitchUrl => '$baseUrl$analyzeEndpoint';
  static String get getSongsUrl => '$baseUrl$songsEndpoint';
  
  // Headers
  static const Map<String, String> headers = {
    'Accept': 'application/json',
  };
  
  // Recording settings
  static const int maxRecordDuration = 30; // seconds (updated to 30)
  static const String audioFormat = 'wav';
}
