"""Example: Device Control with Python"""

import requests

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def list_devices():
    """List all devices"""
    response = requests.get(f"{API_BASE_URL}/devices")
    response.raise_for_status()
    return response.json()

def get_device(device_id: str):
    """Get device details"""
    response = requests.get(f"{API_BASE_URL}/devices/{device_id}")
    response.raise_for_status()
    return response.json()

def turn_on_device(device_id: str, brightness: int = None):
    """Turn on a device"""
    data = {"action": "turn_on"}
    if brightness is not None:
        data["brightness"] = brightness
    
    response = requests.post(
        f"{API_BASE_URL}/devices/{device_id}/control",
        json=data
    )
    response.raise_for_status()
    return response.json()

def turn_off_device(device_id: str):
    """Turn off a device"""
    response = requests.post(
        f"{API_BASE_URL}/devices/{device_id}/control",
        json={"action": "turn_off"}
    )
    response.raise_for_status()
    return response.json()

def set_brightness(device_id: str, brightness: int):
    """Set device brightness"""
    response = requests.post(
        f"{API_BASE_URL}/devices/{device_id}/control",
        json={"action": "set_brightness", "brightness": brightness}
    )
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    # List all devices
    print("Listing devices...")
    devices = list_devices()
    for device in devices:
        print(f"  - {device['name']} ({device['id']})")
    
    # Turn on a device
    if devices:
        device_id = devices[0]['id']
        print(f"\nTurning on {device_id}...")
        turn_on_device(device_id, brightness=50)
        
        # Set brightness
        print(f"Setting brightness to 75%...")
        set_brightness(device_id, 75)
        
        # Turn off
        print(f"Turning off...")
        turn_off_device(device_id)

