"""Database models for media control system"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from home_assistant_platform.config.settings import settings
import os

logger = logging.getLogger(__name__)

Base = declarative_base()


class MediaDevice(Base):
    """Media device (TV, speaker, etc.)"""
    __tablename__ = "media_devices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)  # tv, speaker, chromecast, airplay, etc.
    device_id = Column(String, nullable=False, unique=True)
    
    # Connection info
    ip_address = Column(String)
    port = Column(Integer)
    protocol = Column(String)  # dlna, chromecast, airplay, etc.
    
    # Capabilities
    capabilities = Column(JSON)  # ["play", "pause", "volume", "source"]
    
    # Current state
    current_state = Column(JSON)  # {"playing": false, "volume": 50, "source": "hdmi1"}
    
    # Metadata
    manufacturer = Column(String)
    model = Column(String)
    is_active = Column(Boolean, default=True)
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MediaPlaylist(Base):
    """Media playlist"""
    __tablename__ = "media_playlists"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Playlist items
    items = Column(JSON, nullable=False)  # List of media items
    
    # Source
    source = Column(String)  # spotify, youtube, local, etc.
    source_playlist_id = Column(String)  # External playlist ID
    
    # Metadata
    user_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MediaSession(Base):
    """Active media playback session"""
    __tablename__ = "media_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False)
    
    # Current playback
    media_type = Column(String)  # music, video, podcast
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    duration = Column(Integer)  # seconds
    position = Column(Integer)  # current position in seconds
    
    # Source
    source = Column(String)  # spotify, youtube, local, etc.
    source_id = Column(String)  # External media ID
    
    # State
    is_playing = Column(Boolean, default=False)
    volume = Column(Integer, default=50)
    
    # Metadata
    user_id = Column(String, default="default")
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database setup
def get_media_db():
    """Get database session for media system"""
    db_path = settings.data_dir / "media.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

