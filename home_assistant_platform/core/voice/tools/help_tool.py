"""Help tool - provides help and lists available capabilities"""

import logging
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class HelpTool(Tool):
    """Tool for providing help information"""
    
    def __init__(self, agent):
        self.agent = agent
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "Provide help and list available capabilities"
    
    @property
    def capabilities(self) -> List[str]:
        return ["help", "what_can_you_do", "capabilities"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "help":
            return True
        
        help_keywords = ["help", "what can you do", "capabilities", "what do you do"]
        return any(kw in text_lower for kw in help_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute help request"""
        tools = self.agent.get_available_tools()
        
        if not tools:
            return "I don't have any tools available right now."
        
        response = "I can help you with:\n"
        for tool in tools:
            capabilities_str = ", ".join(tool["capabilities"][:3])  # Show first 3
            response += f"- {tool['description']} ({capabilities_str})\n"
        
        response += "\nJust say 'Hi Pie' followed by your question!"
        return response



