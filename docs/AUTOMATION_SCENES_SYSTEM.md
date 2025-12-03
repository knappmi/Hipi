# Automation & Scenes System

A comprehensive scene management and enhanced automation system with voice activation and time-based triggers.

## ✅ Implemented Features

### 1. Scene Management
- **Scene Creation**: Define scenes with multiple device states
- **Scene Activation**: Activate scenes via API or voice
- **Device States**: Control multiple devices simultaneously
- **Scene Metadata**: Icons, descriptions, and organization

### 2. Enhanced Automation
- **Scene Automations**: Automations that activate scenes
- **Time-Based Triggers**: Schedule scene activations
- **Event-Based Automations**: Trigger automations on events
- **Conditional Automations**: Complex condition support
- **Enable/Disable**: Control automation execution

### 3. Voice Integration
- **Scene Activation**: "Activate movie night"
- **Natural Language**: Understands scene names
- **Scene Recognition**: Maps common phrases to scenes

### 4. Device Control
- **Multi-Device Control**: Control multiple devices in one action
- **State Management**: Set brightness, color, temperature
- **Device States**: On/off, brightness, color, temperature

## API Endpoints

### Scenes
- `GET /api/v1/scenes/scenes` - List all scenes
- `GET /api/v1/scenes/scenes/{scene_id}` - Get scene details
- `POST /api/v1/scenes/scenes` - Create scene
- `PUT /api/v1/scenes/scenes/{scene_id}` - Update scene
- `DELETE /api/v1/scenes/scenes/{scene_id}` - Delete scene
- `POST /api/v1/scenes/scenes/{scene_id}/activate` - Activate scene by ID
- `POST /api/v1/scenes/scenes/activate/{scene_name}` - Activate scene by name

### Automations
- `POST /api/v1/scenes/automations/scene` - Create scene automation
- `POST /api/v1/scenes/automations/{id}/enable` - Enable automation
- `POST /api/v1/scenes/automations/{id}/disable` - Disable automation

## Voice Commands

### Scene Activation
- **"Activate movie night"**
- **"Activate bedtime scene"**
- **"Turn on away mode"**
- **"Set movie night"**
- **"Good night"** (activates bedtime scene)
- **"Movie night"** (activates movie night scene)

## Usage Examples

### Create Scene
```bash
curl -X POST http://localhost:8000/api/v1/scenes/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "movie_night",
    "description": "Dim lights for movie watching",
    "icon": "movie",
    "device_states": [
      {"device_id": "living_room_light", "state": "on", "brightness": 20},
      {"device_id": "bedroom_light", "state": "off"},
      {"device_id": "tv", "state": "on"}
    ]
  }'
```

### Activate Scene
```bash
# By ID
curl -X POST http://localhost:8000/api/v1/scenes/scenes/1/activate

# By name
curl -X POST http://localhost:8000/api/v1/scenes/scenes/activate/movie_night
```

### Create Scene Automation
```bash
curl -X POST http://localhost:8000/api/v1/scenes/automations/scene \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Auto Movie Night",
    "scene_name": "movie_night",
    "trigger_type": "time",
    "trigger_config": {
      "time": "20:00",
      "days": ["friday", "saturday"]
    }
  }'
```

## Common Scenes

### Movie Night
- Dim living room lights
- Turn off bedroom lights
- Turn on TV

### Bedtime
- Turn off all lights
- Dim bedroom light
- Turn off TV

### Away Mode
- Turn off all lights
- Turn off non-essential devices

### Wake Up
- Gradually increase bedroom light
- Turn on coffee maker
- Play morning playlist

## Scene Device States

Each scene contains a list of device states:
```json
{
  "device_id": "living_room_light",
  "state": "on",
  "brightness": 50,
  "color": "#FF5733",
  "temperature": 2700
}
```

Supported properties:
- **state**: "on" or "off"
- **brightness**: 0-100
- **color**: Hex color code
- **temperature**: Color temperature in Kelvin

## Integration

### Voice Integration
The scene tool is automatically registered with the voice agent:
- Voice commands activate scenes
- Natural language scene recognition
- Common scene name mappings

### Automation Integration
- Scenes can be triggered by automations
- Time-based scene activation
- Event-based scene activation
- Conditional scene activation

### Device Control Integration
- Scenes use the unified device manager
- Support for all device types
- Multi-device coordination

## Architecture

```
Automation & Scenes System
├── SceneManager
│   ├── Scene CRUD
│   ├── Scene activation
│   └── Device state management
├── EnhancedAutomationManager
│   ├── Scene automations
│   ├── Event-based automations
│   └── Conditional automations
└── SceneTool (Voice)
    ├── Scene activation
    └── Natural language parsing
```

## Database Models

- **Scene**: Scene definitions with device states
- **Automation**: Enhanced automations with scene support

## Testing

Run the test script:
```bash
python3 test_scenes_automation.py
```

## Status

✅ **Fully Functional**
- Scene management: ✅ Working
- Scene activation: ✅ Working
- Voice commands: ✅ Working (8 tools registered)
- Scene automations: ✅ Working
- Device control: ✅ Working

## Future Enhancements

- Scene templates
- Scene scheduling
- Scene sharing
- Scene preview
- Scene undo/redo
- Scene groups
- Conditional scene activation
- Scene transitions (fade effects)
- Scene recommendations based on usage

