#!/usr/bin/env python3
"""Test script for scenes and automation system"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/scenes"

def test_scenes_automation():
    """Test scenes and automation system"""
    print("=" * 60)
    print("SCENES & AUTOMATION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Create movie night scene
    print("\n1. Creating movie night scene...")
    response = requests.post(
        f"{BASE_URL}/scenes",
        json={
            "name": "movie_night",
            "description": "Dim lights for movie watching",
            "icon": "movie",
            "device_states": [
                {"device_id": "living_room_light", "state": "on", "brightness": 20},
                {"device_id": "bedroom_light", "state": "off"},
                {"device_id": "tv", "state": "on"}
            ]
        }
    )
    if response.status_code == 200:
        data = response.json()
        scene_id = data['scene']['id']
        print(f"   Scene created: {data['scene']['name']} (ID: {scene_id})")
    else:
        print(f"   ERROR: {response.status_code}")
        print(response.text)
        return
    
    # Test 2: Create bedtime scene
    print("\n2. Creating bedtime scene...")
    response = requests.post(
        f"{BASE_URL}/scenes",
        json={
            "name": "bedtime",
            "description": "Turn off lights for sleep",
            "icon": "bed",
            "device_states": [
                {"device_id": "living_room_light", "state": "off"},
                {"device_id": "bedroom_light", "state": "on", "brightness": 10},
                {"device_id": "tv", "state": "off"}
            ]
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Scene created: {data['scene']['name']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: List scenes
    print("\n3. Listing scenes...")
    response = requests.get(f"{BASE_URL}/scenes")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['scenes'])} scene(s)")
        for scene in data['scenes']:
            print(f"     - {scene['name']}: {scene['description']} ({scene['device_count']} devices)")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Get scene details
    print("\n4. Getting scene details...")
    response = requests.get(f"{BASE_URL}/scenes/{scene_id}")
    if response.status_code == 200:
        data = response.json()
        scene = data['scene']
        print(f"   Scene: {scene['name']}")
        print(f"   Devices: {len(scene['device_states'])}")
        for device_state in scene['device_states']:
            print(f"     - {device_state['device_id']}: {device_state.get('state', 'N/A')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 5: Activate scene by ID
    print("\n5. Activating scene by ID...")
    response = requests.post(f"{BASE_URL}/scenes/{scene_id}/activate")
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: Activate scene by name
    print("\n6. Activating scene by name...")
    response = requests.post(f"{BASE_URL}/scenes/activate/bedtime")
    if response.status_code == 200:
        data = response.json()
        print(f"   {data['message']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 7: Test voice command
    print("\n7. Testing voice command...")
    response = requests.post(
        "http://localhost:8000/api/v1/voice/process",
        json={"text": "activate movie night"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Intent: {data.get('intent', 'unknown')}")
        print(f"   Text: {data.get('text', '')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 8: Create scene automation
    print("\n8. Creating scene automation...")
    response = requests.post(
        f"{BASE_URL}/automations/scene",
        json={
            "name": "Auto Movie Night",
            "scene_name": "movie_night",
            "trigger_type": "time",
            "trigger_config": {
                "time": "20:00",
                "days": ["friday", "saturday"]
            }
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Automation created: {data['automation']['name']}")
    else:
        print(f"   ERROR: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_scenes_automation()

