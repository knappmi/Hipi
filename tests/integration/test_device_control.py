#!/usr/bin/env python3
"""Test script for device control system"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/devices"

def test_device_control():
    """Test device control API"""
    print("=" * 60)
    print("DEVICE CONTROL SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: List devices
    print("\n1. Listing devices...")
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {data['count']} devices:")
        for device in data['devices']:
            print(f"   - {device['name']} ({device['id']}) - {device['state']}")
    else:
        print(f"   ERROR: {response.status_code}")
        return
    
    # Test 2: Get device info
    print("\n2. Getting device info...")
    response = requests.get(f"{BASE_URL}/living_room_light")
    if response.status_code == 200:
        device = response.json()['device']
        print(f"   Device: {device['name']}")
        print(f"   State: {device['state']}")
        print(f"   Brightness: {device.get('brightness', 'N/A')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: Turn on device
    print("\n3. Turning on living room light...")
    response = requests.post(f"{BASE_URL}/living_room_light/turn_on")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result['success']}")
        print(f"   State: {result['device']['state']}")
        print(f"   Brightness: {result['device'].get('brightness', 'N/A')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    time.sleep(1)
    
    # Test 4: Set brightness
    print("\n4. Setting brightness to 50%...")
    response = requests.post(
        f"{BASE_URL}/living_room_light/control",
        json={"action": "set_brightness", "value": 50}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result['success']}")
        print(f"   Brightness: {result['device'].get('brightness', 'N/A')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    time.sleep(1)
    
    # Test 5: Turn off device
    print("\n5. Turning off living room light...")
    response = requests.post(f"{BASE_URL}/living_room_light/turn_off")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result['success']}")
        print(f"   State: {result['device']['state']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: Check patterns (should have recorded actions)
    print("\n6. Checking recorded patterns...")
    response = requests.get("http://localhost:8000/api/v1/automation/patterns")
    if response.status_code == 200:
        patterns = response.json().get('patterns', [])
        print(f"   Found {len(patterns)} pattern(s)")
        for pattern in patterns[:3]:  # Show first 3
            print(f"   - {pattern['device_id']} -> {pattern['action']} "
                  f"(confidence: {pattern['confidence']:.2%})")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_device_control()

