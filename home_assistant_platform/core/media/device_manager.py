"""Media device manager - manages media devices and playback"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from home_assistant_platform.core.media.models import (
    MediaDevice, MediaSession, get_media_db
)

logger = logging.getLogger(__name__)


class MediaDeviceManager:
    """Manages media devices and playback"""
    
    def __init__(self):
        self.db = get_media_db()
        self.active_sessions: Dict[int, MediaSession] = {}
    
    def register_device(
        self,
        name: str,
        device_type: str,
        device_id: str,
        ip_address: Optional[str] = None,
        port: Optional[int] = None,
        protocol: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        user_id: str = "default"
    ) -> MediaDevice:
        """Register a media device"""
        # Check if device already exists
        existing = self.db.query(MediaDevice).filter(
            MediaDevice.device_id == device_id
        ).first()
        
        if existing:
            # Update existing device
            existing.name = name
            existing.ip_address = ip_address
            existing.port = port
            existing.protocol = protocol
            existing.capabilities = capabilities or []
            existing.is_active = True
            self.db.commit()
            return existing
        
        device = MediaDevice(
            name=name,
            device_type=device_type,
            device_id=device_id,
            ip_address=ip_address,
            port=port,
            protocol=protocol,
            capabilities=capabilities or [],
            manufacturer=manufacturer,
            model=model,
            user_id=user_id,
            current_state={"playing": False, "volume": 50}
        )
        
        self.db.add(device)
        self.db.commit()
        
        logger.info(f"Registered media device: {name} ({device_type})")
        return device
    
    def get_device(self, device_id: int, user_id: str = "default") -> Optional[MediaDevice]:
        """Get a media device"""
        return self.db.query(MediaDevice).filter(
            MediaDevice.id == device_id,
            MediaDevice.user_id == user_id,
            MediaDevice.is_active == True
        ).first()
    
    def list_devices(self, device_type: Optional[str] = None, user_id: str = "default") -> List[MediaDevice]:
        """List all media devices"""
        query = self.db.query(MediaDevice).filter(
            MediaDevice.user_id == user_id,
            MediaDevice.is_active == True
        )
        
        if device_type:
            query = query.filter(MediaDevice.device_type == device_type)
        
        return query.all()
    
    async def play(self, device_id: int, media: Optional[Dict[str, Any]] = None, user_id: str = "default") -> bool:
        """Play media on device"""
        device = self.get_device(device_id, user_id)
        if not device:
            logger.warning(f"Device {device_id} not found")
            return False
        
        # Update device state
        if device.current_state:
            device.current_state["playing"] = True
        else:
            device.current_state = {"playing": True, "volume": 50}
        
        # Create or update session
        session = self.db.query(MediaSession).filter(
            MediaSession.device_id == device_id,
            MediaSession.user_id == user_id
        ).first()
        
        if not session:
            session = MediaSession(
                device_id=device_id,
                media_type=media.get("type", "music") if media else "music",
                title=media.get("title", "") if media else "",
                artist=media.get("artist", "") if media else "",
                source=media.get("source", "local") if media else "local",
                source_id=media.get("source_id", "") if media else "",
                is_playing=True,
                user_id=user_id
            )
            self.db.add(session)
        else:
            session.is_playing = True
            if media:
                session.title = media.get("title", session.title)
                session.artist = media.get("artist", session.artist)
                session.source = media.get("source", session.source)
        
        self.db.commit()
        self.active_sessions[device_id] = session
        
        logger.info(f"Playing on device {device_id}: {media.get('title', 'Unknown') if media else 'Unknown'}")
        return True
    
    async def pause(self, device_id: int, user_id: str = "default") -> bool:
        """Pause playback on device"""
        device = self.get_device(device_id, user_id)
        if not device:
            return False
        
        if device.current_state:
            device.current_state["playing"] = False
        
        session = self.db.query(MediaSession).filter(
            MediaSession.device_id == device_id,
            MediaSession.user_id == user_id
        ).first()
        
        if session:
            session.is_playing = False
            self.db.commit()
        
        logger.info(f"Paused device {device_id}")
        return True
    
    async def stop(self, device_id: int, user_id: str = "default") -> bool:
        """Stop playback on device"""
        device = self.get_device(device_id, user_id)
        if not device:
            return False
        
        if device.current_state:
            device.current_state["playing"] = False
        
        session = self.db.query(MediaSession).filter(
            MediaSession.device_id == device_id,
            MediaSession.user_id == user_id
        ).first()
        
        if session:
            session.is_playing = False
            self.db.commit()
        
        if device_id in self.active_sessions:
            del self.active_sessions[device_id]
        
        logger.info(f"Stopped device {device_id}")
        return True
    
    async def set_volume(self, device_id: int, volume: int, user_id: str = "default") -> bool:
        """Set volume on device (0-100)"""
        device = self.get_device(device_id, user_id)
        if not device:
            return False
        
        volume = max(0, min(100, volume))  # Clamp to 0-100
        
        if device.current_state:
            device.current_state["volume"] = volume
        else:
            device.current_state = {"volume": volume, "playing": False}
        
        session = self.db.query(MediaSession).filter(
            MediaSession.device_id == device_id,
            MediaSession.user_id == user_id
        ).first()
        
        if session:
            session.volume = volume
            self.db.commit()
        
        logger.info(f"Set volume on device {device_id} to {volume}")
        return True
    
    async def next_track(self, device_id: int, user_id: str = "default") -> bool:
        """Skip to next track"""
        device = self.get_device(device_id, user_id)
        if not device:
            return False
        
        logger.info(f"Next track on device {device_id}")
        return True
    
    async def previous_track(self, device_id: int, user_id: str = "default") -> bool:
        """Skip to previous track"""
        device = self.get_device(device_id, user_id)
        if not device:
            return False
        
        logger.info(f"Previous track on device {device_id}")
        return True
    
    def get_current_session(self, device_id: int, user_id: str = "default") -> Optional[MediaSession]:
        """Get current playback session"""
        return self.db.query(MediaSession).filter(
            MediaSession.device_id == device_id,
            MediaSession.user_id == user_id,
            MediaSession.is_playing == True
        ).first()
    
    def delete_device(self, device_id: int, user_id: str = "default") -> bool:
        """Delete a media device"""
        device = self.get_device(device_id, user_id)
        if device:
            device.is_active = False
            self.db.commit()
            logger.info(f"Deleted media device: {device_id}")
            return True
        return False

