"""
Update audio_path for all songs in database

Usage:
    python update_audio_paths.py
"""

import sqlite3
import os

def update_audio_paths():
    """Update audio_path for songs that don't have it"""
    
    db_path = "songs.db"
    
    print("\n" + "=" * 60)
    print("🔧 Updating Audio Paths")
    print("=" * 60 + "\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all songs
        cursor.execute("SELECT id, title, artist, audio_path FROM songs")
        songs = cursor.fetchall()
        
        updated_count = 0
        
        for song_id, title, artist, audio_path in songs:
            if not audio_path or audio_path == 'None':
                # Generate audio path
                safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '_')).strip()
                safe_title = safe_title.replace(' ', '_').lower()
                
                new_audio_path = f"songs/{safe_title}.mp3"
                
                # Update database
                cursor.execute("UPDATE songs SET audio_path = ? WHERE id = ?", 
                             (new_audio_path, song_id))
                
                print(f"✅ Updated: {title} -> {new_audio_path}")
                updated_count += 1
            else:
                print(f"⏭️  Skipped: {title} (already has: {audio_path})")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Updated {updated_count} song(s)")
        print("=" * 60)
        
        # Show all songs
        cursor.execute("SELECT id, title, audio_path FROM songs")
        all_songs = cursor.fetchall()
        
        print("\n📊 All songs in database:\n")
        for song_id, title, audio_path in all_songs:
            status = "✅" if audio_path and audio_path != 'None' else "❌"
            print(f"  {status} {song_id}. {title:30} -> {audio_path or 'NO PATH'}")
        
        print()
        
    except sqlite3.Error as e:
        print(f"\n❌ Update failed: {str(e)}\n")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == '__main__':
    update_audio_paths()
