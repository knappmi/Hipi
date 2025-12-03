"""Media control API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from home_assistant_platform.core.media.device_manager import MediaDeviceManager
from home_assistant_platform.core.media.spotify_integration import SpotifyIntegration
from home_assistant_platform.core.media.youtube_integration import YouTubeIntegration

logger = logging.getLogger(__name__)
router = APIRouter()


class MediaDeviceCreateRequest(BaseModel):
    name: str
    device_type: str
    device_id: str
    ip_address: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    capabilities: Optional[List[str]] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None


class MediaPlayRequest(BaseModel):
    device_id: int
    media: Optional[Dict[str, Any]] = None


class VolumeRequest(BaseModel):
    device_id: int
    volume: int


def get_media_manager(request: Request) -> MediaDeviceManager:
    """Get media manager from app state"""
    if not hasattr(request.app.state, 'media_manager'):
        request.app.state.media_manager = MediaDeviceManager()
    return request.app.state.media_manager


def get_spotify_integration(request: Request) -> SpotifyIntegration:
    """Get Spotify integration from app state"""
    if not hasattr(request.app.state, 'spotify_integration'):
        from home_assistant_platform.config.settings import settings
        request.app.state.spotify_integration = SpotifyIntegration(
            client_id=getattr(settings, 'spotify_client_id', None),
            client_secret=getattr(settings, 'spotify_client_secret', None)
        )
    return request.app.state.spotify_integration


def get_youtube_integration(request: Request) -> YouTubeIntegration:
    """Get YouTube integration from app state"""
    if not hasattr(request.app.state, 'youtube_integration'):
        from home_assistant_platform.config.settings import settings
        request.app.state.youtube_integration = YouTubeIntegration(
            api_key=getattr(settings, 'youtube_api_key', None)
        )
    return request.app.state.youtube_integration


@router.get("/devices")
async def list_devices(request: Request, device_type: Optional[str] = None, user_id: str = "default"):
    """List all media devices"""
    manager = get_media_manager(request)
    devices = manager.list_devices(device_type=device_type, user_id=user_id)
    
    return {
        "devices": [
            {
                "id": d.id,
                "name": d.name,
                "device_type": d.device_type,
                "device_id": d.device_id,
                "capabilities": d.capabilities,
                "current_state": d.current_state,
                "manufacturer": d.manufacturer,
                "model": d.model
            }
            for d in devices
        ]
    }


@router.post("/devices")
async def register_device(request: Request, device_req: MediaDeviceCreateRequest, user_id: str = "default"):
    """Register a media device"""
    manager = get_media_manager(request)
    device = manager.register_device(
        name=device_req.name,
        device_type=device_req.device_type,
        device_id=device_req.device_id,
        ip_address=device_req.ip_address,
        port=device_req.port,
        protocol=device_req.protocol,
        capabilities=device_req.capabilities,
        manufacturer=device_req.manufacturer,
        model=device_req.model,
        user_id=user_id
    )
    
    return {
        "success": True,
        "device": {
            "id": device.id,
            "name": device.name,
            "device_type": device.device_type
        }
    }


@router.post("/play")
async def play_media(request: Request, play_req: MediaPlayRequest, user_id: str = "default"):
    """Play media on device"""
    manager = get_media_manager(request)
    success = await manager.play(play_req.device_id, play_req.media, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Playback started"}


@router.post("/pause")
async def pause_media(request: Request, device_id: int, user_id: str = "default"):
    """Pause playback"""
    manager = get_media_manager(request)
    success = await manager.pause(device_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Playback paused"}


@router.post("/stop")
async def stop_media(request: Request, device_id: int, user_id: str = "default"):
    """Stop playback"""
    manager = get_media_manager(request)
    success = await manager.stop(device_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Playback stopped"}


@router.post("/volume")
async def set_volume(request: Request, volume_req: VolumeRequest, user_id: str = "default"):
    """Set volume"""
    manager = get_media_manager(request)
    success = await manager.set_volume(volume_req.device_id, volume_req.volume, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": f"Volume set to {volume_req.volume}%"}


@router.post("/next")
async def next_track(request: Request, device_id: int, user_id: str = "default"):
    """Skip to next track"""
    manager = get_media_manager(request)
    success = await manager.next_track(device_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Skipped to next track"}


@router.post("/previous")
async def previous_track(request: Request, device_id: int, user_id: str = "default"):
    """Skip to previous track"""
    manager = get_media_manager(request)
    success = await manager.previous_track(device_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Skipped to previous track"}


@router.get("/sessions/{device_id}")
async def get_session(request: Request, device_id: int, user_id: str = "default"):
    """Get current playback session"""
    manager = get_media_manager(request)
    session = manager.get_current_session(device_id, user_id=user_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session")
    
    return {
        "session": {
            "id": session.id,
            "title": session.title,
            "artist": session.artist,
            "album": session.album,
            "is_playing": session.is_playing,
            "volume": session.volume,
            "source": session.source
        }
    }


@router.get("/spotify/search")
async def search_spotify(request: Request, query: str, limit: int = 10):
    """Search Spotify"""
    spotify = get_spotify_integration(request)
    
    if not spotify.is_configured():
        raise HTTPException(status_code=400, detail="Spotify not configured")
    
    results = await spotify.search(query, limit=limit)
    return {"results": results}


@router.get("/youtube/search")
async def search_youtube(request: Request, query: str, max_results: int = 10):
    """Search YouTube"""
    youtube = get_youtube_integration(request)
    
    if not youtube.is_configured():
        raise HTTPException(status_code=400, detail="YouTube not configured")
    
    results = await youtube.search(query, max_results=max_results)
    return {"results": results}

