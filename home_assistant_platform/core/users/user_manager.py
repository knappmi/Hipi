"""User manager - manages users and authentication"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from home_assistant_platform.core.users.models import (
    User, UserSession, VoiceProfile, get_users_db,
    hash_password, verify_password
)

logger = logging.getLogger(__name__)


class UserManager:
    """Manages users and authentication"""
    
    def __init__(self):
        self.db = get_users_db()
        self.current_user_id: Optional[int] = None
    
    def create_user(
        self,
        username: str,
        password: Optional[str] = None,
        email: Optional[str] = None,
        display_name: Optional[str] = None,
        is_admin: bool = False
    ) -> User:
        """Create a new user"""
        # Check if user exists
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError(f"User '{username}' already exists")
        
        hashed_pwd = None
        if password:
            # Truncate password to 72 bytes for bcrypt
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hashed_pwd = hash_password(password_bytes.decode('utf-8', errors='ignore'))
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            display_name=display_name or username,
            is_admin=is_admin,
            preferences={
                "language": "en",
                "timezone": "UTC",
                "voice_enabled": True
            }
        )
        
        self.db.add(user)
        self.db.commit()
        
        # Create voice profile
        voice_profile = VoiceProfile(user_id=user.id)
        self.db.add(voice_profile)
        self.db.commit()
        
        logger.info(f"Created user: {username}")
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user or not user.is_active:
            return None
        
        if not user.hashed_password:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"User authenticated: {username}")
        return user
    
    def create_session(self, user_id: int, ip_address: Optional[str] = None) -> str:
        """Create a user session"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            expires_at=expires_at
        )
        
        self.db.add(session)
        self.db.commit()
        
        logger.info(f"Created session for user {user_id}")
        return session_token
    
    def get_user_by_session(self, session_token: str) -> Optional[User]:
        """Get user by session token"""
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        return self.db.query(User).filter(User.id == session.user_id).first()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def list_users(self) -> List[User]:
        """List all users"""
        return self.db.query(User).filter(User.is_active == True).all()
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        if user.preferences:
            user.preferences.update(preferences)
        else:
            user.preferences = preferences
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Updated preferences for user {user_id}")
        return True
    
    def set_current_user(self, user_id: int):
        """Set the current active user"""
        user = self.get_user(user_id)
        if user and user.is_active:
            self.current_user_id = user_id
            logger.info(f"Current user set to: {user.username}")
        else:
            logger.warning(f"Invalid user ID: {user_id}")
    
    def get_current_user(self) -> Optional[User]:
        """Get the current active user"""
        if self.current_user_id:
            return self.get_user(self.current_user_id)
        return None
    
    def identify_user_by_voice(self, audio_data: bytes) -> Optional[User]:
        """Identify user by voice (placeholder for voice recognition)"""
        # In production, this would use voice recognition ML model
        # For now, return None (no user identified)
        logger.info("Voice recognition not yet implemented")
        return None
    
    def add_voice_sample(self, user_id: int, audio_data: bytes) -> bool:
        """Add a voice sample for training"""
        voice_profile = self.db.query(VoiceProfile).filter(
            VoiceProfile.user_id == user_id
        ).first()
        
        if not voice_profile:
            voice_profile = VoiceProfile(user_id=user_id)
            self.db.add(voice_profile)
        
        # In production, extract and store voice features
        # For now, just increment sample count
        voice_profile.samples_count += 1
        voice_profile.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Added voice sample for user {user_id} (total: {voice_profile.samples_count})")
        return True
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete)"""
        user = self.get_user(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            logger.info(f"Deleted user: {user_id}")
            return True
        return False

