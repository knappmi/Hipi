"""Example: Advanced Automation Script"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"

def execute_automation_script():
    """Execute a Python automation script"""
    script = """
# Advanced automation logic
devices = context.get('devices', [])

# Turn off all lights if it's daytime
if context.get('time_of_day') == 'day':
    for device in devices:
        if device.get('type') == 'light' and device.get('state') == 'on':
            print(f"Turning off {device['name']} during day")
            # In real automation, this would call the device control API
            # turn_off_device(device['id'])
"""

    response = requests.post(
        f"{API_BASE_URL}/automation/scripts/execute",
        json={
            "language": "python",
            "script": script,
            "context": {
                "devices": [
                    {"id": "light_001", "name": "Living Room", "type": "light", "state": "on"},
                    {"id": "light_002", "name": "Bedroom", "type": "light", "state": "on"}
                ],
                "time_of_day": "day"
            }
        }
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    print("Executing advanced automation script...")
    result = execute_automation_script()
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")

