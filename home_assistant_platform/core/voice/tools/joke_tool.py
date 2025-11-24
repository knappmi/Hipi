"""Joke tool - tells jokes"""

import logging
import random
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class JokeTool(Tool):
    """Tool for telling jokes"""
    
    def __init__(self):
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
            "Why did the bicycle fall over? Because it was two tired!",
            "What do you call a sleeping bull? A bulldozer!",
        ]
    
    @property
    def name(self) -> str:
        return "joke"
    
    @property
    def description(self) -> str:
        return "Tell jokes and make you laugh"
    
    @property
    def capabilities(self) -> List[str]:
        return ["tell_joke", "joke", "humor", "laugh"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "tell_joke":
            return True
        
        joke_keywords = ["joke", "tell me a joke", "make me laugh", "funny", "humor"]
        return any(kw in text_lower for kw in joke_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute joke telling"""
        return random.choice(self.jokes)



