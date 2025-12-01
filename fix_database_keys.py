# fix_database_keys.py
from database_manager import db_manager
from database_models import Song

# Mapping flat to sharp (Mayor notation)
FLAT_TO_SHARP = {
    'Ab': 'G#',
    'Bb': 'A#',
    'Db': 'C#',
    'Eb': 'D#',
    'Gb': 'F#',
    'Fb': 'E',
    'Cb': 'B'
}

session = db_manager.get_session()

print(f"\n{'='*60}")
print(f"🔧 Converting Database Keys to Mayor Notation (Sharp)")
print(f"{'='*60}\n")

# Get all songs
songs = session.query(Song).all()
updated_count = 0

for song in songs:
    original_key = song.key_note
    
    # Check if key needs conversion
    if original_key in FLAT_TO_SHARP:
        new_key = FLAT_TO_SHARP[original_key]
        song.key_note = new_key
        print(f"✅ Updated: {song.title:<30} | {original_key} → {new_key}")
        updated_count += 1
    else:
        # Check if it's already in sharp notation
        if original_key in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
            print(f"⏭️  OK: {song.title:<30} | {original_key} (already sharp)")
        else:
            print(f"⚠️  Unknown: {song.title:<30} | {original_key} (unknown format)")

# Commit changes
session.commit()
session.close()

print(f"\n{'='*60}")
print(f"✅ Done! Updated {updated_count} songs to Mayor notation")
print(f"{'='*60}\n")
