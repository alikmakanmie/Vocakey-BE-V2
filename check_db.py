# check_db.py
from database_manager import db_manager
from database_models import Song

session = db_manager.get_session()
songs = session.query(Song).all()

print(f"\n{'='*60}")
print(f"📊 Database Status Check")
print(f"{'='*60}")
print(f"Total songs in database: {len(songs)}")

if len(songs) > 0:
    print(f"\n✅ Database contains {len(songs)} songs:\n")
    for song in songs:
        print(f"  {song.id}. {song.title:<25} by {song.artist:<20} | Key: {song.key_note:<3} | Genre: {song.genre}")
else:
    print(f"\n❌ Database is EMPTY!")
    print(f"   Run: python seed_database.py")

print(f"{'='*60}\n")

session.close()
