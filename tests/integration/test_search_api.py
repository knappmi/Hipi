#!/usr/bin/env python3
"""Test search tool via API"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_search_via_api():
    """Test search functionality via API"""
    print("Testing Search Tool via API")
    print("=" * 60)
    
    # Test search command
    test_queries = [
        "search for Python programming",
        "what is artificial intelligence",
        "tell me about raspberry pi",
    ]
    
    for query in test_queries:
        print(f"\nTesting: '{query}'")
        print("-" * 60)
        
        try:
            # Process command via voice API
            response = requests.post(
                f"{BASE_URL}/api/v1/voice/process",
                json={"text": query},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Intent: {result.get('intent', 'unknown')}")
                print(f"Response preview: {str(result)[:300]}...")
            else:
                print(f"Error: Status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    test_search_via_api()

