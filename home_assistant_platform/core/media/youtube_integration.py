"""YouTube integration for media control"""

import logging
from typing import List, Dict, Optional, Any
import re

logger = logging.getLogger(__name__)


class YouTubeIntegration:
    """YouTube integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def is_configured(self) -> bool:
        """Check if YouTube is configured"""
        return bool(self.api_key)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for YouTube videos"""
        if not self.is_configured():
            logger.warning("YouTube API key not configured")
            return []
        
        try:
            # In production, use YouTube Data API v3
            # For now, return mock results
            logger.info(f"YouTube search: {query}")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information"""
        if not self.is_configured():
            return None
        
        try:
            # In production, use YouTube Data API v3
            return {
                "id": video_id,
                "title": "Video Title",
                "source": "youtube",
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None

