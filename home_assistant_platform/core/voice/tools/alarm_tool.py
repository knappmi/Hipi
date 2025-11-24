"""Alarm tool - handles alarm setting and management"""

import logging
import re
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class AlarmTool(Tool):
    """Tool for alarm management"""
    
    def __init__(self):
        self.alarms = []  # Simple in-memory storage
    
    @property
    def name(self) -> str:
        return "alarm"
    
    @property
    def description(self) -> str:
        return "Set, list, and manage alarms"
    
    @property
    def capabilities(self) -> List[str]:
        return ["set_alarm", "list_alarms", "alarm"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["set_alarm", "list_alarms"]:
            return True
        
        alarm_keywords = ["alarm", "set alarm", "list alarms", "what alarms"]
        return any(kw in text_lower for kw in alarm_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute alarm operation"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "list_alarms" or "list" in text_lower or "what alarms" in text_lower:
            return self._list_alarms()
        else:
            return self._set_alarm(text)
    
    def _set_alarm(self, text: str) -> str:
        """Set an alarm"""
        # Simple parsing - look for time patterns
        time_patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm)?",
            r"(\d{1,2})\s*(am|pm)",
            r"in (\d+)\s*(minutes?|hours?|mins?)",
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                # TODO: Implement actual alarm scheduling
                return "I'll set an alarm for you. Note: Full alarm functionality is coming soon!"
        
        return "I couldn't understand the time for the alarm. Try saying something like 'set alarm for 3 PM' or 'alarm in 30 minutes'."
    
    def _list_alarms(self) -> str:
        """List all alarms"""
        if not self.alarms:
            return "You don't have any alarms set."
        
        alarm_list = ", ".join([str(alarm) for alarm in self.alarms])
        return f"You have {len(self.alarms)} alarm(s) set: {alarm_list}"



