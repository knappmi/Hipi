"""Weather tool - handles weather queries"""

import logging
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class WeatherTool(Tool):
    """Tool for weather queries"""
    
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return "Get weather information (requires API key configuration)"
    
    @property
    def capabilities(self) -> List[str]:
        return ["get_weather", "weather", "temperature", "forecast"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "get_weather":
            return True
        
        weather_keywords = ["weather", "temperature", "forecast", "how's the weather"]
        return any(kw in text_lower for kw in weather_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute weather query"""
        location = entities[0] if entities else "your location"
        
        # TODO: Integrate with weather API (OpenWeatherMap, etc.)
        return f"I'm sorry, weather information is not yet configured. You asked about the weather in {location}. To enable this, please configure a weather API key in settings."


