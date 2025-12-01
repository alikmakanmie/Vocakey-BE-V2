"""
Database Manager - SQLite Connection & Session Management
File: database_manager.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_models import Base

class DatabaseManager:
    """Manager untuk handle SQLite database operations"""
    
    def __init__(self, db_path='songs.db'):
        """
        Initialize database manager
        
        Args:
            db_path: Path ke SQLite database file (default: songs.db)
        """
        self.db_path = db_path
        
        # Create engine
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False},  # Important untuk multi-threading
            echo=False  # Set True untuk debug SQL queries
        )
        
        # Create all tables jika belum ada
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
        
        print(f"✅ Database initialized: {db_path}")
    
    def get_session(self):
        """
        Get new database session
        
        Returns:
            SQLAlchemy Session object
        """
        return self.Session()
    
    def close_engine(self):
        """Close database engine"""
        self.engine.dispose()

# Global instance (singleton pattern)
db_manager = DatabaseManager('songs.db')
