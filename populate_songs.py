from database_manager import DatabaseManager
import os

def populate_complete_database():
    """
    Populate database with songs covering ALL 12 musical keys.
    Minimum 3 songs per key to ensure comprehensive recommendations.
    """
    db = DatabaseManager('songs.db')
    
    # Ensure songs directory exists
    os.makedirs('songs/original', exist_ok=True)
    
    # Complete song database - grouped by key
    complete_songs = [
        # ===== KEY C =====
        {
            'title': 'Let It Be',
            'artist': 'The Beatles',
            'keynote': 'C',
            'scale': 'major',
            'audiopath': 'songs/original/Let_It_Be_The_Beatles.mp3',
            'vocalrangemin': 'C3',
            'vocalrangemax': 'C5',
            'difficulty': 'Easy',
            'genre': 'Rock'
        },
        {
            'title': 'Imagine',
            'artist': 'John Lennon',
            'keynote': 'C',
            'scale': 'major',
            'audiopath': 'songs/original/Imagine_John_Lennon.mp3',
            'vocalrangemin': 'C3',
            'vocalrangemax': 'A4',
            'difficulty': 'Easy',
            'genre': 'Pop'
        },
        {
            'title': 'Love Yourself',
            'artist': 'Justin Bieber',
            'keynote': 'C',
            'scale': 'major',
            'audiopath': 'songs/original/Love_Yourself_Justin_Bieber.mp3',
            'vocalrangemin': 'E3',
            'vocalrangemax': 'C5',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        
        # ===== KEY C# (Db) =====
        {
            'title': 'All of Me',
            'artist': 'John Legend',
            'keynote': 'C#',
            'scale': 'major',
            'audiopath': 'songs/original/All_of_Me_John_Legend.mp3',
            'vocalrangemin': 'C#3',
            'vocalrangemax': 'E5',
            'difficulty': 'Hard',
            'genre': 'R&B'
        },
        {
            'title': 'Say Something',
            'artist': 'A Great Big World',
            'keynote': 'C#',
            'scale': 'minor',
            'audiopath': 'songs/original/Say_Something_A_Great_Big_World.mp3',
            'vocalrangemin': 'C#3',
            'vocalrangemax': 'C#5',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        {
            'title': 'Chasing Cars',
            'artist': 'Snow Patrol',
            'keynote': 'C#',
            'scale': 'major',
            'audiopath': 'songs/original/Chasing_Cars_Snow_Patrol.mp3',
            'vocalrangemin': 'C#3',
            'vocalrangemax': 'C#5',
            'difficulty': 'Easy',
            'genre': 'Rock'
        },
        
        # ===== KEY D =====
        {
            'title': 'Wonderwall',
            'artist': 'Oasis',
            'keynote': 'D',
            'scale': 'major',
            'audiopath': 'songs/original/Wonderwall_Oasis.mp3',
            'vocalrangemin': 'D3',
            'vocalrangemax': 'D5',
            'difficulty': 'Easy',
            'genre': 'Rock'
        },
        {
            'title': 'Hotel California',
            'artist': 'Eagles',
            'keynote': 'D',
            'scale': 'minor',
            'audiopath': 'songs/original/Hotel_California_Eagles.mp3',
            'vocalrangemin': 'B2',
            'vocalrangemax': 'B4',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        {
            'title': 'Thinking Out Loud',
            'artist': 'Ed Sheeran',
            'keynote': 'D',
            'scale': 'major',
            'audiopath': 'songs/original/Thinking_Out_Loud_Ed_Sheeran.mp3',
            'vocalrangemin': 'A2',
            'vocalrangemax': 'D4',
            'difficulty': 'Easy',
            'genre': 'Pop'
        },
        
        # ===== KEY D# (Eb) =====
        {
            'title': 'Shape of You',
            'artist': 'Ed Sheeran',
            'keynote': 'D#',
            'scale': 'minor',
            'audiopath': 'songs/original/Shape_of_You_Ed_Sheeran.mp3',
            'vocalrangemin': 'D#3',
            'vocalrangemax': 'G4',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        {
            'title': 'Fix You',
            'artist': 'Coldplay',
            'keynote': 'D#',
            'scale': 'major',
            'audiopath': 'songs/original/Fix_You_Coldplay.mp3',
            'vocalrangemin': 'D#3',
            'vocalrangemax': 'G4',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        {
            'title': 'Viva La Vida',
            'artist': 'Coldplay',
            'keynote': 'D#',
            'scale': 'major',
            'audiopath': 'songs/original/Viva_La_Vida_Coldplay.mp3',
            'vocalrangemin': 'D#3',
            'vocalrangemax': 'G4',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        
        # ===== KEY E =====
        {
            'title': 'Stand By Me',
            'artist': 'Ben E. King',
            'keynote': 'E',
            'scale': 'major',
            'audiopath': 'songs/original/Stand_By_Me_Ben_E_King.mp3',
            'vocalrangemin': 'E3',
            'vocalrangemax': 'E5',
            'difficulty': 'Easy',
            'genre': 'Soul'
        },
        {
            'title': 'Hey Jude',
            'artist': 'The Beatles',
            'keynote': 'E',
            'scale': 'major',
            'audiopath': 'songs/original/Hey_Jude_The_Beatles.mp3',
            'vocalrangemin': 'D3',
            'vocalrangemax': 'C5',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        {
            'title': 'Riptide',
            'artist': 'Vance Joy',
            'keynote': 'E',
            'scale': 'minor',
            'audiopath': 'songs/original/Riptide_Vance_Joy.mp3',
            'vocalrangemin': 'E3',
            'vocalrangemax': 'E5',
            'difficulty': 'Easy',
            'genre': 'Folk'
        },
        
        # ===== KEY F =====
        {
            'title': 'Hallelujah',
            'artist': 'Leonard Cohen',
            'keynote': 'F',
            'scale': 'major',
            'audiopath': 'songs/original/Hallelujah_Leonard_Cohen.mp3',
            'vocalrangemin': 'F3',
            'vocalrangemax': 'F5',
            'difficulty': 'Medium',
            'genre': 'Folk'
        },
        {
            'title': 'Perfect',
            'artist': 'Ed Sheeran',
            'keynote': 'F',
            'scale': 'major',
            'audiopath': 'songs/original/Perfect_Ed_Sheeran.mp3',
            'vocalrangemin': 'F3',
            'vocalrangemax': 'Bb4',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        {
            'title': 'Can\'t Help Falling in Love',
            'artist': 'Elvis Presley',
            'keynote': 'F',
            'scale': 'major',
            'audiopath': 'songs/original/Cant_Help_Falling_In_Love_Elvis_Presley.mp3',
            'vocalrangemin': 'F3',
            'vocalrangemax': 'D5',
            'difficulty': 'Easy',
            'genre': 'Pop'
        },
        
        # ===== KEY F# (Gb) =====
        {
            'title': 'Blinding Lights',
            'artist': 'The Weeknd',
            'keynote': 'F#',
            'scale': 'major',
            'audiopath': 'songs/original/Blinding_Lights_The_Weeknd.mp3',
            'vocalrangemin': 'F#3',
            'vocalrangemax': 'C#5',
            'difficulty': 'Hard',
            'genre': 'Synthpop'
        },
        {
            'title': 'Uptown Funk',
            'artist': 'Bruno Mars',
            'keynote': 'F#',
            'scale': 'minor',
            'audiopath': 'songs/original/Uptown_Funk_Bruno_Mars.mp3',
            'vocalrangemin': 'F#3',
            'vocalrangemax': 'D5',
            'difficulty': 'Hard',
            'genre': 'Funk'
        },
        {
            'title': 'Levitating',
            'artist': 'Dua Lipa',
            'keynote': 'F#',
            'scale': 'minor',
            'audiopath': 'songs/original/Levitating_Dua_Lipa.mp3',
            'vocalrangemin': 'F#3',
            'vocalrangemax': 'F#5',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        
        # ===== KEY G =====
        {
            'title': 'Someone Like You',
            'artist': 'Adele',
            'keynote': 'G',
            'scale': 'major',
            'audiopath': 'songs/original/Someone_Like_You_Adele.mp3',
            'vocalrangemin': 'E3',
            'vocalrangemax': 'C5',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        {
            'title': 'Yesterday',
            'artist': 'The Beatles',
            'keynote': 'G',
            'scale': 'major',
            'audiopath': 'songs/original/Yesterday_The_Beatles.mp3',
            'vocalrangemin': 'G3',
            'vocalrangemax': 'G5',
            'difficulty': 'Easy',
            'genre': 'Pop'
        },
        {
            'title': 'Boulevard of Broken Dreams',
            'artist': 'Green Day',
            'keynote': 'G',
            'scale': 'minor',
            'audiopath': 'songs/original/Boulevard_of_Broken_Dreams_Green_Day.mp3',
            'vocalrangemin': 'F#3',
            'vocalrangemax': 'D5',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        
        # ===== KEY G# (Ab) =====
        {
            'title': 'Shallow',
            'artist': 'Lady Gaga & Bradley Cooper',
            'keynote': 'G#',
            'scale': 'minor',
            'audiopath': 'songs/original/Shallow_Lady_Gaga__Bradley_Cooper.mp3',
            'vocalrangemin': 'G#3',
            'vocalrangemax': 'E5',
            'difficulty': 'Hard',
            'genre': 'Pop'
        },
        {
            'title': 'Poker Face',
            'artist': 'Lady Gaga',
            'keynote': 'G#',
            'scale': 'minor',
            'audiopath': 'songs/original/Poker_Face_Lady_Gaga.mp3',
            'vocalrangemin': 'F#3',
            'vocalrangemax': 'C#5',
            'difficulty': 'Medium',
            'genre': 'Pop'
        },
        {
            'title': 'Bad Romance',
            'artist': 'Lady Gaga',
            'keynote': 'G#',
            'scale': 'minor',
            'audiopath': 'songs/original/Bad_Romance_Lady_Gaga.mp3',
            'vocalrangemin': 'G#3',
            'vocalrangemax': 'F5',
            'difficulty': 'Hard',
            'genre': 'Pop'
        },
        
        # ===== KEY A =====
        {
            'title': 'Creep',
            'artist': 'Radiohead',
            'keynote': 'A',
            'scale': 'major',
            'audiopath': 'songs/original/Creep_Radiohead.mp3',
            'vocalrangemin': 'A2',
            'vocalrangemax': 'C5',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        {
            'title': 'No Woman No Cry',
            'artist': 'Bob Marley',
            'keynote': 'A',
            'scale': 'major',
            'audiopath': 'songs/original/No_Woman_No_Cry_Bob_Marley.mp3',
            'vocalrangemin': 'A2',
            'vocalrangemax': 'A4',
            'difficulty': 'Easy',
            'genre': 'Reggae'
        },
        {
            'title': 'Smells Like Teen Spirit',
            'artist': 'Nirvana',
            'keynote': 'A',
            'scale': 'minor',
            'audiopath': 'songs/original/Smells_Like_Teen_Spirit_Nirvana.mp3',
            'vocalrangemin': 'F3',
            'vocalrangemax': 'C5',
            'difficulty': 'Medium',
            'genre': 'Grunge'
        },
        
        # ===== KEY A# (Bb) =====
        {
            'title': 'Rolling in the Deep',
            'artist': 'Adele',
            'keynote': 'A#',
            'scale': 'minor',
            'audiopath': 'songs/original/Rolling_in_the_Deep_Adele.mp3',
            'vocalrangemin': 'A#3',
            'vocalrangemax': 'D5',
            'difficulty': 'Hard',
            'genre': 'Soul'
        },
        {
            'title': 'Stay With Me',
            'artist': 'Sam Smith',
            'keynote': 'A#',
            'scale': 'major',
            'audiopath': 'songs/original/Stay_With_Me_Sam_Smith.mp3',
            'vocalrangemin': 'A#2',
            'vocalrangemax': 'C5',
            'difficulty': 'Medium',
            'genre': 'Soul'
        },
        {
            'title': 'Wrecking Ball',
            'artist': 'Miley Cyrus',
            'keynote': 'A#',
            'scale': 'minor',
            'audiopath': 'songs/original/Wrecking_Ball_Miley_Cyrus.mp3',
            'vocalrangemin': 'A#3',
            'vocalrangemax': 'F5',
            'difficulty': 'Hard',
            'genre': 'Pop'
        },
        
        # ===== KEY B =====
        {
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'keynote': 'B',
            'scale': 'major',
            'audiopath': 'songs/original/Bohemian_Rhapsody_Various_Artist.mp3',
            'vocalrangemin': 'B2',
            'vocalrangemax': 'B4',
            'difficulty': 'Hard',
            'genre': 'Rock'
        },
        {
            'title': 'Don\'t Stop Believin\'',
            'artist': 'Journey',
            'keynote': 'B',
            'scale': 'major',
            'audiopath': 'songs/original/Dont_Stop_Believin_Journey.mp3',
            'vocalrangemin': 'B2',
            'vocalrangemax': 'E5',
            'difficulty': 'Medium',
            'genre': 'Rock'
        },
        {
            'title': 'Livin\' on a Prayer',
            'artist': 'Bon Jovi',
            'keynote': 'B',
            'scale': 'minor',
            'audiopath': 'songs/original/Livin_on_a_Prayer_Bon_Jovi.mp3',
            'vocalrangemin': 'B2',
            'vocalrangemax': 'E5',
            'difficulty': 'Hard',
            'genre': 'Rock'
        },
    ]
    
    print("=" * 70)
    print("🎵 POPULATING COMPLETE SONG DATABASE")
    print("=" * 70)
    print(f"Total songs to add: {len(complete_songs)}")
    print()
    
    # Statistics
    keys_count = {}
    added_count = 0
    skipped_count = 0
    
    for song in complete_songs:
        # Track key statistics
        key = song['keynote']
        keys_count[key] = keys_count.get(key, 0) + 1
        
        # Check if song already exists
        existing = db.getsongbytitle(song['title'])
        if existing:
            print(f"⏭️  Skipped: {song['title']} - already exists")
            skipped_count += 1
        else:
            try:
                song_id = db.addsong(**song)
                print(f"✅ Added: {song['title']} by {song['artist']} (Key: {song['keynote']}) - ID: {song_id}")
                added_count += 1
            except Exception as e:
                print(f"❌ Error adding {song['title']}: {str(e)}")
    
    print()
    print("=" * 70)
    print("📊 DATABASE STATISTICS")
    print("=" * 70)
    print(f"✅ Songs added: {added_count}")
    print(f"⏭️  Songs skipped: {skipped_count}")
    print()
    
    # Songs per key
    print("🎹 Songs per Key:")
    all_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    for key in all_keys:
        count = keys_count.get(key, 0)
        status = "✅" if count >= 3 else "⚠️"
        print(f"  {status} {key:3s}: {count} songs")
    
    print()
    
    # Total songs in database
    all_songs = db.getallsongs()
    print(f"📀 Total songs in database: {len(all_songs)}")
    print("=" * 70)
    print()
    
    # Verify coverage
    missing_keys = [key for key in all_keys if keys_count.get(key, 0) == 0]
    if missing_keys:
        print(f"⚠️  WARNING: Missing keys: {', '.join(missing_keys)}")
    else:
        print("✅ All 12 keys covered!")
    
    print()

if __name__ == '__main__':
    populate_complete_database()
