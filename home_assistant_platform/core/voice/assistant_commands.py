"""Assistant command handlers for basic functionality"""

import logging
import datetime
import random
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class AssistantCommands:
    """Handle basic assistant commands"""
    
    def __init__(self):
        self.alarms = []  # Simple in-memory alarm storage
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the coffee file a police report? It got mugged!",
            "What's a computer's favorite snack? Microchips!",
        ]
    
    def handle_command(self, intent: str, text: str, entities: list) -> Optional[str]:
        """Handle an assistant command and return response text"""
        intent_lower = intent.lower()
        text_lower = text.lower()
        
        # Time commands
        if intent_lower == "get_time" or any(word in text_lower for word in ["what time", "what's the time", "time is it", "tell me the time"]):
            return self.get_time()
        
        # Date commands
        if intent_lower == "get_date" or any(word in text_lower for word in ["what date", "what's the date", "date is it", "tell me the date"]):
            return self.get_date()
        
        # Weather commands
        if intent_lower == "get_weather" or any(word in text_lower for word in ["weather", "temperature", "how's the weather"]):
            location = entities[0] if entities else None
            return self.get_weather(location)
        
        # Joke commands
        if intent_lower == "tell_joke" or any(word in text_lower for word in ["tell me a joke", "joke", "make me laugh"]):
            return self.tell_joke()
        
        # Alarm commands
        if intent_lower == "set_alarm" or any(word in text_lower for word in ["set alarm", "alarm for"]):
            return self.set_alarm(text)
        
        if intent_lower == "list_alarms" or any(word in text_lower for word in ["list alarms", "what alarms", "show alarms"]):
            return self.list_alarms()
        
        # Calculator
        if intent_lower == "calculate" or any(word in text_lower for word in ["what is", "calculate", "what's"]):
            return self.calculate(text)
        
        # Help
        if intent_lower == "help" or "help" in text_lower:
            return self.get_help()
        
        return None
    
    def get_time(self) -> str:
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The time is {time_str}"
    
    def get_date(self) -> str:
        """Get current date"""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}"
    
    def get_weather(self, location: Optional[str] = None) -> str:
        """Get weather information"""
        if not location:
            location = "your location"
        
        # For now, return a placeholder
        # In production, integrate with a weather API like OpenWeatherMap
        return f"I'm sorry, I don't have weather information configured yet. You asked about the weather in {location}."
    
    def tell_joke(self) -> str:
        """Tell a random joke"""
        joke = random.choice(self.jokes)
        return joke
    
    def set_alarm(self, text: str) -> str:
        """Set an alarm from text"""
        # Simple parsing - look for time patterns
        import re
        time_patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm)?",
            r"(\d{1,2})\s*(am|pm)",
            r"in (\d+)\s*(minutes?|hours?|mins?)",
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                # For now, just acknowledge
                # In production, implement actual alarm scheduling
                return f"I'll set an alarm for you. Note: Alarm functionality is not fully implemented yet."
        
        return "I couldn't understand the time for the alarm. Try saying something like 'set alarm for 3 PM' or 'alarm in 30 minutes'."
    
    def list_alarms(self) -> str:
        """List all set alarms"""
        if not self.alarms:
            return "You don't have any alarms set."
        
        alarm_list = ", ".join([str(alarm) for alarm in self.alarms])
        return f"You have {len(self.alarms)} alarm(s) set: {alarm_list}"
    
    def calculate(self, text: str) -> str:
        """Perform simple calculations"""
        import re
        # Look for math expressions
        # Simple pattern: "what is 5 plus 3" or "calculate 10 * 2"
        text_lower = text.lower()
        
        # Replace words with operators
        replacements = {
            "plus": "+",
            "minus": "-",
            "times": "*",
            "multiplied by": "*",
            "divided by": "/",
            "over": "/",
        }
        
        for word, op in replacements.items():
            text_lower = text_lower.replace(word, op)
        
        # Try to extract numbers and operators
        try:
            # Simple evaluation (be careful in production - use a safe math parser)
            # For now, just acknowledge
            return "I can help with calculations, but the full calculator feature is not yet implemented. Try asking 'what is 5 plus 3'."
        except:
            return "I couldn't understand that calculation. Try saying something like 'what is 5 plus 3'."
    
    def get_help(self) -> str:
        """Get help information"""
        return """I can help you with:
- Telling the time: 'What time is it?'
- Telling the date: 'What's the date?'
- Weather: 'What's the weather?'
- Jokes: 'Tell me a joke'
- Alarms: 'Set alarm for 3 PM'
- Calculations: 'What is 5 plus 3'
Just say 'Hi Pie' followed by your question!"""



