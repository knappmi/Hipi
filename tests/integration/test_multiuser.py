#!/usr/bin/env python3
"""Test script for multi-user system"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/users"

def test_multiuser():
    """Test multi-user system"""
    print("=" * 60)
    print("MULTI-USER SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: List users
    print("\n1. Listing users...")
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['users'])} user(s)")
        for user in data['users']:
            print(f"     - {user['display_name']} ({user['username']})")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 2: Register new user
    print("\n2. Registering new user...")
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": "alice",
            "password": "password123",
            "display_name": "Alice Smith",
            "email": "alice@example.com"
        }
    )
    if response.status_code == 200:
        data = response.json()
        user_id = data['user']['id']
        print(f"   User registered: {data['user']['display_name']} (ID: {user_id})")
    else:
        print(f"   ERROR: {response.status_code}")
        print(response.text)
    
    # Test 3: Login
    print("\n3. Logging in...")
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": "alice",
            "password": "password123"
        }
    )
    if response.status_code == 200:
        data = response.json()
        session_token = data['session_token']
        print(f"   Logged in as: {data['user']['display_name']}")
        print(f"   Session token: {session_token[:20]}...")
    else:
        print(f"   ERROR: {response.status_code}")
        session_token = None
    
    # Test 4: Get current user
    print("\n4. Getting current user...")
    headers = {}
    if session_token:
        headers["X-Session-Token"] = session_token
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    if response.status_code == 200:
        data = response.json()
        user = data['user']
        print(f"   Current user: {user['display_name']} ({user['username']})")
        print(f"   Preferences: {user.get('preferences', {})}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 5: Switch user
    print("\n5. Switching user...")
    response = requests.post(f"{BASE_URL}/switch?user_id=1")
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: Update preferences
    print("\n6. Updating preferences...")
    headers = {}
    if session_token:
        headers["X-Session-Token"] = session_token
    response = requests.put(
        f"{BASE_URL}/preferences",
        json={
            "preferences": {
                "language": "en",
                "timezone": "America/New_York",
                "voice_enabled": True
            }
        },
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 7: Test voice command
    print("\n7. Testing voice command...")
    response = requests.post(
        "http://localhost:8000/api/v1/voice/process",
        json={"text": "who am I"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Text: {data.get('text', '')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 8: List users again
    print("\n8. Listing users again...")
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['users'])} user(s)")
        for user in data['users']:
            print(f"     - {user['display_name']} ({user['username']})")
    else:
        print(f"   ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_multiuser()

