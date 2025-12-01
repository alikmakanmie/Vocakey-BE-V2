"""
Retry downloading failed songs

Usage:
    python retry_failed_downloads.py
"""

import os
import sys
from database_manager import db_manager
from database_models import Song

def retry_failed_downloads():
    """
    Retry downloading songs with download_status = 'failed'
    """
    try:
        import yt_dlp
    except ImportError:
        print("❌ Error: yt-dlp not installed!")
        sys.exit(1)
    
    os.makedirs('songs/original', exist_ok=True)
    
    print("\n" + "="*60)
    print("🔄 Retrying Failed Downloads")
    print("="*60 + "\n")
    
    session = db_manager.get_session()
    
    # Get songs with failed download
    failed_songs = session.query(Song).filter_by(download_status='failed').all()
    
    if not failed_songs:
        print("✅ No failed downloads found!")
        session.close()
        return
    
    print(f"📊 Found {len(failed_songs)} failed downloads\n")
    
    success_count = 0
    failed_count = 0
    
    for idx, song in enumerate(failed_songs, 1):
        print(f"[{idx}/{len(failed_songs)}] Retrying: {song.title} by {song.artist}")
        
        try:
            # Generate filename
            safe_title = "".join(c for c in song.title if c.isalnum() or c in (' ', '_')).rstrip()
            safe_artist = "".join(c for c in song.artist if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{safe_title}_{safe_artist}".replace(' ', '_')
            output_path = f'songs/original/{filename}.mp3'
            
            # Download from YouTube with retry
            print(f"   📥 Downloading (with retry)...")
            
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
                'retries': 10,                    # Retry 10x
                'fragment_retries': 10,           # Retry fragment 10x
                'socket_timeout': 60,             # Timeout 60s (lebih lama)
                'http_chunk_size': 1048576,       # Download 1MB chunk (lebih kecil, lebih stable)
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
                print(f"   ❌ Download failed: File not found")
                failed_count += 1
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            failed_count += 1
        
        print()
    
    session.close()
    
    # Summary
    print("="*60)
    print("📊 Retry Summary")
    print("="*60)
    print(f"✅ Success: {success_count} songs")
    print(f"❌ Failed:  {failed_count} songs")
    print(f"📁 Audio files location: songs/original/")
    print("="*60 + "\n")

if __name__ == '__main__':
    retry_failed_downloads()
