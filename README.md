# Home Assistant Platform

A comprehensive, AI-powered home automation platform with voice control, predictive automation, and natural conversation capabilities. Built to compete with Alexa and Google Home.

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker compose up -d
```

The platform will be available at:
- **API**: http://localhost:8000
- **Web UI**: http://localhost:5000
- **API Docs**: http://localhost:8000/docs

### Local Development
```bash
poetry install
poetry run uvicorn home_assistant_platform.core.main:app --reload
```

## ✨ Features

### Core Capabilities
- **Voice Control**: Natural language voice commands with wake word detection
- **Predictive Automation**: Learns patterns and suggests automations
- **Device Control**: MQTT, WiFi devices (TP-Link Kasa, Philips Hue)
- **Scenes & Automation**: Create and activate device scenes
- **Calendar & Reminders**: Voice-controlled reminders and calendar management
- **Media Control**: Playback control for music and video
- **Multi-User Support**: User authentication with voice recognition
- **Energy Monitoring**: Track energy consumption and costs
- **Natural Conversation**: Personality, emotional intelligence, memory

### Voice Features
- **Multi-Language Support**: 9 languages (English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese)
- **Custom Wake Words**: Train custom wake words
- **Voice Cloning**: ElevenLabs integration for personalized voices
- **Enhanced VAD**: Improved voice activity detection
- **Offline Mode**: Local STT/TTS with Vosk and pyttsx3

### Natural Assistant
- **Personality Engine**: Warm, friendly, casual responses
- **Emotional Intelligence**: Recognizes and responds to emotions
- **Memory System**: Remembers names, preferences, family members
- **Proactive Assistance**: Offers help before asked
- **Family Integration**: Understands family relationships

## 📋 Available Tools (12 Total)

1. **Time** - Get current time and date
2. **Joke** - Tell jokes
3. **Weather** - Get weather information
4. **Alarm** - Set and manage alarms
5. **Search** - Internet search (DuckDuckGo)
6. **Reminder** - Set reminders via voice
7. **Scene** - Activate device scenes
8. **Media** - Control media playback
9. **User** - User management and switching
10. **Energy** - Energy consumption queries
11. **Chat** - Casual conversation
12. **Help** - List available capabilities

## 🎯 Voice Commands Examples

### Device Control
- "Turn on the lights"
- "Activate movie night scene"
- "Set bedroom light to 50%"

### Reminders & Calendar
- "Remind me to call mom at 3 PM"
- "Remind me to water plants daily at 8 AM"
- "What reminders do I have?"

### Media Control
- "Play music"
- "Pause"
- "Volume up"
- "Next track"

### Natural Conversation
- "Hey, how are you?"
- "Good morning"
- "Thanks!"
- "Bye!"

### Energy Monitoring
- "How much energy am I using today?"
- "What's my current power consumption?"
- "Energy usage this week"

### User Management
- "Who am I?"
- "Switch user to John"
- "I am John"

## 📡 API Endpoints

### Core APIs
- `/api/v1/voice/*` - Voice processing
- `/api/v1/devices/*` - Device management
- `/api/v1/automation/*` - Automation system
- `/api/v1/scenes/*` - Scene management
- `/api/v1/calendar/*` - Calendar and reminders
- `/api/v1/media/*` - Media control
- `/api/v1/users/*` - User management
- `/api/v1/energy/*` - Energy monitoring

### Enhanced Features
- `/api/v1/voice/enhanced/*` - Enhanced voice features
  - Languages, wake words, voice cloning, VAD

## 🏗️ Architecture

```
Home Assistant Platform
├── Voice System
│   ├── STT Engine (Vosk/OpenAI)
│   ├── TTS Engine (pyttsx3/OpenAI)
│   ├── Wake Word Detection
│   ├── Intent Processing
│   └── Natural Agent (Personality, Memory, Emotional Intelligence)
├── Device Control
│   ├── Unified Device Manager
│   ├── MQTT Integration
│   └── WiFi Discovery (TP-Link, Hue)
├── Automation System
│   ├── Pattern Learning
│   ├── Suggestion Engine
│   ├── Automation Executor
│   └── Automation Scheduler
├── Calendar & Reminders
│   ├── Calendar Manager
│   ├── Reminder Manager
│   └── Reminder Scheduler
├── Scenes & Automation
│   ├── Scene Manager
│   └── Enhanced Automation
├── Media Control
│   ├── Media Device Manager
│   ├── Spotify Integration
│   └── YouTube Integration
├── Multi-User System
│   ├── User Manager
│   ├── Voice Recognition
│   └── Session Management
└── Energy Monitoring
    ├── Energy Monitor
    ├── Device Profiles
    └── Energy Analytics
```

## 🔧 Configuration

### Environment Variables

```bash
# Voice
VOICE_ENABLED=true
WAKE_WORD=hey_assistant
CONVERSATION_MODE=false
STT_ENGINE=vosk  # vosk or openai
TTS_ENGINE=pyttsx3  # pyttsx3 or openai

# OpenAI (optional)
OPENAI_API_KEY=your_key_here
OPENAI_ENABLED=false

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_ENABLED=false

# Language
LANGUAGE=en

# Voice Activity Detection
VAD_ENABLED=true
VAD_ENERGY_THRESHOLD=0.01
VAD_SILENCE_DURATION=0.5
```

## 📚 Documentation

- **[Voice Features](docs/VOICE_FEATURES.md)** - Multi-language, wake words, voice cloning
- **[Automation System](docs/AUTOMATION.md)** - Predictive automation and pattern learning
- **[Device Control](docs/DEVICES.md)** - MQTT, WiFi device integration
- **[Calendar & Reminders](docs/CALENDAR.md)** - Reminder system and calendar management
- **[Scenes & Automation](docs/SCENES.md)** - Scene management and automation
- **[Media Control](docs/MEDIA.md)** - Media playback and platform integration
- **[Multi-User System](docs/USERS.md)** - User management and voice recognition
- **[Energy Monitoring](docs/ENERGY.md)** - Energy tracking and analytics
- **[Natural Assistant](docs/NATURAL_ASSISTANT.md)** - Personality, memory, emotional intelligence

## 🧪 Testing

```bash
# Test API
curl http://localhost:8000/api/v1/status

# Test voice processing
curl -X POST http://localhost:8000/api/v1/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "What time is it?"}'

# Test device control
curl http://localhost:8000/api/v1/devices

# Test reminders
curl -X POST http://localhost:8000/api/v1/calendar/reminders/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "remind me to call mom at 3 PM"}'
```

## 🛠️ Development

### Project Structure
```
home_assistant_platform/
├── core/
│   ├── voice/          # Voice processing
│   ├── automation/     # Automation system
│   ├── devices/        # Device control
│   ├── calendar/       # Calendar & reminders
│   ├── media/          # Media control
│   ├── users/          # Multi-user system
│   ├── energy/         # Energy monitoring
│   ├── personality/    # Natural assistant features
│   └── api/            # API endpoints
├── config/             # Configuration
└── data/               # Data storage
```

### Adding New Features

1. Create tool in `core/voice/tools/`
2. Register tool in `main.py`
3. Add intent patterns in `intent_processor.py`
4. Create API endpoints in `core/api/`
5. Update documentation

## 📊 Status

✅ **All Major Features Implemented**
- Voice control with 12 tools
- Predictive automation
- Device control (MQTT, WiFi)
- Calendar & reminders
- Scenes & automation
- Media control
- Multi-user support
- Energy monitoring
- Natural conversation features

## 🤝 Contributing

This is a comprehensive home automation platform. All features are implemented and tested.

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

Built with FastAPI, Flask, Vosk, OpenAI, and many other open-source technologies.
