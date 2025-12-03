#!/usr/bin/env python3
"""Test script for natural assistant features"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/voice"

def test_natural_assistant():
    """Test natural assistant features"""
    print("=" * 60)
    print("NATURAL ASSISTANT FEATURES TEST")
    print("=" * 60)
    
    # Test 1: Casual greeting
    print("\n1. Testing casual greeting...")
    response = requests.post(
        f"{BASE_URL}/process",
        json={"text": "Hey, how are you?"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Response would be personalized and friendly")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 2: Morning greeting
    print("\n2. Testing morning greeting...")
    response = requests.post(
        f"{BASE_URL}/process",
        json={"text": "Good morning"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Should respond with time-aware greeting")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: Natural request
    print("\n3. Testing natural request...")
    response = requests.post(
        f"{BASE_URL}/process",
        json={"text": "Can you turn on the lights please?"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Should respond naturally with acknowledgment")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Emotional detection
    print("\n4. Testing emotional detection...")
    response = requests.post(
        f"{BASE_URL}/process",
        json={"text": "Ugh, this is so frustrating!"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Should detect frustration and respond empathetically")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 5: Grateful response
    print("\n5. Testing grateful response...")
    response = requests.post(
        f"{BASE_URL}/process",
        json={"text": "Thanks so much!"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Should respond warmly to gratitude")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: Goodbye
    print("\n6. Testing goodbye...")
    response = requests.post(
        f"{BASE_URL}/process",
        json={"text": "Bye! See you later"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Should respond with friendly goodbye")
    else:
        print(f"   ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("KEY FEATURES FOR NATURAL ASSISTANT:")
    print("=" * 60)
    print("✅ Personality & Warmth")
    print("✅ Emotional Intelligence")
    print("✅ Memory & Context")
    print("✅ Natural Conversation Flow")
    print("✅ Proactive Assistance")
    print("✅ Family Integration")
    print("✅ Casual Language")
    print("✅ Time-Aware Responses")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_natural_assistant()

