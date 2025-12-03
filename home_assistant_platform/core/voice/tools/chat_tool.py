"""Casual chat tool - handles friendly conversation"""

import logging
import random
from typing import List, Optional
from datetime import datetime
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class ChatTool(Tool):
    """Tool for casual conversation"""
    
    def __init__(self, personality_engine=None, memory_system=None):
        self.personality = personality_engine
        self.memory = memory_system
    
    @property
    def name(self) -> str:
        return "chat"
    
    @property
    def description(self) -> str:
        return "Handle casual conversation and friendly chat"
    
    @property
    def capabilities(self) -> List[str]:
        return ["greeting", "goodbye", "casual_chat", "how_are_you", "small_talk"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["greeting", "goodbye", "casual_chat"]:
            return True
        
        chat_keywords = [
            "how are you", "what's up", "how's it going",
            "how do you feel", "tell me about yourself"
        ]
        
        return any(kw in text_lower for kw in chat_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute chat operation"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "greeting" or any(word in text_lower for word in ["hi", "hello", "hey"]):
            hour = datetime.now().hour
            if 5 <= hour < 12:
                return random.choice([
                    "Good morning! How can I help you today?",
                    "Morning! What's on your mind?",
                    "Good morning! Ready to start the day?",
                ])
            elif 12 <= hour < 17:
                return random.choice([
                    "Good afternoon! How can I help?",
                    "Afternoon! What can I do for you?",
                    "Hey there! What's up?",
                ])
            elif 17 <= hour < 21:
                return random.choice([
                    "Good evening! How can I help?",
                    "Evening! How was your day?",
                    "Hey! What can I do for you?",
                ])
            else:
                return random.choice([
                    "Hey! Still up? How can I help?",
                    "Hi there! What's going on?",
                    "Hello! What can I do for you?",
                ])
        
        elif intent_lower == "goodbye" or any(word in text_lower for word in ["bye", "goodbye", "see you"]):
            return random.choice([
                "See you later!",
                "Have a great day!",
                "Take care!",
                "Talk to you soon!",
                "Bye!",
            ])
        
        elif "how are you" in text_lower:
            return random.choice([
                "I'm doing great, thanks for asking! How are you?",
                "I'm doing well! How about you?",
                "Pretty good! How can I help you today?",
                "I'm great! What's on your mind?",
            ])
        
        elif "what's up" in text_lower or "whats up" in text_lower:
            return random.choice([
                "Not much! Just here to help. What can I do for you?",
                "Just hanging out, ready to help! What's going on?",
                "All good! What can I help with?",
            ])
        
        elif "tell me about yourself" in text_lower:
            return "I'm your home assistant! I can help control your devices, set reminders, play music, and lots more. What would you like to do?"
        
        return "I'm here to help! What can I do for you?"

