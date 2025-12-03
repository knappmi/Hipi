"""Emotional intelligence - recognizes and responds to emotions"""

import logging
import re
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmotionalIntelligence:
    """Recognizes emotions and responds appropriately"""
    
    def __init__(self):
        self.emotion_patterns = {
            "happy": [
                r"\b(great|awesome|wonderful|fantastic|excellent|amazing|love|happy|excited)\b",
                r"!+",  # Multiple exclamation marks
            ],
            "frustrated": [
                r"\b(ugh|frustrated|annoying|stupid|hate|can't|won't work)\b",
                r"\b(why|how come|not working)\b",
            ],
            "tired": [
                r"\b(tired|exhausted|sleepy|worn out|need rest)\b",
            ],
            "stressed": [
                r"\b(stressed|overwhelmed|too much|busy|rushed)\b",
            ],
            "grateful": [
                r"\b(thanks|thank you|appreciate|grateful)\b",
            ],
        }
        
        self.emotion_responses = {
            "happy": [
                "That's great to hear!",
                "Awesome!",
                "I'm glad!",
                "Wonderful!",
            ],
            "frustrated": [
                "I understand that can be frustrating. Let me help.",
                "I'm here to help with that.",
                "Let's figure this out together.",
            ],
            "tired": [
                "You sound tired. Maybe it's time to rest?",
                "Take it easy!",
                "Want me to help you wind down?",
            ],
            "stressed": [
                "I can help take some things off your plate.",
                "Let me help you with that.",
                "Take a deep breath. We'll get through this.",
            ],
            "grateful": [
                "You're welcome!",
                "Happy to help!",
                "Anytime!",
                "My pleasure!",
            ],
        }
    
    def detect_emotion(self, text: str) -> Optional[str]:
        """Detect emotion in text"""
        text_lower = text.lower()
        
        emotion_scores = {}
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def get_empathetic_response(self, emotion: str, original_response: str) -> str:
        """Get an empathetic response based on detected emotion"""
        import random
        if emotion in self.emotion_responses:
            empathetic_prefix = random.choice(self.emotion_responses[emotion])
            return f"{empathetic_prefix} {original_response}"
        
        return original_response
    
    def adjust_tone(self, emotion: Optional[str], response: str) -> str:
        """Adjust response tone based on emotion"""
        if emotion == "happy":
            # Make it more enthusiastic
            response = response.replace(".", "!")
            if not response.endswith("!"):
                response += "!"
        elif emotion == "frustrated":
            # Be more supportive and helpful
            if not response.startswith(("I", "Let", "We")):
                response = "I understand. " + response
        elif emotion == "tired":
            # Be gentle and calming
            response = response.replace("!", ".")
        
        return response

