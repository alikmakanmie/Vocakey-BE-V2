"""
VocaKey Backend - Pitch Detection & Vocal Analysis API
Menggunakan algoritma konvensional (pYIN) untuk deteksi pitch dari humming
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import traceback

from pitch_detector import PitchDetector
from vocal_analyzer import VocalAnalyzer
from song_recommender import SongRecommender

# ===== KONFIGURASI =====
app = Flask(__name__)
CORS(app)  # Enable CORS untuk Flutter

# Folder untuk menyimpan audio upload sementara
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'webm'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Buat folder uploads jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inisialisasi komponen
pitch_detector = PitchDetector()
vocal_analyzer = VocalAnalyzer()
song_recommender = SongRecommender()

# ===== HELPER FUNCTIONS =====

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_file(filepath):
    """Delete temporary file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

# ===== API ENDPOINTS =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'VocaKey API is running',
        'version': '1.0.0',
        'algorithms': ['pYIN', 'YIN', 'YAAPT'],
        'features': [
            'Pitch Detection',
            'Vocal Range Analysis',
            'Key Detection',
            'Song Recommendation'
        ]
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_vocal():
    """
    Analyze vocal/humming audio and provide recommendations

    Request:
        - audio: Audio file (required)
        - get_recommendations: bool (optional, default: true)
        - max_recommendations: int (optional, default: 10)

    Response:
        {
            "success": true,
            "vocal_analysis": {...},
            "recommended_songs": [...]
        }
    """

    audio_file = None
    filepath = None

    try:
        # Validasi request
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400

        if not allowed_file(audio_file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Parse parameters
        get_recommendations = request.form.get('get_recommendations', 'true').lower() == 'true'
        max_recommendations = int(request.form.get('max_recommendations', 10))

        # Save file temporarily
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)

        # ===== STEP 1: PITCH DETECTION =====
        print(f"[1/4] Detecting pitch from: {filename}")
        pitch_data = pitch_detector.detect_pitch(filepath)

        if not pitch_data['success']:
            cleanup_file(filepath)
            return jsonify({
                'success': False,
                'error': pitch_data['error']
            }), 400

        # ===== STEP 2: VOCAL ANALYSIS =====
        print(f"[2/4] Analyzing vocal characteristics...")
        vocal_analysis = vocal_analyzer.analyze(pitch_data)

        # ===== STEP 3: SONG RECOMMENDATION =====
        recommended_songs = []
        if get_recommendations:
            print(f"[3/4] Finding compatible songs...")
            recommended_songs = song_recommender.recommend(
                vocal_analysis,
                max_results=max_recommendations
            )

        print(f"[4/4] Analysis complete! Found {len(recommended_songs)} recommendations")

        # Cleanup
        cleanup_file(filepath)

        # ===== RESPONSE =====
        return jsonify({
            'success': True,
            'vocal_analysis': vocal_analysis,
            'recommended_songs': recommended_songs,
            'metadata': {
                'audio_duration': pitch_data['metadata']['duration'],
                'sample_rate': pitch_data['metadata']['sample_rate'],
                'algorithm': 'pYIN'
            }
        })

    except Exception as e:
        # Cleanup on error
        if filepath:
            cleanup_file(filepath)

        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())

        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint untuk debugging"""
    return jsonify({
        'message': 'Test endpoint working',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    })

# ===== ERROR HANDLERS =====

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ===== RUN SERVER =====

if __name__ == '__main__':
    print("=" * 60)
    print("🎵 VocaKey Backend - Starting Server...")
    print("=" * 60)
    print("📍 Server URL: http://localhost:5000")
    print("📚 API Endpoints:")
    print("   - GET  /api/health  → Health check")
    print("   - POST /api/analyze → Analyze vocal & get recommendations")
    print("   - GET  /api/test    → Test endpoint")
    print("=" * 60)
    print()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
