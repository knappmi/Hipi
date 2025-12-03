"""Intent processing for voice commands"""

import logging
import re
from typing import Dict, Optional, List
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class IntentProcessor:
    """Process voice commands and extract intents"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Load intent recognition patterns"""
        # Basic intent patterns - can be extended with ML/NLP
        patterns = {
            # Device control
            "turn_on": [
                re.compile(r"turn on (.+)", re.IGNORECASE),
                re.compile(r"switch on (.+)", re.IGNORECASE),
                re.compile(r"enable (.+)", re.IGNORECASE),
            ],
            "turn_off": [
                re.compile(r"turn off (.+)", re.IGNORECASE),
                re.compile(r"switch off (.+)", re.IGNORECASE),
                re.compile(r"disable (.+)", re.IGNORECASE),
            ],
            "set_temperature": [
                re.compile(r"set temperature to (\d+)", re.IGNORECASE),
                re.compile(r"temperature (\d+)", re.IGNORECASE),
            ],
            "get_status": [
                re.compile(r"what is the status of (.+)", re.IGNORECASE),
                re.compile(r"status of (.+)", re.IGNORECASE),
            ],
            "play_music": [
                re.compile(r"play (.+)", re.IGNORECASE),
                re.compile(r"play music", re.IGNORECASE),
            ],
            # Assistant commands
            "get_time": [
                re.compile(r"what time", re.IGNORECASE),
                re.compile(r"what's the time", re.IGNORECASE),
                re.compile(r"time is it", re.IGNORECASE),
                re.compile(r"tell me the time", re.IGNORECASE),
            ],
            "get_date": [
                re.compile(r"what date", re.IGNORECASE),
                re.compile(r"what's the date", re.IGNORECASE),
                re.compile(r"date is it", re.IGNORECASE),
                re.compile(r"tell me the date", re.IGNORECASE),
            ],
            "get_weather": [
                re.compile(r"weather(?: in (.+))?", re.IGNORECASE),
                re.compile(r"temperature(?: in (.+))?", re.IGNORECASE),
                re.compile(r"how's the weather", re.IGNORECASE),
                re.compile(r"what's the weather", re.IGNORECASE),
            ],
            "tell_joke": [
                re.compile(r"tell me a joke", re.IGNORECASE),
                re.compile(r"joke", re.IGNORECASE),
                re.compile(r"make me laugh", re.IGNORECASE),
            ],
            "set_alarm": [
                re.compile(r"set alarm (?:for )?(.+)", re.IGNORECASE),
                re.compile(r"alarm for (.+)", re.IGNORECASE),
            ],
            "list_alarms": [
                re.compile(r"list alarms", re.IGNORECASE),
                re.compile(r"what alarms", re.IGNORECASE),
                re.compile(r"show alarms", re.IGNORECASE),
            ],
            "calculate": [
                re.compile(r"what is (.+)", re.IGNORECASE),
                re.compile(r"calculate (.+)", re.IGNORECASE),
                re.compile(r"what's (.+)", re.IGNORECASE),
            ],
            "help": [
                re.compile(r"help", re.IGNORECASE),
                re.compile(r"what can you do", re.IGNORECASE),
            ],
            "toggle_conversation": [
                re.compile(r"enable conversation mode", re.IGNORECASE),
                re.compile(r"disable conversation mode", re.IGNORECASE),
                re.compile(r"turn on conversation mode", re.IGNORECASE),
                re.compile(r"turn off conversation mode", re.IGNORECASE),
                re.compile(r"conversation mode", re.IGNORECASE),
            ],
            "search": [
                re.compile(r"search for (.+)", re.IGNORECASE),
                re.compile(r"search (.+)", re.IGNORECASE),
                re.compile(r"look up (.+)", re.IGNORECASE),
                re.compile(r"lookup (.+)", re.IGNORECASE),
                re.compile(r"find (.+)", re.IGNORECASE),
                re.compile(r"google (.+)", re.IGNORECASE),
                re.compile(r"tell me about (.+)", re.IGNORECASE),
                re.compile(r"what is (.+)", re.IGNORECASE),
                re.compile(r"who is (.+)", re.IGNORECASE),
                re.compile(r"wikipedia (.+)", re.IGNORECASE),
            ],
            "set_reminder": [
                re.compile(r"remind me to (.+)", re.IGNORECASE),
                re.compile(r"remind me (.+)", re.IGNORECASE),
                re.compile(r"set reminder (.+)", re.IGNORECASE),
                re.compile(r"create reminder (.+)", re.IGNORECASE),
            ],
            "list_reminders": [
                re.compile(r"list reminders", re.IGNORECASE),
                re.compile(r"what reminders", re.IGNORECASE),
                re.compile(r"show reminders", re.IGNORECASE),
                re.compile(r"my reminders", re.IGNORECASE),
            ],
            "activate_scene": [
                re.compile(r"activate (.+)", re.IGNORECASE),
                re.compile(r"turn on (.+) scene", re.IGNORECASE),
                re.compile(r"set (.+) scene", re.IGNORECASE),
                re.compile(r"movie night", re.IGNORECASE),
                re.compile(r"bedtime", re.IGNORECASE),
                re.compile(r"away mode", re.IGNORECASE),
            ],
            "play_music": [
                re.compile(r"play (.+)", re.IGNORECASE),
                re.compile(r"play music", re.IGNORECASE),
                re.compile(r"play song", re.IGNORECASE),
            ],
            "pause_music": [
                re.compile(r"pause", re.IGNORECASE),
                re.compile(r"pause music", re.IGNORECASE),
            ],
            "stop_music": [
                re.compile(r"stop", re.IGNORECASE),
                re.compile(r"stop music", re.IGNORECASE),
            ],
            "volume": [
                re.compile(r"volume (.+)", re.IGNORECASE),
                re.compile(r"turn volume (.+)", re.IGNORECASE),
                re.compile(r"louder", re.IGNORECASE),
                re.compile(r"quieter", re.IGNORECASE),
            ],
            "switch_user": [
                re.compile(r"switch user to (.+)", re.IGNORECASE),
                re.compile(r"change user to (.+)", re.IGNORECASE),
                re.compile(r"login as (.+)", re.IGNORECASE),
            ],
            "who_am_i": [
                re.compile(r"who am i", re.IGNORECASE),
                re.compile(r"who is this", re.IGNORECASE),
            ],
            "energy_usage": [
                re.compile(r"energy usage", re.IGNORECASE),
                re.compile(r"power consumption", re.IGNORECASE),
                re.compile(r"energy consumption", re.IGNORECASE),
                re.compile(r"how much energy", re.IGNORECASE),
            ],
            "energy_cost": [
                re.compile(r"energy cost", re.IGNORECASE),
                re.compile(r"electricity cost", re.IGNORECASE),
                re.compile(r"energy bill", re.IGNORECASE),
            ],
            "greeting": [
                re.compile(r"^(hi|hello|hey|good morning|good afternoon|good evening)", re.IGNORECASE),
                re.compile(r"^what's up", re.IGNORECASE),
            ],
            "goodbye": [
                re.compile(r"^(bye|goodbye|see you|later|thanks bye)", re.IGNORECASE),
            ],
            "casual_chat": [
                re.compile(r"how are you", re.IGNORECASE),
                re.compile(r"what's up", re.IGNORECASE),
                re.compile(r"how's it going", re.IGNORECASE),
            ],
        }
        return patterns
    
    def process(self, text: str) -> Optional[Dict]:
        """Process text and extract intent"""
        text = text.strip()
        if not text:
            return None
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    entities = match.groups()
                    return {
                        "intent": intent,
                        "entities": entities,
                        "text": text,
                        "confidence": 0.8  # Simple pattern matching
                    }
        
        # Default intent if no match
        return {
            "intent": "unknown",
            "entities": [],
            "text": text,
            "confidence": 0.0
        }
    
    def add_intent_pattern(self, intent: str, pattern: str):
        """Add a new intent pattern"""
        if intent not in self.intent_patterns:
            self.intent_patterns[intent] = []
        
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.intent_patterns[intent].append(compiled_pattern)
            logger.info(f"Added intent pattern for {intent}: {pattern}")
        except Exception as e:
            logger.error(f"Failed to add intent pattern: {e}")

