"""Example: Creating Automations with Python"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"

def create_automation(name: str, trigger: dict, actions: list):
    """Create a new automation"""
    automation = {
        "name": name,
        "trigger": trigger,
        "actions": actions,
        "enabled": True
    }
    
    response = requests.post(
        f"{API_BASE_URL}/automation/automations",
        json=automation
    )
    response.raise_for_status()
    return response.json()

def list_automations():
    """List all automations"""
    response = requests.get(f"{API_BASE_URL}/automation/automations")
    response.raise_for_status()
    return response.json()

def enable_automation(automation_id: int):
    """Enable an automation"""
    response = requests.post(
        f"{API_BASE_URL}/automation/automations/{automation_id}/enable"
    )
    response.raise_for_status()
    return response.json()

# Example: Time-based automation
if __name__ == "__main__":
    # Create morning routine automation
    automation = create_automation(
        name="Morning Routine",
        trigger={
            "type": "time",
            "time": "07:00",
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        },
        actions=[
            {
                "type": "scene",
                "scene_id": 1  # Morning scene
            }
        ]
    )
    print(f"Created automation: {automation['name']} (ID: {automation['id']})")
    
    # List all automations
    print("\nAll automations:")
    automations = list_automations()
    for auto in automations:
        print(f"  - {auto['name']} (ID: {auto['id']}, Enabled: {auto.get('enabled', False)})")

