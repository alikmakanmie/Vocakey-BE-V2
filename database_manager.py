import sqlite3
from typing import List, Dict, Optional
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "songs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with songs table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                key_note TEXT,
                scale TEXT,
                vocal_range_min TEXT,
                vocal_range_max TEXT,
                difficulty TEXT,
                genre TEXT,
                audio_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions (SQLite compatible)
        Replaces SQLAlchemy session
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_songs_by_keys(self, keys: List[str]) -> List[Dict]:
        """Get songs by multiple keys"""
        if not keys:
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(keys))
        query = f"SELECT * FROM songs WHERE key_note IN ({placeholders})"
        
        cursor.execute(query, keys)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_song_by_id(self, song_id: int) -> Optional[Dict]:
        """Get a single song by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_song_by_title(self, title: str) -> Optional[Dict]:
        """Get a single song by title"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM songs WHERE title LIKE ?", (f"%{title}%",))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def add_song(self, title: str, artist: str = None, key_note: str = None, 
                 scale: str = None, audio_path: str = None, **kwargs) -> int:
        """Add a new song to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO songs (title, artist, key_note, scale, audio_path,
                             vocal_range_min, vocal_range_max, difficulty, genre)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, artist, key_note, scale, audio_path,
            kwargs.get('vocal_range_min'),
            kwargs.get('vocal_range_max'),
            kwargs.get('difficulty'),
            kwargs.get('genre')
        ))
        
        song_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return song_id
    
    def get_all_songs(self) -> List[Dict]:
        """Get all songs from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM songs ORDER BY title")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_song(self, song_id: int) -> bool:
        """Delete a song by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def update_song(self, song_id: int, **kwargs) -> bool:
        """Update song fields"""
        if not kwargs:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build UPDATE query dynamically
        fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [song_id]
        
        query = f"UPDATE songs SET {fields} WHERE id = ?"
        cursor.execute(query, values)
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0

# ✅ Create global instance for backwards compatibility
db_manager = DatabaseManager()
