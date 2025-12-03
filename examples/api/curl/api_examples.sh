#!/bin/bash
# Example API calls using curl

API_BASE_URL="http://localhost:8000/api/v1"

echo "=== Device Control Examples ==="

# List devices
echo "Listing devices..."
curl -s "${API_BASE_URL}/devices" | jq '.'

# Turn on device
echo -e "\nTurning on device..."
curl -s -X POST "${API_BASE_URL}/devices/light_001/control" \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on", "brightness": 50}' | jq '.'

# Set brightness
echo -e "\nSetting brightness..."
curl -s -X POST "${API_BASE_URL}/devices/light_001/control" \
  -H "Content-Type: application/json" \
  -d '{"action": "set_brightness", "brightness": 75}' | jq '.'

echo -e "\n=== Scene Management Examples ==="

# List scenes
echo "Listing scenes..."
curl -s "${API_BASE_URL}/scenes/scenes" | jq '.'

# Activate scene
echo -e "\nActivating scene..."
curl -s -X POST "${API_BASE_URL}/scenes/scenes/1/activate" | jq '.'

echo -e "\n=== Automation Examples ==="

# List automations
echo "Listing automations..."
curl -s "${API_BASE_URL}/automation/automations" | jq '.'

# Create automation
echo -e "\nCreating automation..."
curl -s -X POST "${API_BASE_URL}/automation/automations" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Routine",
    "trigger": {"type": "time", "time": "07:00"},
    "actions": [{"type": "scene", "scene_id": 1}]
  }' | jq '.'

echo -e "\n=== Voice Processing Examples ==="

# Process voice command
echo "Processing voice command..."
curl -s -X POST "${API_BASE_URL}/voice/process" \
  -H "Content-Type: application/json" \
  -d '{"text": "Turn on the lights"}' | jq '.'

echo -e "\nDone!"

