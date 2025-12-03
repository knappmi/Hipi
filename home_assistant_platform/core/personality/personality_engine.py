"""Personality engine - makes the assistant feel more natural and family-friendly"""

import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from home_assistant_platform.core.users.user_manager import UserManager

logger = logging.getLogger(__name__)


class PersonalityEngine:
    """Adds personality and natural conversation to the assistant"""
    
    def __init__(self, user_manager=None):
        self.user_manager = user_manager
        self.conversation_history: List[Dict[str, Any]] = []
        self.family_members: Dict[str, Dict[str, Any]] = {}
        self.personality_traits = {
            "warmth": 0.8,  # How warm and friendly (0-1)
            "humor": 0.7,  # How funny (0-1)
            "proactivity": 0.6,  # How proactive (0-1)
            "formality": 0.3,  # How formal (0-1, lower = more casual)
        }
        self.greetings = [
            "Hey there!",
            "Hi!",
            "Hello!",
            "Hey!",
            "What's up?",
            "How can I help?",
        ]
        self.goodbyes = [
            "See you later!",
            "Have a great day!",
            "Take care!",
            "Talk to you soon!",
            "Bye!",
            "Catch you later!",
        ]
        self.acknowledgments = [
            "Got it!",
            "Sure thing!",
            "On it!",
            "You got it!",
            "Absolutely!",
            "No problem!",
        ]
        self.apologies = [
            "Sorry about that.",
            "My bad!",
            "Oops, let me fix that.",
            "Sorry, I didn't catch that.",
        ]
    
    def personalize_response(self, response: str, user_id: str = "default") -> str:
        """Personalize a response based on user and context"""
        # Get user info
        user = None
        if self.user_manager:
            user = self.user_manager.get_current_user()
        
        # Add casual touches
        if self.personality_traits["formality"] < 0.5:
            # Make it more casual
            response = response.replace("I have", "I've got")
            response = response.replace("I will", "I'll")
            response = response.replace("cannot", "can't")
            response = response.replace("do not", "don't")
        
        # Add warmth
        if self.personality_traits["warmth"] > 0.7:
            if not response.startswith(("I've", "I'll", "I'm", "I", "Got", "Sure")):
                if random.random() < 0.3:
                    response = random.choice(["Sure! ", "Of course! ", ""]) + response
        
        # Add name if we know the user
        if user and user.display_name and random.random() < 0.2:
            if not any(word in response.lower() for word in ["you", "your"]):
                response = response.replace(".", f", {user.display_name}.")
        
        return response
    
    def get_greeting(self, time_of_day: Optional[str] = None) -> str:
        """Get a personalized greeting"""
        if not time_of_day:
            hour = datetime.now().hour
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"
        
        greetings = {
            "morning": ["Good morning!", "Morning!", "Rise and shine!", "Good morning! Ready to start the day?"],
            "afternoon": ["Good afternoon!", "Afternoon!", "Hey there!", "How's your day going?"],
            "evening": ["Good evening!", "Evening!", "Hey!", "How was your day?"],
            "night": ["Good night!", "Hey!", "Still up?", "How can I help?"]
        }
        
        return random.choice(greetings.get(time_of_day, self.greetings))
    
    def get_goodbye(self) -> str:
        """Get a personalized goodbye"""
        return random.choice(self.goodyes)
    
    def get_acknowledgment(self) -> str:
        """Get an acknowledgment"""
        return random.choice(self.acknowledgments)
    
    def add_context_to_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add context-aware touches to responses"""
        # Check if this is a follow-up question
        if context.get("is_follow_up"):
            response = "Also, " + response.lower()
        
        # Add time awareness
        hour = datetime.now().hour
        if hour >= 22 or hour < 6:
            if "reminder" in response.lower() or "alarm" in response.lower():
                response += " Don't forget to get some rest!"
        
        return response
    
    def remember_family_member(self, name: str, relationship: str, user_id: str = "default"):
        """Remember a family member"""
        if name not in self.family_members:
            self.family_members[name] = {
                "relationship": relationship,
                "user_id": user_id,
                "first_mentioned": datetime.now()
            }
            logger.info(f"Remembered family member: {name} ({relationship})")
    
    def get_family_reference(self, name: str) -> Optional[str]:
        """Get a natural reference to a family member"""
        if name in self.family_members:
            member = self.family_members[name]
            relationship = member["relationship"]
            return f"your {relationship} {name}"
        return None
    
    def add_humor(self, response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Add humor to responses when appropriate"""
        import random
        if self.personality_traits["humor"] < 0.5:
            return response
        
        # Add occasional light humor
        if random.random() < 0.1:  # 10% chance
            humor_additions = [
                " Easy peasy!",
                " Piece of cake!",
                " Done and done!",
            ]
            if response.endswith("."):
                response = response[:-1] + random.choice(humor_additions) + "."
        
        return response
    
    def get_proactive_suggestion(self, user_id: str = "default") -> Optional[str]:
        """Get a proactive suggestion based on context"""
        if self.personality_traits["proactivity"] < 0.5:
            return None
        
        hour = datetime.now().hour
        
        # Morning suggestions
        if 6 <= hour < 10:
            suggestions = [
                "Would you like me to check the weather for today?",
                "Want me to read your reminders for today?",
                "Should I turn on some morning music?",
            ]
            return random.choice(suggestions)
        
        # Evening suggestions
        if 18 <= hour < 22:
            suggestions = [
                "Want me to set up the movie night scene?",
                "Should I check what's on your calendar for tomorrow?",
                "Want me to dim the lights for the evening?",
            ]
            return random.choice(suggestions)
        
        return None
    
    def remember_conversation(self, user_input: str, assistant_response: str, user_id: str = "default"):
        """Remember a conversation for context"""
        self.conversation_history.append({
            "user_input": user_input,
            "assistant_response": assistant_response,
            "timestamp": datetime.now(),
            "user_id": user_id
        })
        
        # Keep only last 10 conversations
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get recent conversation context"""
        return {
            "recent_count": len(self.conversation_history),
            "is_follow_up": len(self.conversation_history) > 0,
            "last_topic": self.conversation_history[-1]["user_input"] if self.conversation_history else None
        }

