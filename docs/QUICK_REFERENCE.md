# Quick Reference Guide

## Voice Commands

### Device Control
- "Turn on the lights"
- "Turn off bedroom light"
- "Set living room light to 50%"
- "Activate movie night scene"
- "Activate bedtime scene"

### Reminders & Calendar
- "Remind me to call mom at 3 PM"
- "Remind me to water plants daily at 8 AM"
- "Remind me to exercise in 30 minutes"
- "List reminders"
- "What reminders do I have?"

### Media Control
- "Play music"
- "Play [song name]"
- "Pause"
- "Stop"
- "Volume up" / "Louder"
- "Volume down" / "Quieter"
- "Volume 50" / "Set volume to 50%"
- "Next track" / "Skip"
- "Previous track" / "Back"

### Natural Conversation
- "Hey, how are you?"
- "Good morning"
- "Good evening"
- "Thanks!"
- "Bye!" / "See you later"

### Energy Monitoring
- "How much energy am I using today"
- "What's my current power consumption"
- "Energy usage this week"
- "Energy cost today"

### User Management
- "Who am I"
- "Switch user to John"
- "I am John"
- "List users"

## API Quick Reference

### Voice
- `POST /api/v1/voice/process` - Process voice command
- `GET /api/v1/voice/enhanced/languages` - List languages
- `POST /api/v1/voice/enhanced/languages` - Change language

### Devices
- `GET /api/v1/devices` - List devices
- `POST /api/v1/devices/{id}/control` - Control device

### Automation
- `GET /api/v1/automation/patterns` - List patterns
- `GET /api/v1/automation/suggestions` - List suggestions
- `POST /api/v1/automation/automations` - Create automation

### Scenes
- `GET /api/v1/scenes/scenes` - List scenes
- `POST /api/v1/scenes/scenes` - Create scene
- `POST /api/v1/scenes/scenes/{id}/activate` - Activate scene

### Calendar & Reminders
- `GET /api/v1/calendar/reminders` - List reminders
- `POST /api/v1/calendar/reminders/voice` - Create reminder via voice
- `GET /api/v1/calendar/events/upcoming` - Get upcoming events

### Media
- `GET /api/v1/media/devices` - List media devices
- `POST /api/v1/media/play` - Play media
- `POST /api/v1/media/pause` - Pause playback
- `POST /api/v1/media/volume` - Set volume

### Users
- `POST /api/v1/users/register` - Register user
- `POST /api/v1/users/login` - Login
- `GET /api/v1/users/me` - Get current user
- `POST /api/v1/users/switch` - Switch user

### Energy
- `POST /api/v1/energy/readings` - Record energy reading
- `GET /api/v1/energy/current` - Get current power
- `GET /api/v1/energy/summary` - Get daily summary
- `GET /api/v1/energy/insights` - Get energy insights

## Configuration

### Quick Setup
```bash
# Start platform
docker compose up -d

# Check status
curl http://localhost:8000/api/v1/status

# Test voice
curl -X POST http://localhost:8000/api/v1/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "What time is it?"}'
```

### Environment Variables
```bash
VOICE_ENABLED=true
WAKE_WORD=hey_assistant
LANGUAGE=en
MQTT_BROKER_HOST=localhost
OPENAI_API_KEY=your_key  # Optional
ELEVENLABS_API_KEY=your_key  # Optional
```

## Common Tasks

### Create a Scene
```bash
curl -X POST http://localhost:8000/api/v1/scenes/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "movie_night",
    "device_states": [
      {"device_id": "light_001", "state": "on", "brightness": 20}
    ]
  }'
```

### Set a Reminder
```bash
curl -X POST http://localhost:8000/api/v1/calendar/reminders/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "remind me to call mom at 3 PM"}'
```

### Register a Device
```bash
curl -X POST http://localhost:8000/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Living Room Light",
    "device_type": "light",
    "capabilities": ["turn_on", "turn_off", "set_brightness"]
  }'
```

### Record Energy Reading
```bash
curl -X POST http://localhost:8000/api/v1/energy/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "light_001",
    "power_watts": 60.5,
    "device_name": "Living Room Light"
  }'
```

