from database_manager import DatabaseManager
import os

def populate_sample_songs():
    """Add sample songs to database"""
    db = DatabaseManager("songs.db")
    
    # Create songs folder if not exists
    os.makedirs('songs', exist_ok=True)
    
    sample_songs = [
        {
            "title": "Perfect",
            "artist": "Ed Sheeran",
            "key_note": "Ab",
            "scale": "major",
            "audio_path": "songs/perfect.mp3",
            "vocal_range_min": "F3",
            "vocal_range_max": "Bb4",
            "difficulty": "Medium",
            "genre": "Pop"
        },
        {
            "title": "Thinking Out Loud",
            "artist": "Ed Sheeran",
            "key_note": "D",
            "scale": "major",
            "audio_path": "songs/thinking_out_loud.mp3",
            "vocal_range_min": "A2",
            "vocal_range_max": "D4",
            "difficulty": "Easy",
            "genre": "Pop"
        },
        {
            "title": "Someone Like You",
            "artist": "Adele",
            "key_note": "A",
            "scale": "major",
            "audio_path": "songs/someone_like_you.mp3",
            "vocal_range_min": "E3",
            "vocal_range_max": "C#5",
            "difficulty": "Medium",
            "genre": "Pop"
        },
        {
            "title": "All of Me",
            "artist": "John Legend",
            "key_note": "Ab",
            "scale": "major",
            "audio_path": "songs/all_of_me.mp3",
            "vocal_range_min": "C3",
            "vocal_range_max": "Eb5",
            "difficulty": "Hard",
            "genre": "R&B"
        },
    ]
    
    print("=" * 60)
    print("Adding sample songs to database...")
    print("=" * 60)
    
    for song in sample_songs:
        # Check if song already exists
        existing = db.get_song_by_title(song['title'])
        
        if existing:
            print(f"⏭️  Skipped: {song['title']} (already exists)")
        else:
            song_id = db.add_song(**song)
            print(f"✅ Added: {song['title']} by {song['artist']} (ID: {song_id})")
    
    print("=" * 60)
    print("✅ Database populated!")
    print("=" * 60)
    
    # List all songs
    all_songs = db.get_all_songs()
    print(f"\n📊 Total songs in database: {len(all_songs)}\n")
    
    for song in all_songs:
        print(f"  {song['id']}. {song['title']} - {song['artist']} (Key: {song['key_note']})")

if __name__ == "__main__":
    populate_sample_songs()
