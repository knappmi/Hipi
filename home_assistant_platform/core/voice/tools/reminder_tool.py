"""Reminder tool - handles reminder voice commands"""

import logging
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class ReminderTool(Tool):
    """Tool for reminder management"""
    
    def __init__(self, reminder_manager=None):
        self.reminder_manager = reminder_manager
    
    @property
    def name(self) -> str:
        return "reminder"
    
    @property
    def description(self) -> str:
        return "Set, list, and manage reminders"
    
    @property
    def capabilities(self) -> List[str]:
        return ["set_reminder", "list_reminders", "reminder", "remind"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["set_reminder", "list_reminders"]:
            return True
        
        reminder_keywords = [
            "remind me", "set reminder", "reminder", "remind me to",
            "what reminders", "list reminders", "show reminders"
        ]
        
        return any(kw in text_lower for kw in reminder_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute reminder operation"""
        if not self.reminder_manager:
            return "Reminder system is not available"
        
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "list_reminders" or "list" in text_lower or "what reminders" in text_lower:
            return self._list_reminders()
        else:
            return self._set_reminder(text)
    
    def _set_reminder(self, text: str) -> str:
        """Set a reminder from voice command"""
        try:
            reminder = self.reminder_manager.parse_reminder_from_text(text)
            
            if reminder:
                time_str = reminder.reminder_time.strftime("%I:%M %p on %B %d")
                recurrence_str = ""
                if reminder.recurrence_type:
                    recurrence_str = f" ({reminder.recurrence_type})"
                
                return f"I've set a reminder to {reminder.title} at {time_str}{recurrence_str}."
            else:
                return "I couldn't understand when you want the reminder. Try saying something like 'remind me to call mom at 3 PM'."
        except Exception as e:
            logger.error(f"Error setting reminder: {e}", exc_info=True)
            return "I encountered an error setting the reminder. Please try again."
    
    def _list_reminders(self) -> str:
        """List upcoming reminders"""
        try:
            reminders = self.reminder_manager.get_upcoming_reminders(hours=24)
            
            if not reminders:
                return "You have no upcoming reminders."
            
            response = f"You have {len(reminders)} upcoming reminder(s):\n"
            for i, reminder in enumerate(reminders[:5], 1):  # Limit to 5
                time_str = reminder.reminder_time.strftime("%I:%M %p on %B %d")
                response += f"{i}. {reminder.title} at {time_str}\n"
            
            return response.strip()
        except Exception as e:
            logger.error(f"Error listing reminders: {e}", exc_info=True)
            return "I encountered an error listing reminders."

