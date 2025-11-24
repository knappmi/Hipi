# Tool Development Guide

## Creating a New Tool

To add a new tool to the agentic system, create a new file in `tools/` that implements the `Tool` interface.

### Example Tool

```python
from home_assistant_platform.core.voice.agent import Tool
from typing import List, Optional

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
        return "my keyword" in text_lower or intent == "my_capability"
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute the tool and return response text"""
        # Your tool logic here
        return "Tool response"
```

### Registering Your Tool

In `core/main.py`, add:

```python
from home_assistant_platform.core.voice.tools.my_tool import MyCustomTool

app.state.agent.register_tool(MyCustomTool())
```

### Tool Interface Methods

- `name`: Unique identifier for the tool
- `description`: Human-readable description
- `capabilities`: List of capability strings this tool handles
- `can_handle()`: Returns True if tool can handle the request
- `execute()`: Executes the tool and returns response text (or None)

### Best Practices

1. **Keep tools focused**: Each tool should do one thing well
2. **Clear capabilities**: List all intents/keywords your tool handles
3. **Error handling**: Return user-friendly error messages
4. **Logging**: Log important operations for debugging
5. **Async support**: For I/O operations, consider async (future enhancement)

### Example: Calculator Tool

```python
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
        return intent == "calculate" or any(op in text for op in ["plus", "minus", "times", "divided"])
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        # Parse and calculate
        try:
            result = self._calculate(text)
            return f"The answer is {result}"
        except:
            return "I couldn't understand that calculation."
```



