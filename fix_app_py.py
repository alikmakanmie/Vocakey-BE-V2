"""
Fix app.py indentation and remove broken transpose functions
Then add clean versions
"""

def fix_app():
    # Read current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where to insert new functions (before if __name__)
    insert_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("if __name__ == '__main__':"):
            insert_index = i
            break
    
    if insert_index == -1:
        print("❌ Could not find if __name__ == '__main__'")
        return
    
    # Remove old broken transpose functions
    cleaned_lines = []
    skip_until_next_route = False
    
    for line in lines[:insert_index]:
        # Skip lines between broken transpose functions
        if "transpose_song_by_title" in line or "serve_transposed_file" in line:
            skip_until_next_route = True
            continue
        
        if skip_until_next_route:
            # Continue skipping until we find next @app.route or if __name__
            if line.strip().startswith('@app.route') or line.strip().startswith('if __name__'):
                skip_until_next_route = False
                cleaned_lines.append(line)
            continue
        
        cleaned_lines.append(line)
    
    # Add new clean transpose functions
    new_functions = '''
# ============================================================
# TRANSPOSE ENDPOINTS
# ============================================================

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
        
        print(f"\\n🎵 Transpose Request:")
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


'''
    
    # Combine all
    final_lines = cleaned_lines + [new_functions] + lines[insert_index:]
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    
    print("✅ Fixed app.py!")
    print(f"   Removed broken functions")
    print(f"   Added clean transpose endpoints")
    print(f"   Total lines: {len(final_lines)}")

if __name__ == "__main__":
    fix_app()
