"""User management API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from home_assistant_platform.core.users.user_manager import UserManager
from home_assistant_platform.core.users.voice_recognition import VoiceRecognition

logger = logging.getLogger(__name__)
router = APIRouter()


class UserCreateRequest(BaseModel):
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    is_admin: bool = False


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserPreferencesRequest(BaseModel):
    preferences: Dict[str, Any]


def get_user_manager(request: Request) -> UserManager:
    """Get user manager from app state"""
    if not hasattr(request.app.state, 'user_manager'):
        request.app.state.user_manager = UserManager()
    return request.app.state.user_manager


def get_voice_recognition(request: Request) -> VoiceRecognition:
    """Get voice recognition from app state"""
    if not hasattr(request.app.state, 'voice_recognition'):
        request.app.state.voice_recognition = VoiceRecognition()
    return request.app.state.voice_recognition


def get_current_user(request: Request, session_token: Optional[str] = Header(None, alias="X-Session-Token")) -> Optional[Dict]:
    """Get current user from session"""
    user_manager = get_user_manager(request)
    
    if session_token:
        user = user_manager.get_user_by_session(session_token)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name
            }
    
    # Fallback to current user
    current_user = user_manager.get_current_user()
    if current_user:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "display_name": current_user.display_name
        }
    
    return None


@router.post("/register")
async def register_user(request: Request, user_req: UserCreateRequest):
    """Register a new user"""
    manager = get_user_manager(request)
    
    try:
        user = manager.create_user(
            username=user_req.username,
            password=user_req.password,
            email=user_req.email,
            display_name=user_req.display_name,
            is_admin=user_req.is_admin
        )
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(request: Request, login_req: UserLoginRequest):
    """Login and create session"""
    manager = get_user_manager(request)
    
    user = manager.authenticate(login_req.username, login_req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_token = manager.create_session(user.id)
    manager.set_current_user(user.id)
    
    return {
        "success": True,
        "session_token": session_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name
        }
    }


@router.get("/me")
async def get_current_user_info(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    """Get current user info"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    manager = get_user_manager(request)
    user = manager.get_user(current_user["id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "preferences": user.preferences,
            "is_admin": user.is_admin
        }
    }


@router.get("/users")
async def list_users(request: Request):
    """List all users"""
    manager = get_user_manager(request)
    users = manager.list_users()
    
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "display_name": u.display_name,
                "is_admin": u.is_admin
            }
            for u in users
        ]
    }


@router.post("/switch")
async def switch_user(request: Request, user_id: int, current_user: Optional[Dict] = Depends(get_current_user)):
    """Switch to a different user"""
    manager = get_user_manager(request)
    
    user = manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    manager.set_current_user(user_id)
    
    return {
        "success": True,
        "message": f"Switched to user: {user.display_name}",
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name
        }
    }


@router.put("/preferences")
async def update_preferences(
    request: Request,
    prefs_req: UserPreferencesRequest,
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """Update user preferences"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    manager = get_user_manager(request)
    success = manager.update_user_preferences(current_user["id"], prefs_req.preferences)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Preferences updated"}


@router.post("/voice/train")
async def train_voice_profile(
    request: Request,
    user_id: int,
    audio_samples: List[bytes],
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """Train voice recognition for a user"""
    if not current_user or (current_user["id"] != user_id and not current_user.get("is_admin")):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    voice_recognition = get_voice_recognition(request)
    success = voice_recognition.train_user_model(user_id, audio_samples)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to train voice model")
    
    return {"success": True, "message": "Voice model trained"}


@router.post("/voice/identify")
async def identify_user_by_voice(request: Request, audio_data: bytes):
    """Identify user from voice sample"""
    voice_recognition = get_voice_recognition(request)
    user_id = voice_recognition.identify_user(audio_data)
    
    if not user_id:
        return {"success": False, "message": "User not identified"}
    
    manager = get_user_manager(request)
    user = manager.get_user(user_id)
    
    if user:
        manager.set_current_user(user_id)
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name
            }
        }
    
    return {"success": False, "message": "User not found"}


@router.get("/voice/status/{user_id}")
async def get_voice_status(request: Request, user_id: int):
    """Get voice recognition training status"""
    voice_recognition = get_voice_recognition(request)
    status = voice_recognition.get_training_status(user_id)
    
    return {"status": status}

