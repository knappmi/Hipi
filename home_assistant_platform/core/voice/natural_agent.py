"""Enhanced agent with personality and natural conversation"""

import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from home_assistant_platform.core.voice.agent import Agent, Tool
from home_assistant_platform.core.personality.personality_engine import PersonalityEngine
from home_assistant_platform.core.personality.memory_system import MemorySystem
from home_assistant_platform.core.personality.emotional_intelligence import EmotionalIntelligence

logger = logging.getLogger(__name__)


class NaturalAgent(Agent):
    """Enhanced agent with personality, memory, and emotional intelligence"""
    
    def __init__(self, user_manager=None):
        super().__init__()
        self.personality = PersonalityEngine(user_manager)
        self.memory = MemorySystem()
        self.emotional_intelligence = EmotionalIntelligence()
        self.conversation_count = 0
    
    def handle_request(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Handle a request with personality and context"""
        # Detect emotion
        emotion = self.emotional_intelligence.detect_emotion(text)
        
        # Get conversation context
        context = self.personality.get_conversation_context()
        context["emotion"] = emotion
        context["conversation_count"] = self.conversation_count
        
        # Handle greeting
        if intent == "greeting" or any(word in text.lower() for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            self.conversation_count += 1
            greeting = self.personality.get_greeting()
            
            # Add proactive suggestion occasionally
            if self.conversation_count == 1 or random.random() < 0.2:
                suggestion = self.personality.get_proactive_suggestion()
                if suggestion:
                    return f"{greeting} {suggestion}"
            
            return greeting
        
        # Handle goodbye
        if intent == "goodbye" or any(word in text.lower() for word in ["bye", "goodbye", "see you", "later"]):
            return self.personality.get_goodbye()
        
        # Get base response from parent class
        response = super().handle_request(intent, text, entities)
        
        if not response:
            # Try to be helpful even if we don't understand
            helpful_responses = [
                "I'm not sure I understand. Can you try rephrasing that?",
                "Hmm, I'm not quite sure what you mean. Could you say that differently?",
                "I didn't catch that. Mind trying again?",
            ]
            response = random.choice(helpful_responses)
        
        # Enhance response with personality
        response = self.personality.personalize_response(response)
        response = self.personality.add_context_to_response(response, context)
        
        # Add emotional intelligence
        if emotion:
            response = self.emotional_intelligence.get_empathetic_response(emotion, response)
            response = self.emotional_intelligence.adjust_tone(emotion, response)
        
        # Add humor occasionally
        response = self.personality.add_humor(response, context)
        
        # Remember conversation
        self.personality.remember_conversation(text, response)
        
        # Extract and remember information
        self._extract_and_remember(text, entities)
        
        return response
    
    def _extract_and_remember(self, text: str, entities: List[str]):
        """Extract information from conversation and remember it"""
        text_lower = text.lower()
        
        # Remember names mentioned
        if "my name is" in text_lower or "i'm" in text_lower or "i am" in text_lower:
            # Try to extract name
            import re
            name_match = re.search(r"(?:my name is|i'm|i am)\s+([A-Z][a-z]+)", text)
            if name_match:
                name = name_match.group(1)
                self.memory.remember(f"user_name", name, memory_type="fact")
        
        # Remember preferences
        if "i like" in text_lower or "i prefer" in text_lower or "i love" in text_lower:
            # Extract preference
            import re
            pref_match = re.search(r"(?:i like|i prefer|i love)\s+(.+)", text_lower)
            if pref_match:
                preference = pref_match.group(1).strip()
                self.memory.remember(f"preference_{preference}", True, memory_type="preference")
        
        # Remember family members
        if "my" in text_lower and any(word in text_lower for word in ["wife", "husband", "son", "daughter", "mom", "dad", "brother", "sister"]):
            import re
            family_match = re.search(r"my\s+(wife|husband|son|daughter|mom|dad|brother|sister)\s+is\s+([A-Z][a-z]+)", text)
            if family_match:
                relationship = family_match.group(1)
                name = family_match.group(2)
                self.personality.remember_family_member(name, relationship)
                self.memory.remember(f"family_{name}", {"relationship": relationship}, memory_type="relationship")

