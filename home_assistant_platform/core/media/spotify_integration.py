"""Spotify integration for media control"""

import logging
from typing import List, Dict, Optional, Any
import requests

logger = logging.getLogger(__name__)


class SpotifyIntegration:
    """Spotify API integration"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
    
    def is_configured(self) -> bool:
        """Check if Spotify is configured"""
        return bool(self.client_id and self.client_secret)
    
    async def search(self, query: str, media_type: str = "track", limit: int = 10) -> List[Dict[str, Any]]:
        """Search for tracks/artists/albums"""
        if not self.is_configured():
            logger.warning("Spotify not configured")
            return []
        
        await self._ensure_token()
        
        try:
            url = "https://api.spotify.com/v1/search"
            params = {
                "q": query,
                "type": media_type,
                "limit": limit
            }
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = []
            data = response.json()
            
            if media_type == "track" and "tracks" in data:
                for item in data["tracks"]["items"]:
                    results.append({
                        "id": item["id"],
                        "title": item["name"],
                        "artist": ", ".join([a["name"] for a in item["artists"]]),
                        "album": item["album"]["name"],
                        "duration": item["duration_ms"] // 1000,
                        "source": "spotify",
                        "uri": item["uri"],
                        "image": item["album"]["images"][0]["url"] if item["album"]["images"] else None
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching Spotify: {e}")
            return []
    
    async def play_track(self, device_id: str, track_uri: str) -> bool:
        """Play a track on a Spotify device"""
        if not self.is_configured():
            return False
        
        await self._ensure_token()
        
        try:
            url = f"https://api.spotify.com/v1/me/player/play"
            params = {"device_id": device_id}
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = {"uris": [track_uri]}
            
            response = requests.put(url, params=params, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f"Error playing Spotify track: {e}")
            return False
    
    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get available Spotify devices"""
        if not self.is_configured():
            return []
        
        await self._ensure_token()
        
        try:
            url = "https://api.spotify.com/v1/me/player/devices"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get("devices", [])
        except Exception as e:
            logger.error(f"Error getting Spotify devices: {e}")
            return []
    
    async def _ensure_token(self):
        """Ensure we have a valid access token"""
        # In a real implementation, this would handle OAuth flow
        # For now, we'll just log that it's needed
        if not self.access_token:
            logger.warning("Spotify access token needed. OAuth flow required.")
            # In production, implement OAuth 2.0 flow here

