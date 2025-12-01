"""
Re-download all songs from database

Usage:
    python redownload_songs.py
"""

import os
import sys
from database_manager import db_manager
from database_models import Song

def redownload_all_songs():
    """
    Re-download audio files for all songs in database
    """
    try:
        import yt_dlp
    except ImportError:
        print("❌ Error: yt-dlp not installed!")
        print("   Run: pip install yt-dlp")
        sys.exit(1)
    
    # Create folders
    os.makedirs('songs/original', exist_ok=True)
    
    print("\n" + "="*60)
    print("🔄 Re-downloading All Songs")
    print("="*60 + "\n")
    
    session = db_manager.get_session()
    songs = session.query(Song).all()
    
    if not songs:
        print("❌ No songs found in database!")
        session.close()
        return
    
    print(f"📊 Found {len(songs)} songs in database\n")
    
    success_count = 0
    failed_count = 0
    
    for idx, song in enumerate(songs, 1):
        print(f"[{idx}/{len(songs)}] {song.title} by {song.artist}")
        
        try:
            # Generate filename
            safe_title = "".join(c for c in song.title if c.isalnum() or c in (' ', '_')).rstrip()
            safe_artist = "".join(c for c in song.artist if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{safe_title}_{safe_artist}".replace(' ', '_')
            output_path = f'songs/original/{filename}.mp3'
            
            # Delete old file if exists
            if os.path.exists(output_path):
                os.remove(output_path)
                print(f"   🗑️  Deleted old file")
            
            # Download from YouTube
            print(f"   📥 Downloading...")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song.link_youtube])
            
            # Get file size
            if os.path.exists(output_path):
                file_size_bytes = os.path.getsize(output_path)
                file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
                
                # Update database
                song.audio_file_path = output_path
                song.file_size_mb = file_size_mb
                song.download_status = 'completed'
                session.commit()
                
                print(f"   ✅ Downloaded: {file_size_mb} MB")
                success_count += 1
            else:
                song.download_status = 'failed'
                session.commit()
                print(f"   ❌ Download failed: File not found")
                failed_count += 1
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            song.download_status = 'failed'
            session.commit()
            failed_count += 1
        
        print()
    
    session.close()
    
    # Summary
    print("="*60)
    print("📊 Re-download Summary")
    print("="*60)
    print(f"✅ Success: {success_count} songs")
    print(f"❌ Failed:  {failed_count} songs")
    print(f"📁 Audio files location: songs/original/")
    print("="*60 + "\n")

if __name__ == '__main__':
    redownload_all_songs()
