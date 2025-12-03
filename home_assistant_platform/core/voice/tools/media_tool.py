"""Media control tool - handles media voice commands"""

import logging
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class MediaTool(Tool):
    """Tool for media control"""
    
    def __init__(self, media_manager=None):
        self.media_manager = media_manager
    
    @property
    def name(self) -> str:
        return "media"
    
    @property
    def description(self) -> str:
        return "Control media playback (play, pause, volume, etc.)"
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "play_music", "pause_music", "stop_music", "volume",
            "next_track", "previous_track", "play_spotify", "play_youtube"
        ]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["play_music", "pause_music", "stop_music", "volume"]:
            return True
        
        media_keywords = [
            "play", "pause", "stop", "volume", "music", "song",
            "next", "previous", "skip", "louder", "quieter",
            "spotify", "youtube", "playlist"
        ]
        
        return any(kw in text_lower for kw in media_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute media operation"""
        if not self.media_manager:
            return "Media system is not available"
        
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        # Get default device (first available)
        devices = self.media_manager.list_devices()
        if not devices:
            return "No media devices available. Please add a media device first."
        
        device = devices[0]
        
        # Parse command
        if intent_lower == "play_music" or "play" in text_lower:
            # Extract media info if provided
            media = self._extract_media_info(text)
            import asyncio
            success = asyncio.run(self.media_manager.play(device.id, media))
            if success:
                if media and media.get("title"):
                    return f"Playing {media['title']} on {device.name}"
                return f"Playing on {device.name}"
            return "Failed to start playback"
        
        elif intent_lower == "pause_music" or "pause" in text_lower:
            import asyncio
            success = asyncio.run(self.media_manager.pause(device.id))
            return "Paused" if success else "Failed to pause"
        
        elif intent_lower == "stop_music" or "stop" in text_lower:
            import asyncio
            success = asyncio.run(self.media_manager.stop(device.id))
            return "Stopped" if success else "Failed to stop"
        
        elif "volume" in text_lower or "louder" in text_lower or "quieter" in text_lower:
            volume_change = self._parse_volume_change(text_lower)
            if volume_change:
                session = self.media_manager.get_current_session(device.id)
                current_volume = session.volume if session else 50
                new_volume = max(0, min(100, current_volume + volume_change))
                
                import asyncio
                success = asyncio.run(self.media_manager.set_volume(device.id, new_volume))
                return f"Volume set to {new_volume}%" if success else "Failed to change volume"
            return "I didn't understand the volume change. Try saying 'turn volume up' or 'volume 50'."
        
        elif "next" in text_lower or "skip" in text_lower:
            import asyncio
            success = asyncio.run(self.media_manager.next_track(device.id))
            return "Skipped to next track" if success else "Failed to skip"
        
        elif "previous" in text_lower or "back" in text_lower:
            import asyncio
            success = asyncio.run(self.media_manager.previous_track(device.id))
            return "Skipped to previous track" if success else "Failed to skip"
        
        return "I didn't understand the media command. Try saying 'play music', 'pause', or 'volume up'."
    
    def _extract_media_info(self, text: str) -> Optional[dict]:
        """Extract media information from text"""
        text_lower = text.lower()
        
        # Check for Spotify
        if "spotify" in text_lower:
            # Extract song/artist name
            parts = text_lower.split("spotify")
            if len(parts) > 1:
                query = parts[1].strip()
                return {
                    "source": "spotify",
                    "query": query,
                    "type": "music"
                }
        
        # Check for YouTube
        if "youtube" in text_lower or "youtu.be" in text_lower:
            import re
            video_id_match = re.search(r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})", text)
            if video_id_match:
                return {
                    "source": "youtube",
                    "source_id": video_id_match.group(1),
                    "type": "video"
                }
        
        # Extract song/artist name
        if "play" in text_lower:
            parts = text_lower.split("play")
            if len(parts) > 1:
                query = parts[1].strip()
                # Remove common words
                query = query.replace("music", "").replace("song", "").strip()
                if query:
                    return {
                        "source": "local",
                        "query": query,
                        "type": "music"
                    }
        
        return None
    
    def _parse_volume_change(self, text: str) -> Optional[int]:
        """Parse volume change from text"""
        import re
        
        # Look for specific volume number
        volume_match = re.search(r"volume (\d+)", text)
        if volume_match:
            volume = int(volume_match.group(1))
            session = self.media_manager.get_current_session(1)  # Default device
            current_volume = session.volume if session else 50
            return volume - current_volume
        
        # Look for percentage
        percent_match = re.search(r"(\d+)%", text)
        if percent_match:
            volume = int(percent_match.group(1))
            session = self.media_manager.get_current_session(1)
            current_volume = session.volume if session else 50
            return volume - current_volume
        
        # Look for relative changes
        if "up" in text or "louder" in text or "increase" in text:
            return 10
        if "down" in text or "quieter" in text or "decrease" in text:
            return -10
        
        return None

