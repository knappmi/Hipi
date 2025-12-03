"""Scene tool - handles scene voice commands"""

import logging
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class SceneTool(Tool):
    """Tool for scene management"""
    
    def __init__(self, scene_manager=None):
        self.scene_manager = scene_manager
    
    @property
    def name(self) -> str:
        return "scene"
    
    @property
    def description(self) -> str:
        return "Activate scenes and manage device presets"
    
    @property
    def capabilities(self) -> List[str]:
        return ["activate_scene", "scene", "movie night", "bedtime", "away mode"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["activate_scene", "scene"]:
            return True
        
        scene_keywords = [
            "activate", "scene", "movie night", "bedtime", "away mode",
            "good night", "wake up", "dinner time", "reading", "party mode"
        ]
        
        return any(kw in text_lower for kw in scene_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute scene operation"""
        if not self.scene_manager:
            return "Scene system is not available"
        
        text_lower = text.lower()
        
        # Extract scene name
        scene_name = self._extract_scene_name(text_lower)
        
        if scene_name:
            # Try to activate scene
            import asyncio
            try:
                success = asyncio.run(self.scene_manager.activate_scene_by_name(scene_name))
                if success:
                    return f"Activated scene: {scene_name}"
                else:
                    return f"Scene '{scene_name}' not found or failed to activate"
            except Exception as e:
                logger.error(f"Error activating scene: {e}", exc_info=True)
                return f"Error activating scene: {scene_name}"
        else:
            return "I didn't understand which scene you want to activate. Try saying 'activate movie night' or 'activate bedtime scene'."
    
    def _extract_scene_name(self, text: str) -> Optional[str]:
        """Extract scene name from text"""
        # Remove common prefixes
        prefixes = ["activate", "turn on", "start", "set", "enable"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes = ["scene", "mode"]
        for suffix in suffixes:
            if text.endswith(suffix):
                text = text[:-len(suffix)].strip()
        
        # Common scene names
        scene_mappings = {
            "movie night": "movie_night",
            "movie": "movie_night",
            "bedtime": "bedtime",
            "good night": "bedtime",
            "sleep": "bedtime",
            "away": "away_mode",
            "away mode": "away_mode",
            "dinner": "dinner_time",
            "dinner time": "dinner_time",
            "reading": "reading",
            "party": "party_mode",
            "party mode": "party_mode",
            "wake up": "wake_up",
            "morning": "wake_up",
        }
        
        # Check for exact matches first
        if text in scene_mappings:
            return scene_mappings[text]
        
        # Check for partial matches
        for key, value in scene_mappings.items():
            if key in text:
                return value
        
        # Return normalized text as scene name
        return text.replace(" ", "_").lower() if text else None

