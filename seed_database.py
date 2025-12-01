"""
Seed Database Script
File: seed_database.py
Jalankan sekali untuk populate database dengan sample songs
"""

from database_manager import db_manager
from database_models import Song

def seed_songs():
    """Populate database dengan sample songs"""
    
    session = db_manager.get_session()
    
    # Sample songs data
    sample_songs = [
        {
            'title': 'Perfect',
            'artist': 'Ed Sheeran',
            'key_note': 'G',
            'pitch_range_acc': 0.75,
            'link_youtube': 'https://www.youtube.com/watch?v=2Vv-BfVoq4g',
            'genre': 'Pop',
            'tempo': 95,
            'popularity_score': 0.95
        },
        {
            'title': 'Someone Like You',
            'artist': 'Adele',
            'key_note': 'A',
            'pitch_range_acc': 0.82,
            'link_youtube': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0',
            'genre': 'Pop Ballad',
            'tempo': 67,
            'popularity_score': 0.92
        },
        {
            'title': 'Shape of You',
            'artist': 'Ed Sheeran',
            'key_note': 'C#',
            'pitch_range_acc': 0.68,
            'link_youtube': 'https://www.youtube.com/watch?v=JGwWNGJdvx8',
            'genre': 'Pop',
            'tempo': 96,
            'popularity_score': 0.98
        },
        {
            'title': 'All of Me',
            'artist': 'John Legend',
            'key_note': 'Ab',
            'pitch_range_acc': 0.78,
            'link_youtube': 'https://www.youtube.com/watch?v=450p7goxZqg',
            'genre': 'R&B/Soul',
            'tempo': 120,
            'popularity_score': 0.89
        },
        {
            'title': 'Thinking Out Loud',
            'artist': 'Ed Sheeran',
            'key_note': 'D',
            'pitch_range_acc': 0.72,
            'link_youtube': 'https://www.youtube.com/watch?v=lp-EO5I60KA',
            'genre': 'Pop/Soul',
            'tempo': 79,
            'popularity_score': 0.91
        },
        {
            'title': 'Let It Be',
            'artist': 'The Beatles',
            'key_note': 'C',
            'pitch_range_acc': 0.70,
            'link_youtube': 'https://www.youtube.com/watch?v=QDYfEBY9NM4',
            'genre': 'Rock/Pop',
            'tempo': 76,
            'popularity_score': 0.96
        },
        {
            'title': 'Hallelujah',
            'artist': 'Leonard Cohen',
            'key_note': 'C',
            'pitch_range_acc': 0.65,
            'link_youtube': 'https://www.youtube.com/watch?v=YrLk4vdY28Q',
            'genre': 'Folk',
            'tempo': 60,
            'popularity_score': 0.88
        },
        {
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'key_note': 'Bb',
            'pitch_range_acc': 0.95,
            'link_youtube': 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ',
            'genre': 'Rock',
            'tempo': 144,
            'popularity_score': 0.99
        }
    ]
    
    # Add songs to database
    for song_data in sample_songs:
        song = Song(**song_data)
        session.add(song)
    
    session.commit()
    session.close()
    
    print(f"✅ Successfully seeded {len(sample_songs)} songs to database")
    print("   Database file: songs.db")

if __name__ == '__main__':
    print("=" * 60)
    print("🎵 VocaKey - Database Seeding")
    print("=" * 60)
    
    seed_songs()
    
    print("=" * 60)
    print("✅ Done! You can now run the server.")
    print("=" * 60)
