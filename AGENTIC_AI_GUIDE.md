# Agentic AI System Guide

## Overview

Your platform now uses an **agentic AI architecture** where a base `Agent` receives requests and intelligently routes them to specialized `Tool` implementations. This makes it easy to add new capabilities without modifying core code.

## Architecture

```
User Request → Agent → Tool Selection → Tool Execution → Response
```

1. **Agent**: Base router that receives intents and selects the best tool
2. **Tools**: Modular, focused implementations of specific capabilities
3. **Tool Registry**: Dynamic registry of available tools

## Current Tools

- **TimeTool**: Time and date queries
- **JokeTool**: Tells jokes
- **WeatherTool**: Weather information (placeholder)
- **AlarmTool**: Alarm management
- **HelpTool**: Lists available capabilities

## Adding a New Tool

### Step 1: Create Tool File

Create `home_assistant_platform/core/voice/tools/my_tool.py`:

```python
from home_assistant_platform.core.voice.agent import Tool
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "What this tool does"
    
    @property
    def capabilities(self) -> List[str]:
        return ["my_capability", "another_capability"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Return True if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        # Check intent
        if intent_lower in ["my_capability", "another_capability"]:
            return True
        
        # Check text for keywords
        keywords = ["my keyword", "another keyword"]
        return any(kw in text_lower for kw in keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute the tool and return response text"""
        # Your tool logic here
        return "Tool response"
```

### Step 2: Register Tool

In `home_assistant_platform/core/main.py`, add:

```python
from home_assistant_platform.core.voice.tools.my_tool import MyCustomTool

# In the voice initialization section:
app.state.agent.register_tool(MyCustomTool())
```

### Step 3: Add Intent Patterns (Optional)

If your tool needs new intent patterns, add them to `intent_processor.py`:

```python
"my_capability": [
    re.compile(r"my pattern (.+)", re.IGNORECASE),
],
```

## Example: Calculator Tool

```python
from home_assistant_platform.core.voice.agent import Tool
from typing import List, Optional
import re

class CalculatorTool(Tool):
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "Perform mathematical calculations"
    
    @property
    def capabilities(self) -> List[str]:
        return ["calculate", "math", "compute"]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower == "calculate":
            return True
        
        math_keywords = ["plus", "minus", "times", "divided", "multiply", "add", "subtract"]
        return any(kw in text_lower for kw in math_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        # Simple math parsing (enhance as needed)
        text_lower = text.lower()
        
        # Replace words with operators
        replacements = {
            "plus": "+", "minus": "-", "times": "*",
            "multiplied by": "*", "divided by": "/", "over": "/"
        }
        
        for word, op in replacements.items():
            text_lower = text_lower.replace(word, op)
        
        # Extract numbers and operators (simplified)
        try:
            # Use a safe math evaluator in production
            # For now, return placeholder
            return "Calculator functionality coming soon!"
        except:
            return "I couldn't understand that calculation."
```

## Tool Selection Algorithm

The agent uses a scoring system to select the best tool:

1. **Exact intent match**: +10 points
2. **Intent type match**: +5 points  
3. **Keyword match**: +3 points

The tool with the highest score is selected.

## API Endpoint (Future Enhancement)

You can add an API endpoint to dynamically register tools:

```python
@router.post("/tools/register")
async def register_tool(request: Request, tool_data: dict):
    # Dynamic tool registration
    # This would allow plugins to register tools at runtime
    pass
```

## Benefits

1. **Modularity**: Each tool is independent
2. **Easy onboarding**: Add new tools in minutes
3. **Scalability**: Tools can be distributed as plugins
4. **Testability**: Test tools in isolation
5. **Extensibility**: No core code changes needed

## Best Practices

1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Capabilities**: List all intents/keywords your tool handles
3. **Error Handling**: Return user-friendly error messages
4. **Logging**: Log important operations
5. **Documentation**: Document your tool's purpose and usage

## Testing Your Tool

```python
from home_assistant_platform.core.voice.tools.my_tool import MyCustomTool

tool = MyCustomTool()
print(f"Can handle: {tool.can_handle('my_capability', 'my keyword', [])}")
print(f"Response: {tool.execute('my_capability', 'my keyword', [])}")
```

## Next Steps

- Add more tools (calculator, news, reminders, etc.)
- Integrate LLM for better tool selection
- Add tool discovery API
- Create tool marketplace
- Add tool versioning and updates



