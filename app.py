"""
VocaKey Backend - Pitch Detection & Vocal Analysis API
Menggunakan algoritma konvensional (pYIN) untuk deteksi pitch dari humming
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import traceback
import sqlite3  # ✅ ADD THIS


from pitch_detector import PitchDetector
from vocal_analyzer import VocalAnalyzer
from database_manager import DatabaseManager, db_manager  # ✅ Keep this
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

@app.route('/api/songs', methods=['POST'])
def add_song():
    """
    Add song to database and auto-download from YouTube
    Request (JSON):
    {
        "title": "Perfect",
        "artist": "Ed Sheeran",
        "key_note": "G",
        "link_youtube": "https://youtube.com/...",
        "genre": "Pop",
        "tempo": 95,
        "pitch_range_acc": "0.68",
        "popularity_score": "0.98"
    }
    Response:
    {
        "success": true,
        "message": "Song added and downloading",
        "song": {...}
    }
    """
    try:
        import yt_dlp
        from key_utils import normalize_key_name
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['title', 'artist', 'key_note', 'link_youtube']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Normalize key
        normalized_key = normalize_key_name(data['key_note'])
        
        # Create folders
        os.makedirs('songs/original', exist_ok=True)
        os.makedirs('songs/transposed', exist_ok=True)
        
        # Generate safe filename
        safe_title = ''.join(c for c in data['title'] if c.isalnum() or c in (' ', '_')).rstrip()
        safe_artist = ''.join(c for c in data['artist'] if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"{safe_title}_{safe_artist}".replace(' ', '_')
        output_path = f"songs/original/{filename}.mp3"
        
        # ✅ Check if song already exists
        existing = song_recommender.db_manager.get_song_by_title(data['title'])
        
        if existing and existing['artist'] == data['artist']:
            return jsonify({
                'success': False,
                'error': f'Song "{data["title"]}" by {data["artist"]} already exists',
                'existing_song': {
                    'id': existing['id'],
                    'title': existing['title'],
                    'artist': existing['artist'],
                    'key_note': existing['key_note'],
                    'download_status': 'completed'
                }
            }), 409
        
        # ✅ Add to database
        song_id = song_recommender.db_manager.add_song(
            title=data['title'],
            artist=data['artist'],
            key_note=normalized_key,
            audio_path=output_path,
            genre=data.get('genre', 'Unknown')
        )
        
        # Download from YouTube
        print(f"\n{'='*60}")
        print(f"[Download] Starting download: {data['title']} by {data['artist']}")
        print(f"[Download] YouTube URL: {data['link_youtube']}")
        print(f"[Download] Output: {output_path}")
        print(f"{'='*60}\n")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([data['link_youtube']])
            
            # Get file size
            file_size_bytes = os.path.getsize(output_path)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
            
            print(f"\n✅ Download completed!")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size_mb} MB\n")
            
            # Get song data
            song_data = song_recommender.db_manager.get_song_by_id(song_id)
            song_data['file_size_mb'] = file_size_mb
            song_data['download_status'] = 'completed'
            
            return jsonify({
                'success': True,
                'message': 'Song added and downloaded successfully',
                'song': song_data
            }), 201
            
        except Exception as download_error:
            print(f"\n❌ Download failed: {str(download_error)}\n")
            
            return jsonify({
                'success': False,
                'error': f'Failed to download audio: {str(download_error)}',
                'song_id': song_id
            }), 500
    
    except Exception as e:
        print(f"❌ Error adding song: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Failed to add song: {str(e)}'
        }), 500


@app.route('/api/songs/<int:song_id>/transpose', methods=['POST'])
def transpose_song_custom(song_id):
    """
    Transpose song with custom semitone shift
    Request (JSON):
    {
        "semitone_shift": -2,  // Negative = down, Positive = up
        "preserve_formant": true  // Optional, default = true
    }
    Response:
    {
        "success": true,
        "transposed_url": "http://192.168.3.2:5000/songs/transposed/...",
        "semitone_shift": -2,
        "direction": "down",
        "original_key": "G",
        "new_key": "F"
    }
    """
    try:
        import librosa
        import soundfile as sf
        from key_utils import transpose_key
        
        # ✅ Get song from database
        song = song_recommender.db_manager.get_song_by_id(song_id)
        
        if not song:
            return jsonify({
                'success': False,
                'error': f'Song with ID {song_id} not found'
            }), 404
        
        # Get request data
        data = request.get_json()
        if not data or 'semitone_shift' not in data:
            return jsonify({
                'success': False,
                'error': 'semitone_shift is required'
            }), 400
        
        semitone_shift = int(data['semitone_shift'])
        preserve_formant = data.get('preserve_formant', True)
        
        # Validate range
        if semitone_shift < -12 or semitone_shift > 12:
            return jsonify({
                'success': False,
                'error': 'semitone_shift must be between -12 and 12'
            }), 400
        
        if semitone_shift == 0:
            return jsonify({
                'success': False,
                'error': 'semitone_shift cannot be 0 (no transposition needed)'
            }), 400
        
        # Check if audio file exists
        if not song.get('audio_path') or not os.path.exists(song['audio_path']):
            return jsonify({
                'success': False,
                'error': f'Audio file not found for song "{song["title"]}". Download status: {song.get("download_status", "unknown")}'
            }), 404
        
        # Generate output filename
        direction = 'down' if semitone_shift < 0 else 'up'
        transposed_filename = f"{os.path.splitext(os.path.basename(song['audio_path']))[0]}_transpose_{semitone_shift}.mp3"
        transposed_path = os.path.join('songs/transposed', transposed_filename)
        
        # Check if already transposed (cache)
        if os.path.exists(transposed_path):
            print(f"✅ Transpose: Using cached version: {transposed_filename}")
            
            new_key = transpose_key(song['key_note'], semitone_shift)
            
            return jsonify({
                'success': True,
                'message': 'Transposed audio already exists (cached)',
                'transposed_url': f"http://{request.host}/songs/transposed/{transposed_filename}",
                'semitone_shift': semitone_shift,
                'direction': direction,
                'original_key': song['key_note'],
                'new_key': new_key,
                'song': {
                    'id': song['id'],
                    'title': song['title'],
                    'artist': song['artist']
                }
            }), 200
        
        # Load and transpose audio
        print(f"\n{'='*60}")
        print(f"[Transpose] Loading: {song['audio_path']}")
        y, sr = librosa.load(song['audio_path'], sr=16000, mono=True)
        
        print(f"[Transpose] Shifting by {semitone_shift} semitones ({direction})")
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitone_shift)
        
        # Save transposed audio
        sf.write(transposed_path, y_shifted, sr)
        
        file_size_bytes = os.path.getsize(transposed_path)
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
        
        print(f"✅ Transpose: Done! Size: {file_size_mb} MB")
        print(f"{'='*60}\n")
        
        new_key = transpose_key(song['key_note'], semitone_shift)
        
        return jsonify({
            'success': True,
            'message': 'Song transposed successfully',
            'transposed_url': f"http://{request.host}/songs/transposed/{transposed_filename}",
            'semitone_shift': semitone_shift,
            'direction': direction,
            'original_key': song['key_note'],
            'new_key': new_key,
            'file_size_mb': file_size_mb,
            'song': {
                'id': song['id'],
                'title': song['title'],
                'artist': song['artist']
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error transposing song: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Failed to transpose song: {str(e)}'
        }), 500


from flask import send_file
import os

# ✅ IMPROVED ENDPOINT
@app.route('/api/songs/<int:song_id>/audio', methods=['GET'])
def get_song_audio(song_id):
    """
    Serve audio file untuk lagu tertentu
    Contoh: /api/songs/1/audio
    """
    try:
        song = song_recommender.db_manager.get_song_by_id(song_id)
        
        if not song:
            print(f"❌ Song ID {song_id} not found in database")
            return jsonify({
                "success": False,
                "error": f"Song with ID {song_id} not found"
            }), 404
        
        print(f"✅ Found song: {song.get('title')}")
        
        audio_path = song.get('audio_path')
        
        if not audio_path:
            audio_path = os.path.join('songs', f"{song['title']}.mp3")
        
        # ✅ FOR TESTING: If file not exists, redirect to demo
        if not os.path.exists(audio_path):
            print(f"⚠️  Audio file not found: {audio_path}")
            print(f"✅ Using demo audio instead")
            
            # Return demo audio URL as redirect or JSON
            demo_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            
            return jsonify({
                "success": True,
                "audio_url": demo_url,
                "message": "Using demo audio (real file not found)",
                "song": {
                    "id": song['id'],
                    "title": song['title'],
                    "artist": song['artist']
                }
            }), 200
        
        # If file exists, serve it
        file_ext = os.path.splitext(audio_path)[1].lower()
        mimetype_map = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
        }
        mimetype = mimetype_map.get(file_ext, 'audio/mpeg')
        
        print(f"✅ Serving audio: {audio_path} ({mimetype})")
        return send_file(audio_path, mimetype=mimetype)
        
    except Exception as e:
        print(f"❌ Error serving audio: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# ✅ ENDPOINT: Get song by title
@app.route('/api/songs/by-title/<string:title>/audio', methods=['GET'])
def get_song_audio_by_title(title):
    """
    Serve audio file berdasarkan judul
    Contoh: /api/songs/by-title/Thinking Out Loud/audio
    """
    try:
        song = song_recommender.db_manager.get_song_by_title(title)
        
        if not song:
            return jsonify({
                "success": False,
                "error": f"Song '{title}' not found"
            }), 404
        
        # Redirect to ID-based endpoint
        return get_song_audio(song['id'])
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ✅ ENDPOINT: Demo audio (fallback untuk testing)
@app.route('/api/songs/demo/audio', methods=['GET'])
def get_demo_audio():
    """
    Return demo audio URL untuk testing
    """
    return jsonify({
        "success": True,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "message": "This is a demo audio file"
    }), 200


# ✅ ENDPOINT: List all songs
@app.route('/api/songs', methods=['GET'])
def list_songs():
    """
    List semua lagu di database
    """
    try:
        conn = sqlite3.connect(song_recommender.db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, artist, key_note, audio_path FROM songs")
        rows = cursor.fetchall()
        conn.close()
        
        songs = [dict(row) for row in rows]
        
        return jsonify({
            "success": True,
            "count": len(songs),
            "songs": songs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/songs/<path:subpath>/<filename>')
def serve_audio(subpath, filename):
    """
    Serve audio files from songs folder
    Example: /songs/transposed/perfect_transpose_2.mp3
    """
    try:
        directory = os.path.join('songs', subpath)
        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File not found: {str(e)}'
        }), 404

@app.route('/songs/file/<string:title>', methods=['GET'])
def get_song_file_by_title(title):
    """
    Serve audio file by matching title only
    
    Example:
        GET /songs/file/Shallow
        -> Returns songs/original/Shallow_Lady_Gaga__Bradley_Cooper.mp3
    """
    try:
        print(f"\n🔍 Looking for audio file matching title: {title}")
        
        songs_folder = 'songs/original'
        
        if not os.path.exists(songs_folder):
            return jsonify({
                'success': False,
                'error': 'Songs folder not found'
            }), 404
        
        # Get all MP3 files
        mp3_files = [f for f in os.listdir(songs_folder) if f.endswith('.mp3')]
        
        # Normalize title for matching
        normalized_title = title.lower().replace('_', '').replace(' ', '')
        
        # Find matching file
        for filename in mp3_files:
            # Extract title part from filename (before first underscore or artist name)
            file_title_part = filename.split('_')[0].lower()
            
            # Also try matching the whole filename start
            filename_normalized = filename.lower().replace('_', '').replace(' ', '')
            
            if (file_title_part == title.lower() or 
                filename_normalized.startswith(normalized_title)):
                
                print(f"✅ Found matching file: {filename}")
                
                # Serve the file
                return send_from_directory(songs_folder, filename)
        
        # If no match found
        print(f"❌ No file found matching: {title}")
        print(f"   Available files: {mp3_files}")
        
        return jsonify({
            'success': False,
            'error': f'No audio file found for "{title}"'
        }), 404
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/songs/search/<string:title>', methods=['GET'])
def search_song_by_title(title):
    """
    Get song details and audio URL by title
    
    Returns song metadata + actual audio file path
    """
    try:
        print(f"\n🔍 Searching for song: {title}")
        
        # Search in database
        song = song_recommender.db_manager.get_song_by_title(title)
        
        if not song:
            # Try fuzzy search
            all_songs = song_recommender.db_manager.get_all_songs()
            title_lower = title.lower()
            
            for s in all_songs:
                if title_lower in s['title'].lower():
                    song = s
                    break
        
        if not song:
            return jsonify({
                'success': False,
                'error': f'Song "{title}" not found'
            }), 404
        
        # Find actual audio file
        audio_url = None
        songs_folder = 'songs/original'
        
        if os.path.exists(songs_folder):
            mp3_files = [f for f in os.listdir(songs_folder) if f.endswith('.mp3')]
            
            # Match by title
            title_normalized = song['title'].lower().replace(' ', '')
            
            for filename in mp3_files:
                filename_normalized = filename.lower().replace('_', '').replace(' ', '')
                
                if filename_normalized.startswith(title_normalized):
                    audio_url = f"/songs/original/{filename}"
                    break
        
        # Use database path as fallback
        if not audio_url:
            audio_url = song.get('audio_file_path') or song.get('audio_path')
        
        print(f"✅ Found: {song['title']} -> {audio_url}")
        
        return jsonify({
            'success': True,
            'song': {
                **song,
                'audio_url': audio_url
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/songs/search/<string:title>/transpose', methods=['POST'])
def transpose_song_by_title(title):
    """Transpose song audio by title"""
    try:
        import librosa
        import soundfile as sf
        from key_utils import transpose_key
        
        data = request.get_json()
        semitone_shift = data.get('semitone_shift', 0)
        preserve_formant = data.get('preserve_formant', True)
        
        print(f"\n🎵 Transpose Request:")
        print(f"   Title: {title}")
        print(f"   Shift: {semitone_shift} semitones")
        
        if semitone_shift == 0:
            return jsonify({'success': False, 'error': 'No transpose needed'}), 400
        
        # Find song
        song = song_recommender.db_manager.get_song_by_title(title)
        
        if not song:
            all_songs = song_recommender.db_manager.get_all_songs()
            title_lower = title.lower()
            for s in all_songs:
                if title_lower in s['title'].lower():
                    song = s
                    break
        
        if not song:
            return jsonify({'success': False, 'error': f'Song "{title}" not found'}), 404
        
        # Find audio file
        original_audio_path = None
        songs_folder = 'songs/original'
        
        if os.path.exists(songs_folder):
            mp3_files = [f for f in os.listdir(songs_folder) if f.endswith('.mp3')]
            title_normalized = song['title'].lower().replace(' ', '')
            
            for filename in mp3_files:
                filename_normalized = filename.lower().replace('_', '').replace(' ', '')
                if filename_normalized.startswith(title_normalized):
                    original_audio_path = os.path.join(songs_folder, filename)
                    break
        
        if not original_audio_path:
            original_audio_path = song.get('audio_file_path') or song.get('audio_path')
        
        if not original_audio_path or not os.path.exists(original_audio_path):
            return jsonify({'success': False, 'error': 'Audio file not found'}), 404
        
        print(f"✅ Found: {original_audio_path}")
        
        # Generate output path
        transposed_folder = 'songs/transposed'
        os.makedirs(transposed_folder, exist_ok=True)
        
        base_filename = os.path.splitext(os.path.basename(original_audio_path))[0]
        shift_str = f"+{semitone_shift}" if semitone_shift > 0 else str(semitone_shift)
        transposed_filename = f"{base_filename}_transpose_{shift_str}.wav"
        transposed_path = os.path.join(transposed_folder, transposed_filename)
        
        # Check cache
        if os.path.exists(transposed_path):
            print(f"✅ Using cached: {transposed_path}")
        else:
            print(f"🎵 Transposing...")
            
            # Load and transpose
            y, sr = librosa.load(original_audio_path, sr=None)
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitone_shift)
            sf.write(transposed_path, y_shifted, sr)
            
            print(f"✅ Saved: {transposed_path}")
        
        # Calculate new key
        original_key = song.get('key_note', 'C') + ' major'
        new_key = transpose_key(original_key, semitone_shift)
        
        # Response
        transposed_url = f"http://192.168.3.2:5000/songs/transposed/{transposed_filename}"
        
        return jsonify({
            'success': True,
            'transposed_url': transposed_url,
            'original_key': original_key,
            'new_key': new_key,
            'semitone_shift': semitone_shift
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/songs/transposed/<filename>')
def serve_transposed_file(filename):
    """Serve transposed audio files"""
    try:
        transposed_folder = 'songs/transposed'
        
        if not os.path.exists(os.path.join(transposed_folder, filename)):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_from_directory(transposed_folder, filename)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
