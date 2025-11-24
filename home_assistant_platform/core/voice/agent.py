"""Agentic AI system - Base agent that routes requests to tools"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Abstract base class for all tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the agent"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of capabilities this tool can handle"""
        pass
    
    @abstractmethod
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        pass
    
    @abstractmethod
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute the tool and return response"""
        pass


class Agent:
    """Base agent that routes requests to appropriate tools"""
    
    def __init__(self):
        self.tools: List[Tool] = []
        self.tool_registry: Dict[str, Tool] = {}
        logger.info("Agent initialized")
    
    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self.tools.append(tool)
        self.tool_registry[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} - {tool.description}")
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self.tool_registry:
            tool = self.tool_registry[tool_name]
            self.tools.remove(tool)
            del self.tool_registry[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools and their capabilities"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "capabilities": tool.capabilities
            }
            for tool in self.tools
        ]
    
    def select_tool(self, intent: str, text: str, entities: List[str]) -> Optional[Tool]:
        """Select the best tool to handle the request"""
        # Score each tool based on how well it can handle the request
        scored_tools = []
        
        for tool in self.tools:
            if tool.can_handle(intent, text, entities):
                # Calculate a simple score (can be enhanced with ML)
                score = self._calculate_tool_score(tool, intent, text, entities)
                scored_tools.append((score, tool))
        
        if not scored_tools:
            return None
        
        # Return the tool with highest score
        scored_tools.sort(key=lambda x: x[0], reverse=True)
        return scored_tools[0][1]
    
    def _calculate_tool_score(self, tool: Tool, intent: str, text: str, entities: List[str]) -> float:
        """Calculate how well a tool matches the request"""
        score = 0.0
        
        # Exact intent match
        if intent in tool.capabilities:
            score += 10.0
        
        # Intent type match (e.g., "get_time" matches "get_*")
        for capability in tool.capabilities:
            if intent.startswith(capability.split('_')[0]):
                score += 5.0
        
        # Text contains capability keywords
        text_lower = text.lower()
        for capability in tool.capabilities:
            if capability.replace('_', ' ') in text_lower:
                score += 3.0
        
        return score
    
    def handle_request(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Handle a request by routing to appropriate tool"""
        logger.info(f"Agent handling request: intent={intent}, text={text}")
        
        # Select the best tool
        tool = self.select_tool(intent, text, entities)
        
        if not tool:
            logger.warning(f"No tool found to handle: intent={intent}, text={text}")
            return None
        
        logger.info(f"Selected tool: {tool.name}")
        
        try:
            # Execute the tool
            response = tool.execute(intent, text, entities)
            return response
        except Exception as e:
            logger.error(f"Error executing tool {tool.name}: {e}", exc_info=True)
            return f"I encountered an error while using {tool.name}."



