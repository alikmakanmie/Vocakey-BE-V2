from database_manager import DatabaseManager

db = DatabaseManager('songs.db')

all_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

print("=" * 60)
print("DATABASE COVERAGE VERIFICATION")
print("=" * 60)

total_songs = 0
for key in all_keys:
    songs = db.get_songs_by_keys([key])
    total_songs += len(songs)
    status = "✅" if len(songs) >= 3 else "❌"
    print(f"{status} {key:3s}: {len(songs)} songs")
    for song in songs:
        print(f"     - {song['title']} by {song['artist']}")

print("=" * 60)
print(f"Total: {total_songs} songs")
print("=" * 60)

# Check missing keys
missing = [key for key in all_keys if len(db.get_songs_by_keys([key])) < 3]
if missing:
    print(f"\n⚠️  MISSING COVERAGE: {', '.join(missing)}")
else:
    print("\n✅ ALL KEYS COVERED! Ready for production!")
