#!/usr/bin/env python3
"""Test script for energy monitoring system"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1/energy"

def test_energy_monitoring():
    """Test energy monitoring system"""
    print("=" * 60)
    print("ENERGY MONITORING SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Record energy readings
    print("\n1. Recording energy readings...")
    devices = [
        {"device_id": "light_001", "power_watts": 60.5, "device_name": "Living Room Light"},
        {"device_id": "tv_001", "power_watts": 120.0, "device_name": "Living Room TV"},
        {"device_id": "ac_001", "power_watts": 1500.0, "device_name": "AC Unit"},
    ]
    
    for device in devices:
        response = requests.post(
            f"{BASE_URL}/readings",
            json=device
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   Recorded: {device['device_name']} = {device['power_watts']}W")
        else:
            print(f"   ERROR: {response.status_code}")
    
    # Test 2: Get current power
    print("\n2. Getting current total power...")
    response = requests.get(f"{BASE_URL}/current")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total power: {data['total_power_watts']:.1f}W ({data['total_power_kilowatts']:.2f}kW)")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 3: Get device readings
    print("\n3. Getting device readings...")
    response = requests.get(f"{BASE_URL}/readings/light_001")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data['readings'])} reading(s) for light_001")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 4: Get daily summary
    print("\n4. Getting daily summary...")
    response = requests.get(f"{BASE_URL}/summary")
    if response.status_code == 200:
        data = response.json()
        summary = data['summary']
        print(f"   Today's energy: {summary['total_kwh']:.2f} kWh")
        print(f"   Today's cost: ${summary['total_cost']:.2f}")
        print(f"   Peak power: {summary['peak_power_watts']:.1f}W")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 5: Create device profile
    print("\n5. Creating device profile...")
    response = requests.post(
        f"{BASE_URL}/profiles",
        json={
            "device_id": "light_001",
            "device_name": "Living Room Light",
            "rated_power_watts": 60,
            "typical_power_watts": 55,
            "standby_power_watts": 0.5,
            "cost_per_kwh": 0.12
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Profile created: {data['profile']['device_name']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 6: Get energy insights
    print("\n6. Getting energy insights...")
    response = requests.get(f"{BASE_URL}/insights?days=7")
    if response.status_code == 200:
        data = response.json()
        insights = data['insights']
        print(f"   7-day total: {insights['total_kwh']:.2f} kWh")
        print(f"   7-day cost: ${insights['total_cost']:.2f}")
        print(f"   Average daily: {insights['average_daily_kwh']:.2f} kWh")
        if insights['top_devices']:
            print(f"   Top device: {insights['top_devices'][0]['device_id']} ({insights['top_devices'][0]['total_kwh']:.2f} kWh)")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 7: Create energy alert
    print("\n7. Creating energy alert...")
    response = requests.post(
        f"{BASE_URL}/alerts",
        json={
            "device_id": "ac_001",
            "alert_type": "high_consumption",
            "threshold_value": 2000.0
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   Alert created: {data['alert']['alert_type']} for {data['alert']['device_id']}")
    else:
        print(f"   ERROR: {response.status_code}")
    
    # Test 8: Test voice command
    print("\n8. Testing voice command...")
    response = requests.post(
        "http://localhost:8000/api/v1/voice/process",
        json={"text": "how much energy am I using today"}
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
    test_energy_monitoring()

