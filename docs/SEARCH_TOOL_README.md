# Internet Search Tool

A new voice tool that enables internet search functionality in the Home Assistant Platform.

## Features

- **Web Search**: Search the internet for information using DuckDuckGo
- **Instant Answers**: Get quick answers for common queries
- **Voice Commands**: Use natural language to search
- **Multiple Query Formats**: Supports various ways to ask for searches

## Installation

The search tool requires the `ddgs` library:

```bash
pip install ddgs
```

Or add to requirements.txt:
```
ddgs>=1.0.0
```

## Usage

### Voice Commands

You can search the internet using various voice commands:

- **"Search for Python tutorials"**
- **"What is artificial intelligence"**
- **"Look up the weather"**
- **"Tell me about raspberry pi"**
- **"Who is Albert Einstein"**
- **"Google machine learning"**
- **"Wikipedia Python programming"**

### API Usage

You can also use the search tool via the API:

```bash
# Process a search command
curl -X POST http://localhost:8000/api/v1/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "search for Python programming"}'
```

## How It Works

1. **Intent Recognition**: The tool recognizes search-related intents and keywords
2. **Query Extraction**: Extracts the actual search query from the user's text
3. **Instant Answers**: First tries to get an instant answer (for definitions, facts)
4. **Web Search**: If no instant answer, performs a web search
5. **Result Formatting**: Formats and returns the top search results

## Supported Query Patterns

The tool recognizes these patterns:

- "search for [query]"
- "search [query]"
- "look up [query]"
- "find [query]"
- "google [query]"
- "tell me about [query]"
- "what is [query]"
- "who is [query]"
- "wikipedia [query]"

## Example Responses

**Query**: "search for Python tutorials"

**Response**:
```
I found information about 'Python tutorials':

1. Python Tutorial - Learn Python Programming
   This comprehensive Python tutorial covers everything from basics to advanced topics...
   Source: https://example.com/python-tutorial

2. Python Programming Tutorials
   Learn Python programming with step-by-step tutorials and examples...
   Source: https://example.com/python-programming
```

## Integration

The search tool is automatically registered when the platform starts. It's included in the agent's tool registry and can be used alongside other tools like:

- Time tool
- Weather tool
- Joke tool
- Alarm tool
- Help tool

## Configuration

No configuration is required. The tool uses DuckDuckGo's public search API, which doesn't require an API key.

## Limitations

- Search results are limited to top 3 results for brevity
- Instant answers may not be available for all queries
- Requires internet connection
- Rate limiting may apply for excessive use

## Future Enhancements

Potential improvements:

- Search history
- Search result caching
- Custom search engines (Google, Bing)
- Image search support
- Video search support
- Search result filtering

## Troubleshooting

**Issue**: "Internet search is not available"

**Solution**: Install the ddgs library:
```bash
pip install ddgs
```

**Issue**: No search results returned

**Solution**: 
- Check internet connection
- Try rephrasing your search query
- Check logs for errors

## Testing

Test the search tool:

```bash
# Test via API
python3 test_search_api.py

# Test tool directly
python3 test_search_tool.py
```

