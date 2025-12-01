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
from song_recommender_sqlite import SongRecommenderSQLite

# ===== KONFIGURASI =====
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'webm'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== Inisialisasi komponen =====
pitch_detector = PitchDetector()
vocal_analyzer = VocalAnalyzer()
song_recommender = SongRecommenderSQLite()

print("✅ PitchDetector initialized")
print("✅ VocalAnalyzer initialized")
print("✅ SongRecommenderSQLite initialized")

# ===== HELPER FUNCTIONS =====

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Cleaned up: {filepath}")
    except Exception as e:
        print(f"⚠️ Failed to cleanup {filepath}: {e}")

# ===== ROUTES =====

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'VocaKey API',
        'version': '1.0.0'
    }), 200

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'message': 'VocaKey API is running!',
        'endpoints': {
            'health': '/api/health',
            'analyze': '/api/analyze (POST)',
            'test': '/api/test'
        }
    }), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_vocal():
    audio_file = None
    filepath = None
    
    try:
        # ===== STEP 0: VALIDATE REQUEST =====
        print("\n" + "="*60)
        print("[DEBUG] Starting /api/analyze request")
        print("="*60)
        
        if 'audio' not in request.files:
            print("[ERROR] No audio file in request")
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        print(f"[DEBUG] Audio file received: {audio_file.filename}")
        
        if audio_file.filename == '':
            print("[ERROR] Empty filename")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not allowed_file(filename):
            print(f"[ERROR] Invalid file type: {filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400
        
        audio_file.save(filepath)
        print(f"[DEBUG] File saved to: {filepath}")
        
        # Get optional parameters
        get_recommendations = request.form.get('get_recommendations', 'true').lower() == 'true'
        max_recommendations = int(request.form.get('max_recommendations', 10))
        
        print(f"[DEBUG] Parameters:")
        print(f"  - get_recommendations: {get_recommendations}")
        print(f"  - max_recommendations: {max_recommendations}")
        
        # ===== STEP 1: PITCH DETECTION =====
        print(f"\n[1/4] Detecting pitch from: {filename}")
        pitch_data = pitch_detector.detect_pitch(filepath)
        
        print(f"[DEBUG] Pitch detection result:")
        print(f"  - success: {pitch_data.get('success')}")
        print(f"  - keys: {list(pitch_data.keys())}")
        
        if not pitch_data['success']:
            error_msg = pitch_data.get('error', 'Pitch detection failed')
            print(f"[ERROR] Pitch detection failed: {error_msg}")
            cleanup_file(filepath)
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # ===== STEP 2: VOCAL ANALYSIS =====
        print(f"\n[2/4] Analyzing vocal characteristics...")
        print(f"[DEBUG] Calling vocal_analyzer.analyze()...")
        
        try:
            vocal_analysis = vocal_analyzer.analyze(pitch_data)
            print(f"[DEBUG] Vocal analysis complete")
            print(f"  - type: {type(vocal_analysis)}")
            print(f"  - keys: {list(vocal_analysis.keys()) if isinstance(vocal_analysis, dict) else 'NOT A DICT'}")
        except Exception as e:
            print(f"[ERROR] Vocal analysis failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            cleanup_file(filepath)
            return jsonify({
                'success': False,
                'error': f'Vocal analysis failed: {str(e)}'
            }), 400
        
        # ===== STEP 3: SONG RECOMMENDATION =====
        recommended_songs = []
        if get_recommendations:
            print(f"\n[3/4] Finding compatible songs...")
            print(f"[DEBUG] Calling song_recommender.recommend()...")
            
            try:
                recommended_songs = song_recommender.recommend(
                    vocal_analysis,
                    max_results=max_recommendations
                )
                print(f"[DEBUG] Recommendation complete: {len(recommended_songs)} songs")
            except Exception as e:
                print(f"[ERROR] Recommendation failed: {str(e)}")
                import traceback
                print(traceback.format_exc())
                # Don't return error, just continue with empty recommendations
                recommended_songs = []
        
        print(f"\n[4/4] Analysis complete! Found {len(recommended_songs)} recommendations")
        
        # Cleanup uploaded file
        cleanup_file(filepath)
        
        # ===== STEP 4: BUILD RESPONSE =====
        print("\n[DEBUG] Building response...")
        
        # 1. Extract key/note info
        key_info = vocal_analysis.get("key", {})
        note_str = "Unknown"
        accuracy = 0.0
        
        print(f"[DEBUG] key_info: {key_info}")
        
        if isinstance(key_info, dict):
            key_name = key_info.get("key", "")
            scale = key_info.get("scale", "")
            confidence = key_info.get("confidence", 0.0)
            
            if key_name:
                note_str = f"{key_name} {scale}".strip()
            
            accuracy = confidence * 100  # Convert to percentage
        
        # 2. Extract pitch range
        pitch_range = vocal_analysis.get("pitch_range", {})
        lowest = "Unknown"
        highest = "Unknown"
        
        print(f"[DEBUG] pitch_range: {pitch_range}")
        
        if isinstance(pitch_range, dict):
            notes_dict = pitch_range.get("notes", {})
            if isinstance(notes_dict, dict):
                lowest = notes_dict.get("min", "Unknown")
                highest = notes_dict.get("max", "Unknown")
        
        # 3. Extract vocal type
        vocal_classification = vocal_analysis.get("vocal_classification", {})
        vocal_type_str = "Unknown"
        
        print(f"[DEBUG] vocal_classification: {vocal_classification}")
        
        if isinstance(vocal_classification, dict):
            vocal_type_str = vocal_classification.get("primary", "Unknown")
        
        # 4. Extract statistics
        statistics = vocal_analysis.get("statistics", {})
        
        # Debug print
        print(f"\n[DEBUG] Final response data:")
        print(f"  - Note: {note_str}")
        print(f"  - Range: {lowest} - {highest}")
        print(f"  - Accuracy: {accuracy}%")
        print(f"  - Vocal Type: {vocal_type_str}")
        print(f"  - Recommendations: {len(recommended_songs)}")
        
        # ===== RETURN RESPONSE =====
        response_data = {
            'success': True,
            'data': {
                'note': note_str,
                'vocal_range': f"{lowest} - {highest}",
                'accuracy': float(accuracy),
                'vocal_type': vocal_type_str
            },
            'recommendations': [
                {
                    'title': song.get('title', 'Unknown'),
                    'artist': song.get('artist', 'Unknown'),
                    'original_note': song.get('key_note', 'Unknown'),
                    'match_score': song.get('compatibility_score', {}).get('total', 0) 
                        if isinstance(song.get('compatibility_score'), dict) else 0
                }
                for song in recommended_songs
            ],
            'metadata': {
                'audio_duration': pitch_data.get('metadata', {}).get('duration', 0),
                'sample_rate': pitch_data.get('metadata', {}).get('sample_rate', 0),
                'algorithm': 'pYIN',
                'num_samples': statistics.get('num_samples', 0) if isinstance(statistics, dict) else 0
            }
        }
        
        print(f"\n[DEBUG] Returning response with status 200")
        print("="*60 + "\n")
        
        return jsonify(response_data), 200
    
    except Exception as e:
        # Cleanup on error
        if filepath and os.path.exists(filepath):
            cleanup_file(filepath)
        
        # Print detailed error
        print("\n" + "=" * 60)
        print("❌ UNHANDLED EXCEPTION")
        print("=" * 60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\n--- Full Traceback ---")
        print(traceback.format_exc())
        print("=" * 60 + "\n")
        
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'error_type': type(e).__name__
        }), 500



# ===== ENDPOINT: TRANSPOSE AUDIO =====

@app.route('/api/transpose/audio', methods=['POST'])
def transpose_audio_endpoint():
    """
    Transpose audio file dari original key ke target key
    
    Request (multipart/form-data):
        - audio: File audio (required)
        - original_key: Original key (required)
        - target_key: Target key (required)
        - preserve_formant: Boolean (optional, default: true)
    
    Response:
        {
            "success": true,
            "semitone_shift": 2,
            "transposed_audio_url": "/uploads/...",
            "quality": {...}
        }
    """
    
    audio_file = None
    filepath = None
    output_file = None
    
    try:
        # Import transpose_audio function
        from transpose_audio import transpose_audio
        
        # Validate request
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        original_key = request.form.get('original_key')
        target_key = request.form.get('target_key')
        preserve_formant = request.form.get('preserve_formant', 'true').lower() == 'true'
        
        if not original_key or not target_key:
            return jsonify({
                'success': False,
                'error': 'original_key and target_key are required'
            }), 400
        
        if not allowed_file(audio_file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save input file
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        # Transpose audio
        print(f"[Transpose] {original_key} → {target_key}")
        output_file, transpose_info = transpose_audio(
            filepath,
            original_key,
            target_key,
            preserve_formant=preserve_formant
        )
        
        # Generate URL
        output_filename = os.path.basename(output_file)
        transposed_url = f"/uploads/{output_filename}"
        
        # Cleanup original file
        cleanup_file(filepath)
        
        # Response
        return jsonify({
            'success': True,
            'original_key': transpose_info['original_key'],
            'target_key': transpose_info['target_key'],
            'semitone_shift': transpose_info['semitone_shift'],
            'direction': transpose_info['direction'],
            'transposed_audio_url': transposed_url,
            'quality': transpose_info['quality'],
            'audio_info': transpose_info['audio_info']
        })
    
    except ValueError as e:
        if filepath:
            cleanup_file(filepath)
        if output_file:
            cleanup_file(output_file)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        if filepath:
            cleanup_file(filepath)
        if output_file:
            cleanup_file(output_file)
        
        print(f"❌ Transpose Error: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


# ===== RUN SERVER =====

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎵 VocaKey Backend - Starting Server...")
    print("=" * 60)
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"📡 API Endpoints:")
    print(f"   - GET  /api/health  → Health check")
    print(f"   - POST /api/analyze → Analyze vocal & get recommendations")
    print(f"   - POST /api/transpose/audio → Transpose audio file")
    print(f"   - GET  /api/test    → Test endpoint")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)


# ===== ENDPOINT: TRANSPOSE AUDIO =====


# ===== RUN SERVER =====
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎵 VocaKey Backend - Starting Server...")
    print("="*60)
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"📡 API Endpoints:")
    print(f"   - GET  /api/health  → Health check")
    print(f"   - POST /api/analyze → Analyze vocal & get recommendations")
    print(f"   - GET  /api/test    → Test endpoint")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
