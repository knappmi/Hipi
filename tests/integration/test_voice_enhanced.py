#!/usr/bin/env python3
"""Test script for enhanced voice features"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/voice/enhanced"

def test_enhanced_voice_features():
    """Test enhanced voice features"""
    print("=" * 60)
    print("ENHANCED VOICE FEATURES TEST")
    print("=" * 60)
    
    # Test 1: List languages
    print("\n1. Testing language support...")
    response = requests.get(f"{BASE_URL}/languages")
    if response.status_code == 200:
        data = response.json()
        print(f"   Current language: {data['current_language']} ({data['current_language_name']})")
        print(f"   Supported languages: {len(data['languages'])}")
        for lang in data['languages'][:5]:  # Show first 5
            print(f"     - {lang['name']} ({lang['code']})")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 2: Change language
    print("\n2. Testing language change...")
    response = requests.post(
        f"{BASE_URL}/languages",
        json={"language_code": "fr"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data['success']}")
        print(f"   New language: {data['language_name']}")
        print(f"   Model available: {data['model_available']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: List trained wake words
    print("\n3. Testing wake word training...")
    response = requests.get(f"{BASE_URL}/wake-words/trained")
    if response.status_code == 200:
        data = response.json()
        print(f"   Trained wake words: {len(data['wake_words'])}")
        if data['wake_words']:
            for word in data['wake_words']:
                print(f"     - {word['wake_word']} ({word['status']})")
        else:
            print("     No trained wake words yet")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Start wake word training
    print("\n4. Testing wake word training start...")
    response = requests.post(
        f"{BASE_URL}/wake-words/train",
        json={"wake_word": "test_wake_word", "description": "Test wake word"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Training started: {data['success']}")
        print(f"   Session ID: {data['session']['id']}")
        print(f"   Samples needed: {data['session']['min_samples']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 5: Voice cloning status
    print("\n5. Testing voice cloning...")
    response = requests.get(f"{BASE_URL}/voice-cloning/voices")
    if response.status_code == 200:
        data = response.json()
        if data.get('enabled'):
            print(f"   ElevenLabs enabled: {data['enabled']}")
            print(f"   Cloned voices: {len(data['voices'])}")
            print(f"   Current voice: {data.get('current_voice', 'None')}")
        else:
            print(f"   ElevenLabs: {data.get('message', 'Not configured')}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: VAD status
    print("\n6. Testing Voice Activity Detection...")
    response = requests.get(f"{BASE_URL}/vad/status")
    if response.status_code == 200:
        data = response.json()
        print(f"   VAD enabled: {data['enabled']}")
        print(f"   Energy threshold: {data['energy_threshold']}")
        print(f"   Silence duration: {data['silence_duration']}s")
    else:
        print(f"   ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_voice_features()

