#!/usr/bin/env python3
"""Test script for media control system"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/media"

def test_media_control():
    """Test media control system"""
    print("=" * 60)
    print("MEDIA CONTROL SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Register media device
    print("\n1. Registering media device...")
    response = requests.post(
        f"{BASE_URL}/devices",
        json={
            "name": "Living Room Speaker",
            "device_type": "speaker",
            "device_id": "speaker_001",
            "capabilities": ["play", "pause", "stop", "volume", "next", "previous"],
            "manufacturer": "Sonos",
            "model": "One"
        }
    )
    if response.status_code == 200:
        data = response.json()
        device_id = data['device']['id']
        print(f"   Device registered: {data['device']['name']} (ID: {device_id})")
    else:
        print(f"   ERROR: {response.status_code}")
        print(response.text)
        return
    
    # Test 2: List devices
    print("\n2. Listing media devices...")
    response = requests.get(f"{BASE_URL}/devices")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['devices'])} device(s)")
        for device in data['devices']:
            print(f"     - {device['name']} ({device['device_type']})")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: Play media
    print("\n3. Playing media...")
    response = requests.post(
        f"{BASE_URL}/play",
        json={
            "device_id": device_id,
            "media": {
                "title": "Test Song",
                "artist": "Test Artist",
                "source": "local",
                "type": "music"
            }
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Set volume
    print("\n4. Setting volume...")
    response = requests.post(
        f"{BASE_URL}/volume",
        json={
            "device_id": device_id,
            "volume": 75
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 5: Pause
    print("\n5. Pausing playback...")
    response = requests.post(f"{BASE_URL}/pause?device_id={device_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: Get session
    print("\n6. Getting playback session...")
    response = requests.get(f"{BASE_URL}/sessions/{device_id}")
    if response.status_code == 200:
        data = response.json()
        session = data['session']
        print(f"   Title: {session['title']}")
        print(f"   Artist: {session['artist']}")
        print(f"   Playing: {session['is_playing']}")
        print(f"   Volume: {session['volume']}%")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 7: Test voice command
    print("\n7. Testing voice command...")
    response = requests.post(
        "http://localhost:8000/api/v1/voice/process",
        json={"text": "play music"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Text: {data.get('text', '')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_media_control()

