#!/usr/bin/env python3
"""Test script for calendar and reminder system"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1/calendar"

def test_calendar_reminders():
    """Test calendar and reminder system"""
    print("=" * 60)
    print("CALENDAR & REMINDER SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Create calendar
    print("\n1. Creating calendar...")
    response = requests.post(
        f"{BASE_URL}/calendars",
        json={"name": "Test Calendar", "source_type": "local"}
    )
    if response.status_code == 200:
        data = response.json()
        calendar_id = data['calendar']['id']
        print(f"   Calendar created: {data['calendar']['name']} (ID: {calendar_id})")
    else:
        print(f"   ERROR: {response.status_code}")
        return
    
    # Test 2: Create event
    print("\n2. Creating calendar event...")
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    
    response = requests.post(
        f"{BASE_URL}/events",
        json={
            "calendar_id": calendar_id,
            "title": "Test Meeting",
            "start_time": start_time,
            "end_time": end_time,
            "description": "Test event description"
        }
    )
    if response.status_code == 200:
        data = response.json()
        event_id = data['event']['id']
        print(f"   Event created: {data['event']['title']} (ID: {event_id})")
    else:
        print(f"   ERROR: {response.status_code}")
        print(response.text)
    
    # Test 3: List events
    print("\n3. Listing events...")
    response = requests.get(f"{BASE_URL}/events")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['events'])} event(s)")
        for event in data['events']:
            print(f"     - {event['title']} at {event['start_time']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Create reminder via voice
    print("\n4. Creating reminder via voice command...")
    response = requests.post(
        f"{BASE_URL}/reminders/voice",
        json={"text": "remind me to call mom at 3 PM"}
    )
    if response.status_code == 200:
        data = response.json()
        reminder_id = data['reminder']['id']
        print(f"   Reminder created: {data['reminder']['title']}")
        print(f"   Time: {data['reminder']['reminder_time']}")
    else:
        print(f"   ERROR: {response.status_code}")
        print(response.text)
    
    # Test 5: Create reminder with specific time
    print("\n5. Creating reminder with specific time...")
    reminder_time = (datetime.now() + timedelta(hours=2)).isoformat()
    response = requests.post(
        f"{BASE_URL}/reminders",
        json={
            "title": "Take medication",
            "reminder_time": reminder_time,
            "description": "Daily medication reminder"
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Reminder created: {data['reminder']['title']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: List reminders
    print("\n6. Listing reminders...")
    response = requests.get(f"{BASE_URL}/reminders")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['reminders'])} reminder(s)")
        for reminder in data['reminders']:
            status = "[DONE]" if reminder['completed'] else "[PENDING]"
            print(f"     {status} {reminder['title']} at {reminder['reminder_time']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 7: Get upcoming reminders
    print("\n7. Getting upcoming reminders...")
    response = requests.get(f"{BASE_URL}/reminders/upcoming?hours=24")
    if response.status_code == 200:
        data = response.json()
        print(f"   Upcoming reminders: {len(data['reminders'])}")
        for reminder in data['reminders']:
            print(f"     - {reminder['title']} at {reminder['reminder_time']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 8: Test voice command via voice API
    print("\n8. Testing reminder voice command...")
    response = requests.post(
        "http://localhost:8000/api/v1/voice/process",
        json={"text": "remind me to buy groceries tomorrow at 10 AM"}
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
    test_calendar_reminders()

