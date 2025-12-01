"""
Database Migration - Add new columns for audio and vocal range support

Usage:
    python migrate_database.py
"""

import sqlite3
import os

def migrate_database():
    """
    Add new columns to existing songs table:
    - audio_path
    - vocal_range_min
    - vocal_range_max
    - difficulty
    - genre
    - scale
    """
    
    db_path = "songs.db"
    
    print("\n" + "=" * 60)
    print("🔧 Database Migration - Adding Audio & Vocal Range Columns")
    print("=" * 60 + "\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current columns
        cursor.execute("PRAGMA table_info(songs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📋 Current columns: {', '.join(columns)}\n")
        
        # Define new columns to add
        new_columns = {
            'audio_path': 'TEXT',
            'vocal_range_min': 'TEXT',
            'vocal_range_max': 'TEXT',
            'difficulty': 'TEXT',
            'genre': 'TEXT',
            'scale': 'TEXT DEFAULT "major"',
        }
        
        # Add missing columns
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"➕ Adding column: {col_name} ({col_type})")
                cursor.execute(f"ALTER TABLE songs ADD COLUMN {col_name} {col_type}")
                print("   ✅ Done")
            else:
                print(f"⏭️  Column '{col_name}' already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify new columns
        cursor.execute("PRAGMA table_info(songs)")
        new_columns_list = cursor.fetchall()
        
        print("\n" + "=" * 60)
        print("📋 Updated table schema:")
        print("=" * 60)
        
        for col in new_columns_list:
            col_id, col_name, col_type, not_null, default_val, pk = col
            nullable = "NOT NULL" if not_null else "NULL"
            default = f"DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name:20} {col_type:15} {nullable:10} {default}")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60 + "\n")
        
        # Check if we need to populate audio_path
        cursor.execute("SELECT id, title, audio_path FROM songs")
        songs = cursor.fetchall()
        
        needs_update = False
        for song_id, title, audio_path in songs:
            if not audio_path or audio_path == 'None':
                needs_update = True
                break
        
        if needs_update:
            print("⚠️  Some songs don't have audio_path set")
            print("   Run: python update_audio_paths.py")
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {str(e)}\n")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
