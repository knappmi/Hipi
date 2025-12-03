#!/usr/bin/env python3
"""Test script for the search tool"""

import sys
sys.path.insert(0, '/home/knappmi14/Documents')

from home_assistant_platform.core.voice.tools.search_tool import SearchTool

def test_search_tool():
    """Test the search tool"""
    print("Testing Search Tool")
    print("=" * 60)
    
    tool = SearchTool()
    
    print(f"Tool name: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Capabilities: {tool.capabilities}")
    print()
    
    # Test can_handle
    test_cases = [
        ("search", "search for Python tutorials", []),
        ("search", "what is artificial intelligence", []),
        ("search", "look up the weather", []),
        ("search", "tell me about raspberry pi", []),
        ("unknown", "turn on the lights", []),
    ]
    
    print("Testing can_handle:")
    print("-" * 60)
    for intent, text, entities in test_cases:
        can_handle = tool.can_handle(intent, text, entities)
        status = "[PASS]" if can_handle == (intent == "search") else "[FAIL]"
        print(f"{status} Intent: {intent}, Text: '{text}' -> {can_handle}")
    print()
    
    # Test query extraction
    print("Testing query extraction:")
    print("-" * 60)
    test_queries = [
        "search for Python tutorials",
        "what is artificial intelligence",
        "look up the weather",
        "tell me about raspberry pi",
        "who is Albert Einstein",
    ]
    
    for query in test_queries:
        extracted = tool._extract_query(query)
        print(f"  '{query}' -> '{extracted}'")
    print()
    
    # Test actual search (if library is available)
    print("Testing actual search:")
    print("-" * 60)
    try:
        result = tool.execute("search", "search for Python programming", [])
        if result:
            print("[SUCCESS] Search executed!")
            print(f"Result preview: {result[:200]}...")
        else:
            print("[INFO] Search returned no result")
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        print("Note: Install duckduckgo-search: pip install duckduckgo-search")
    
    print()
    print("=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    test_search_tool()

