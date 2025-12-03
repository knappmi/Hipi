"""Database models for multi-user system"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import UniqueConstraint
from home_assistant_platform.config.settings import settings
import bcrypt

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    
    # Profile
    display_name = Column(String)
    avatar_url = Column(String)
    
    # Voice recognition
    voice_profile_id = Column(String)  # ID for voice recognition system
    voice_samples = Column(JSON)  # Voice samples for training
    
    # Preferences
    preferences = Column(JSON)  # User preferences (language, timezone, etc.)
    
    # Permissions
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class UserSession(Base):
    """Active user session"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String, nullable=False, unique=True, index=True)
    
    # Session info
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Expiration
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class VoiceProfile(Base):
    """Voice recognition profile"""
    __tablename__ = "voice_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True)
    
    # Voice features
    voice_features = Column(JSON)  # Extracted voice features
    samples_count = Column(Integer, default=0)
    
    # Training status
    is_trained = Column(Boolean, default=False)
    training_accuracy = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database setup
def get_users_db():
    """Get database session for users system"""
    db_path = settings.data_dir / "users.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def hash_password(password: str) -> str:
    """Hash a password"""
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    try:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

