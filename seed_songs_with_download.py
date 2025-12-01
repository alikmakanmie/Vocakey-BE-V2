"""
Database Seeder with Auto-Download from YouTube

Usage:
    python seed_songs_with_download.py
"""

import os
import sys
from database_manager import db_manager
from database_models import Song
from key_utils import normalize_key_name

def seed_songs_with_download():
    """
    Seed database with songs and auto-download audio from YouTube
    """
    try:
        import yt_dlp
    except ImportError:
        print("❌ Error: yt-dlp not installed!")
        print("   Run: pip install yt-dlp")
        sys.exit(1)
    
    # Create folders
    os.makedirs('songs/original', exist_ok=True)
    os.makedirs('songs/transposed', exist_ok=True)
    
    # Sample songs with YouTube links
    songs_data = [
        {
            'title': 'Perfect',
            'artist': 'Ed Sheeran',
            'key_note': 'G',
            'link_youtube': 'https://www.youtube.com/watch?v=2Vv-BfVoq4g',
            'genre': 'Pop',
            'tempo': 95,
            'pitch_range_acc': 0.68,
            'popularity_score': 0.98
        },
        {
            'title': 'Someone Like You',
            'artist': 'Adele',
            'key_note': 'A',
            'link_youtube': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0',
            'genre': 'Pop Ballad',
            'tempo': 67,
            'pitch_range_acc': 0.75,
            'popularity_score': 0.95
        },
        {
            'title': 'Shape of You',
            'artist': 'Ed Sheeran',
            'key_note': 'C#',
            'link_youtube': 'https://www.youtube.com/watch?v=JGwWNGJdvx8',
            'genre': 'Pop',
            'tempo': 96,
            'pitch_range_acc': 0.72,
            'popularity_score': 0.97
        },
        {
            'title': 'All of Me',
            'artist': 'John Legend',
            'key_note': 'G#',
            'link_youtube': 'https://www.youtube.com/watch?v=450p7goxZqg',
            'genre': 'R&B/Soul',
            'tempo': 120,
            'pitch_range_acc': 0.70,
            'popularity_score': 0.94
        },
        {
            'title': 'Thinking Out Loud',
            'artist': 'Ed Sheeran',
            'key_note': 'D',
            'link_youtube': 'https://www.youtube.com/watch?v=lp-EO5I60KA',
            'genre': 'Pop/Soul',
            'tempo': 79,
            'pitch_range_acc': 0.65,
            'popularity_score': 0.96
        },
        {
            'title': 'Let It Be',
            'artist': 'The Beatles',
            'key_note': 'C',
            'link_youtube': 'https://www.youtube.com/watch?v=QDYfEBY9NM4',
            'genre': 'Rock/Pop',
            'tempo': 73,
            'pitch_range_acc': 0.62,
            'popularity_score': 0.99
        },
        {
            'title': 'Hallelujah',
            'artist': 'Leonard Cohen',
            'key_note': 'C',
            'link_youtube': 'https://www.youtube.com/watch?v=ttEMYvpoR-k',
            'genre': 'Folk',
            'tempo': 58,
            'pitch_range_acc': 0.58,
            'popularity_score': 0.93
        },
        {
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'key_note': 'A#',
            'link_youtube': 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ',
            'genre': 'Rock',
            'tempo': 144,
            'pitch_range_acc': 0.80,
            'popularity_score': 1.0
        },
        {
            'title': 'Wonderwall',
            'artist': 'Oasis',
            'key_note': 'A',
            'link_youtube': 'https://www.youtube.com/watch?v=bx1Bh8ZvH84',
            'genre': 'Rock',
            'tempo': 87,
            'pitch_range_acc': 0.65,
            'popularity_score': 0.92
        },
        {
            'title': 'Shallow',
            'artist': 'Lady Gaga & Bradley Cooper',
            'key_note': 'A#',
            'link_youtube': 'https://www.youtube.com/watch?v=bo_efYhYU2A',
            'genre': 'Pop',
            'tempo': 96,
            'pitch_range_acc': 0.72,
            'popularity_score': 0.95
        }
    ]
    
    print("\n" + "="*60)
    print("🎵 VocaKey - Database Seeding with Auto-Download")
    print("="*60 + "\n")
    
    session = db_manager.get_session()
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for idx, song_data in enumerate(songs_data, 1):
        print(f"\n[{idx}/{len(songs_data)}] Processing: {song_data['title']} by {song_data['artist']}")
        
        try:
            # Check if song already exists
            existing = session.query(Song).filter_by(
                title=song_data['title'],
                artist=song_data['artist']
            ).first()
            
            if existing:
                print(f"⏭️  Skipped: Song already exists (ID: {existing.id})")
                skipped_count += 1
                continue
            
            # Normalize key
            normalized_key = normalize_key_name(song_data['key_note'])
            
            # Generate safe filename
            safe_title = "".join(c for c in song_data['title'] if c.isalnum() or c in (' ', '_')).rstrip()
            safe_artist = "".join(c for c in song_data['artist'] if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{safe_title}_{safe_artist}".replace(' ', '_')
            output_path = f'songs/original/{filename}.mp3'
            
            # Download audio from YouTube
            print(f"   📥 Downloading from YouTube...")
            
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
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([song_data['link_youtube']])
                
                # Get file size
                if os.path.exists(output_path):
                    file_size_bytes = os.path.getsize(output_path)
                    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
                    download_status = 'completed'
                else:
                    file_size_mb = None
                    download_status = 'failed'
                
                print(f"   ✅ Downloaded: {file_size_mb} MB")
                
            except Exception as download_error:
                print(f"   ❌ Download failed: {str(download_error)}")
                file_size_mb = None
                download_status = 'failed'
            
            # Create song object
            song = Song(
                title=song_data['title'],
                artist=song_data['artist'],
                key_note=normalized_key,
                link_youtube=song_data['link_youtube'],
                genre=song_data.get('genre', 'Unknown'),
                tempo=song_data.get('tempo', 120),
                pitch_range_acc=song_data.get('pitch_range_acc', 0.5),
                popularity_score=song_data.get('popularity_score', 0.5),
                audio_file_path=output_path,
                file_size_mb=file_size_mb,
                download_status=download_status
            )
            
            # Add to database
            session.add(song)
            session.commit()
            
            if download_status == 'completed':
                print(f"   ✅ Added to database (ID: {song.id})")
                success_count += 1
            else:
                print(f"   ⚠️  Added to database but download failed (ID: {song.id})")
                failed_count += 1
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            session.rollback()
            failed_count += 1
    
    session.close()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Seeding Summary")
    print("="*60)
    print(f"✅ Success: {success_count} songs")
    print(f"⏭️  Skipped: {skipped_count} songs (already exists)")
    print(f"❌ Failed:  {failed_count} songs")
    print(f"📁 Audio files location: songs/original/")
    print("="*60 + "\n")

if __name__ == '__main__':
    seed_songs_with_download()
