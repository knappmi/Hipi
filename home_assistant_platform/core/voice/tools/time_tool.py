"""Time tool - handles time and date queries"""

import logging
import datetime
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class TimeTool(Tool):
    """Tool for time and date queries"""
    
    @property
    def name(self) -> str:
        return "time"
    
    @property
    def description(self) -> str:
        return "Get current time and date information"
    
    @property
    def capabilities(self) -> List[str]:
        return ["get_time", "get_date", "time", "date"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        # Check intent
        if intent_lower in ["get_time", "get_date"]:
            return True
        
        # Check text for time/date keywords
        time_keywords = ["time", "what time", "what's the time", "time is it"]
        date_keywords = ["date", "what date", "what's the date", "date is it", "what day"]
        
        return any(kw in text_lower for kw in time_keywords + date_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute time/date query"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        # Determine if asking for time or date
        if "date" in text_lower or "day" in text_lower or intent_lower == "get_date":
            return self._get_date()
        else:
            return self._get_time()
    
    def _get_time(self) -> str:
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The time is {time_str}"
    
    def _get_date(self) -> str:
        """Get current date"""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}"



