"""Example: IFTTT Webhook Integration"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"
IFTTT_WEBHOOK_URL = "https://maker.ifttt.com/trigger/home_event/with/key/YOUR_IFTTT_KEY"

def create_ifttt_webhook():
    """Create IFTTT webhook"""
    webhook = {
        "name": "IFTTT Integration",
        "url": IFTTT_WEBHOOK_URL,
        "method": "POST",
        "trigger_on_device_change": True,
        "trigger_on_scene_activate": True,
        "trigger_on_automation_run": True,
        "payload_template": """{
            "value1": "{{ event_type }}",
            "value2": "{{ event_data.device_id or event_data.scene_id or 'automation' }}",
            "value3": "{{ event_data.state or event_data.name or 'executed' }}"
        }""",
        "enabled": True
    }
    
    response = requests.post(
        f"{API_BASE_URL}/webhooks",
        json=webhook
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    print("Creating IFTTT webhook...")
    result = create_ifttt_webhook()
    print(f"✓ Created webhook: {result['name']} (ID: {result['id']})")
    print("\nThis webhook will trigger IFTTT when:")
    print("  - Any device changes")
    print("  - A scene is activated")
    print("  - An automation runs")

