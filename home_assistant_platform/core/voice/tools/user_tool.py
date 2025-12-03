"""User management tool - handles user voice commands"""

import logging
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class UserTool(Tool):
    """Tool for user management"""
    
    def __init__(self, user_manager=None):
        self.user_manager = user_manager
    
    @property
    def name(self) -> str:
        return "user"
    
    @property
    def description(self) -> str:
        return "Manage users and switch between users"
    
    @property
    def capabilities(self) -> List[str]:
        return ["switch_user", "who_am_i", "list_users", "user"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["switch_user", "who_am_i"]:
            return True
        
        user_keywords = [
            "switch user", "change user", "who am i", "who is this",
            "i am", "this is", "user", "login as"
        ]
        
        return any(kw in text_lower for kw in user_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute user operation"""
        if not self.user_manager:
            return "User system is not available"
        
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "who_am_i" or "who am i" in text_lower or "who is this" in text_lower:
            current_user = self.user_manager.get_current_user()
            if current_user:
                return f"You are {current_user.display_name} ({current_user.username})"
            return "No user is currently active"
        
        elif intent_lower == "switch_user" or "switch user" in text_lower or "change user" in text_lower:
            # Extract username
            username = self._extract_username(text_lower)
            if username:
                user = self.user_manager.get_user_by_username(username)
                if user:
                    self.user_manager.set_current_user(user.id)
                    return f"Switched to user: {user.display_name}"
                return f"User '{username}' not found"
            return "I didn't understand which user you want to switch to. Try saying 'switch user to John'."
        
        elif "i am" in text_lower or "this is" in text_lower:
            # Try to identify user from voice or extract name
            username = self._extract_username(text_lower)
            if username:
                user = self.user_manager.get_user_by_username(username)
                if user:
                    self.user_manager.set_current_user(user.id)
                    return f"Hello {user.display_name}!"
                return f"User '{username}' not found"
            return "I didn't understand. Try saying 'I am John' or 'This is John'."
        
        elif "list users" in text_lower:
            users = self.user_manager.list_users()
            if users:
                user_list = ", ".join([u.display_name for u in users])
                return f"Available users: {user_list}"
            return "No users found"
        
        return "I didn't understand the user command. Try saying 'who am I' or 'switch user to John'."
    
    def _extract_username(self, text: str) -> Optional[str]:
        """Extract username from text"""
        import re
        
        # Patterns: "switch user to John", "I am John", "this is John"
        patterns = [
            r"switch user to (.+)",
            r"change user to (.+)",
            r"i am (.+)",
            r"this is (.+)",
            r"login as (.+)",
            r"user (.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                username = match.group(1).strip()
                # Remove common words
                username = username.replace("user", "").strip()
                return username
        
        return None

