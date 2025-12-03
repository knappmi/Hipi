"""Example: Scene Management with Python"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"

def create_scene(name: str, device_states: list, description: str = None):
    """Create a new scene"""
    scene = {
        "name": name,
        "device_states": device_states,
        "description": description
    }
    
    response = requests.post(
        f"{API_BASE_URL}/scenes/scenes",
        json=scene
    )
    response.raise_for_status()
    return response.json()

def list_scenes():
    """List all scenes"""
    response = requests.get(f"{API_BASE_URL}/scenes/scenes")
    response.raise_for_status()
    return response.json()

def activate_scene(scene_id: int):
    """Activate a scene"""
    response = requests.post(
        f"{API_BASE_URL}/scenes/scenes/{scene_id}/activate"
    )
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    # Create movie night scene
    scene = create_scene(
        name="Movie Night",
        description="Dim lights for movie watching",
        device_states=[
            {"device_id": "light_living_room", "state": "on", "brightness": 20},
            {"device_id": "light_kitchen", "state": "off"},
            {"device_id": "light_bedroom", "state": "off"}
        ]
    )
    print(f"Created scene: {scene['name']} (ID: {scene['id']})")
    
    # List all scenes
    print("\nAll scenes:")
    scenes = list_scenes()
    for scene in scenes:
        print(f"  - {scene['name']} (ID: {scene['id']})")
    
    # Activate scene
    if scenes:
        scene_id = scenes[0]['id']
        print(f"\nActivating scene {scene_id}...")
        activate_scene(scene_id)
        print("Scene activated!")

