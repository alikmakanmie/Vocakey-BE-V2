"""
Sync audio files from songs/original folder to database

This script will:
1. Scan songs/original folder for MP3 files
2. Update existing songs in database with audio_file_path
3. Auto-populate missing metadata
"""

import sqlite3
import os
import re

def get_safe_filename(title):
    """Convert title to safe filename format"""
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe

def parse_filename(filename):
    """
    Parse filename to extract title and artist
    
    Examples:
        "Bohemian_Rhapsody_Queen.mp3" -> ("Bohemian Rhapsody", "Queen")
        "Perfect_Ed_Sheeran.mp3" -> ("Perfect", "Ed Sheeran")
        "All_of_Me_John_Legend.mp3" -> ("All of Me", "John Legend")
    """
    # Remove .mp3 extension
    name = filename.replace('.mp3', '')
    
    # Split by underscore
    parts = name.split('_')
    
    if len(parts) >= 3:
        # Pattern: Song_Word_Artist_Name
        # Find common artist patterns (usually last 1-2 words)
        
        # Try common 2-word artists
        common_two_word = ['John Legend', 'Ed Sheeran', 'Taylor Swift', 
                          'Ariana Grande', 'Bruno Mars', 'Lady Gaga']
        
        two_word_artist = ' '.join(parts[-2:])
        
        if two_word_artist in common_two_word or len(parts) > 3:
            # Last 2 words are artist
            artist = two_word_artist
            title = ' '.join(parts[:-2])
        else:
            # Last 1 word is artist
            artist = parts[-1]
            title = ' '.join(parts[:-1])
            
    elif len(parts) == 2:
        # Pattern: Song_Artist
        title = parts[0]
        artist = parts[1]
    else:
        title = name.replace('_', ' ')
        artist = "Unknown Artist"
    
    return title, artist

def sync_audio_files():
    """Sync audio files from songs/original to database"""
    
    db_path = "songs.db"
    songs_folder = "songs/original"
    
    print("\n" + "=" * 70)
    print("🎵 Syncing Audio Files from Folder to Database")
    print("=" * 70)
    
    # Check if folder exists
    if not os.path.exists(songs_folder):
        print(f"\n❌ Folder not found: {songs_folder}")
        print(f"   Please create the folder and add MP3 files.")
        return
    
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(songs_folder) if f.endswith('.mp3')]
    
    if not mp3_files:
        print(f"\n❌ No MP3 files found in {songs_folder}")
        return
    
    print(f"\n📂 Found {len(mp3_files)} MP3 files in {songs_folder}\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get column names from songs table
    cursor.execute("PRAGMA table_info(songs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"📋 Database columns: {', '.join(columns)}\n")
    
    try:
        updated_count = 0
        added_count = 0
        skipped_count = 0
        
        for filename in mp3_files:
            # Parse filename
            title, artist = parse_filename(filename)
            audio_path = f"songs/original/{filename}"
            
            # Get file size
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            
            print(f"📄 Processing: {filename}")
            print(f"   Title: {title}")
            print(f"   Artist: {artist}")
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Check if song exists in database (check by title OR filename)
            cursor.execute("""
                SELECT id, audio_file_path 
                FROM songs 
                WHERE title = ? OR audio_file_path LIKE ?
            """, (title, f"%{filename}%"))
            existing = cursor.fetchone()
            
            if existing:
                song_id, current_path = existing
                
                if current_path and current_path != 'None' and current_path == audio_path:
                    print(f"   ⏭️  Already synced: {current_path}")
                    skipped_count += 1
                else:
                    # Update audio_file_path
                    cursor.execute("""
                        UPDATE songs 
                        SET audio_file_path = ?, 
                            file_size_mb = ?,
                            download_status = 'completed'
                        WHERE id = ?
                    """, (audio_path, file_size_mb, song_id))
                    
                    print(f"   ✅ Updated audio path (ID: {song_id})")
                    updated_count += 1
            else:
                # Add new song to database
                # Build INSERT query based on available columns
                
                base_fields = {
                    'title': title,
                    'artist': artist,
                    'key_note': 'C',
                    'audio_file_path': audio_path,
                    'file_size_mb': file_size_mb,
                    'download_status': 'completed'
                }
                
                # Add optional fields if they exist
                if 'pitch_range_acc' in columns:
                    base_fields['pitch_range_acc'] = 0.85  # Default accuracy
                
                if 'link_youtube' in columns:
                    base_fields['link_youtube'] = ''
                
                if 'cover_image_url' in columns:
                    base_fields['cover_image_url'] = ''
                
                if 'genre' in columns:
                    base_fields['genre'] = 'Pop'
                
                if 'tempo' in columns:
                    base_fields['tempo'] = 120
                
                if 'popularity_score' in columns:
                    base_fields['popularity_score'] = 50.0
                
                # Build query
                field_names = ', '.join(base_fields.keys())
                placeholders = ', '.join(['?' for _ in base_fields])
                values = tuple(base_fields.values())
                
                cursor.execute(f"""
                    INSERT INTO songs ({field_names})
                    VALUES ({placeholders})
                """, values)
                
                song_id = cursor.lastrowid
                print(f"   ✅ Added to database (ID: {song_id})")
                added_count += 1
            
            print()
        
        # Commit changes
        conn.commit()
        
        print("=" * 70)
        print(f"✅ Sync Complete!")
        print(f"   📊 Total files: {len(mp3_files)}")
        print(f"   ✅ Updated: {updated_count}")
        print(f"   ➕ Added: {added_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print("=" * 70)
        
        # Show all songs with audio
        print("\n📊 Songs in Database with Audio:\n")
        
        cursor.execute("""
            SELECT id, title, artist, audio_file_path, file_size_mb 
            FROM songs 
            WHERE audio_file_path IS NOT NULL AND audio_file_path != ''
            ORDER BY id
        """)
        
        songs = cursor.fetchall()
        
        for song_id, title, artist, audio_path, file_size in songs:
            exists = "✅" if os.path.exists(audio_path or '') else "❌"
            size_str = f"{file_size:.2f} MB" if file_size else "N/A"
            print(f"{exists} {song_id:3}. {title:35} - {artist:20} ({size_str})")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    sync_audio_files()
