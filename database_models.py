"""
Database Models - SQLAlchemy ORM
File: database_models.py
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Song(Base):
    """Model untuk tabel songs"""
    
    __tablename__ = 'songs'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Info
    title = Column(String(255), nullable=False, index=True)
    artist = Column(String(255), nullable=False, index=True)
    
    # Music Theory (untuk matching)
    key_note = Column(String(20), nullable=False, index=True)
    pitch_range_acc = Column(Float, nullable=False, index=True)
    
    # Media Links
    link_youtube = Column(String(500), nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    
    # Additional Metadata
    genre = Column(String(100), nullable=True)
    tempo = Column(Integer, nullable=True)
    popularity_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Song(id={self.id}, title='{self.title}', artist='{self.artist}', key='{self.key_note}')>"
    
    def to_dict(self):
        """Convert to dictionary untuk JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'key_note': self.key_note,
            'pitch_range_acc': self.pitch_range_acc,
            'link_youtube': self.link_youtube,
            'cover_image_url': self.cover_image_url,
            'genre': self.genre,
            'tempo': self.tempo,
            'popularity_score': self.popularity_score
        }
