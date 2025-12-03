"""Search tool - handles internet search queries"""

import logging
import re
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)

try:
    from ddgs import DDGS
    DDG_AVAILABLE = True
except ImportError:
    # Fallback to old package name
    try:
        from duckduckgo_search import DDGS
        DDG_AVAILABLE = True
    except ImportError:
        DDG_AVAILABLE = False
        logger.warning("ddgs not available. Install with: pip install ddgs")


class SearchTool(Tool):
    """Tool for internet search queries"""
    
    def __init__(self):
        self.ddgs = None
        if DDG_AVAILABLE:
            try:
                self.ddgs = DDGS()
                logger.info("DuckDuckGo search initialized")
            except Exception as e:
                logger.error(f"Failed to initialize DuckDuckGo search: {e}")
    
    @property
    def name(self) -> str:
        return "search"
    
    @property
    def description(self) -> str:
        return "Search the internet for information, answers, and web content"
    
    @property
    def capabilities(self) -> List[str]:
        return ["search", "search_web", "lookup", "find", "google", "wikipedia"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        # Check intent
        if intent_lower in ["search", "search_web", "lookup", "find"]:
            return True
        
        # Check for search keywords
        search_keywords = [
            "search for", "search", "look up", "lookup", "find", 
            "google", "what is", "who is", "tell me about",
            "wikipedia", "search the web", "web search"
        ]
        
        # Check if text contains search patterns
        if any(kw in text_lower for kw in search_keywords):
            return True
        
        # Check for question patterns that might need search
        question_patterns = [
            r"^(what|who|where|when|why|how)\s+is\s+",
            r"^(what|who|where|when|why|how)\s+are\s+",
            r"^(what|who|where|when|why|how)\s+does\s+",
        ]
        
        for pattern in question_patterns:
            if re.match(pattern, text_lower):
                return True
        
        return False
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute search query"""
        if not DDG_AVAILABLE or not self.ddgs:
            return "Internet search is not available. Please install ddgs library: pip install ddgs"
        
        # Extract search query from text
        query = self._extract_query(text)
        
        if not query:
            return "I didn't understand what you want me to search for. Please try again with a clearer search query."
        
        try:
            logger.info(f"Searching for: {query}")
            
            # Try to get instant answer first (for definitions, facts, etc.)
            instant_answer = self._get_instant_answer(query)
            if instant_answer:
                return instant_answer
            
            # Perform web search
            results = list(self.ddgs.text(query, max_results=3))
            
            if not results:
                return f"I couldn't find any results for '{query}'. Please try rephrasing your search."
            
            # Format results
            response = f"I found information about '{query}':\n\n"
            
            for i, result in enumerate(results[:2], 1):  # Limit to top 2 results
                title = result.get('title', 'No title')
                snippet = result.get('body', 'No description')
                url = result.get('href', '')
                
                # Truncate snippet if too long
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."
                
                response += f"{i}. {title}\n"
                response += f"   {snippet}\n"
                if url:
                    response += f"   Source: {url}\n"
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error performing search: {e}", exc_info=True)
            return f"I encountered an error while searching. Please try again later."
    
    def _extract_query(self, text: str) -> str:
        """Extract search query from user text"""
        text_lower = text.lower()
        
        # Remove common search prefixes
        prefixes = [
            "search for", "search", "look up", "lookup", "find",
            "google", "search the web", "web search", "tell me about",
            "what is", "who is", "what are", "who are"
        ]
        
        query = text
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                query = text[len(prefix):].strip()
                break
        
        # Remove question words at the start
        query = re.sub(r"^(what|who|where|when|why|how)\s+is\s+", "", query, flags=re.IGNORECASE)
        query = re.sub(r"^(what|who|where|when|why|how)\s+are\s+", "", query, flags=re.IGNORECASE)
        query = re.sub(r"^(what|who|where|when|why|how)\s+does\s+", "", query, flags=re.IGNORECASE)
        
        # Clean up
        query = query.strip()
        query = re.sub(r"\?+$", "", query)  # Remove trailing question marks
        
        return query if query else text.strip()
    
    def _get_instant_answer(self, query: str) -> Optional[str]:
        """Try to get instant answer from DuckDuckGo"""
        try:
            # DuckDuckGo instant answer API
            results = list(self.ddgs.answers(query))
            if results:
                answer = results[0]
                text = answer.get('text', '')
                if text and len(text) > 0:
                    # Truncate if too long
                    if len(text) > 300:
                        text = text[:300] + "..."
                    return f"Here's what I found about '{query}':\n\n{text}"
        except Exception as e:
            logger.debug(f"Could not get instant answer: {e}")
        
        return None

