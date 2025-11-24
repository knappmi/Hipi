# Voice Listening and Wake Word Guide

## Current Status

The platform is now configured for continuous voice listening with wake word detection and acknowledgment sounds.

## How It Works

1. **Continuous Listening**: The platform starts listening automatically when voice is enabled
2. **Wake Word Detection**: Say your wake word (default: "hey assistant") to activate
3. **Acknowledgment**: A beep sound plays when wake word is detected
4. **Command Processing**: After wake word, your command is processed

## Testing Wake Word

### Method 1: Via API (Simulate Voice Input)

```bash
# Test wake word detection with acknowledgment
curl -X POST http://192.168.1.81:5000/api/v1/voice/test-wake-word \
  -H "Content-Type: application/json" \
  -d '{"text": "hey assistant turn on the lights"}'
```

You should:
1. See "Wake word detected" in logs
2. Hear an acknowledgment beep
3. See the intent processed

### Method 2: Check Listening Status

```bash
curl http://192.168.1.81:5000/api/v1/voice/listen/status
```

Should return:
```json
{
  "listening": true,
  "enabled": true,
  "awake": false,
  "wake_word": "hey_assistant"
}
```

## Wake Word Format

The wake word uses underscores to separate words:
- `hey_assistant` = "hey assistant"
- `ok_computer` = "ok computer"
- `alexa` = "alexa"

## Acknowledgment Sound

When the wake word is detected:
- A beep sound plays (600Hz, 0.15 seconds)
- The system is ready to process your command
- You can then speak your command

## Continuous Listening

### Current Implementation

The system is set up for continuous listening, but requires:

1. **Vosk Model** (for local STT):
   - Download a Vosk model to `/app/data/vosk_models/`
   - Or use OpenAI STT with API key

2. **Audio Input**:
   - Microphone must be accessible to Docker container
   - Audio devices are already configured

### Enable True Continuous Listening

For actual microphone input, you need to:

1. **Mount microphone device** (add to docker-compose.yml):
   ```yaml
   devices:
     - /dev/snd:/dev/snd
   # Add microphone if separate device
   ```

2. **Download Vosk Model**:
   ```bash
   # Inside container or on host
   mkdir -p /app/data/vosk_models
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip -d /app/data/vosk_models/
   ```

3. **Or Use OpenAI STT**:
   - Set `OPENAI_ENABLED=True` in .env
   - Add `OPENAI_API_KEY=your_key`
   - Set `STT_ENGINE=openai`

## Testing Without Microphone

You can test the wake word system using the API:

```bash
# Simulate saying "hey assistant, what time is it?"
curl -X POST http://192.168.1.81:5000/api/v1/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "hey assistant what time is it"}'
```

This will:
1. Detect wake word
2. Play acknowledgment beep
3. Process the command
4. Return the intent

## Troubleshooting

### No Acknowledgment Sound

1. **Check audio output**:
   ```bash
   sudo docker compose exec platform espeak "test"
   ```

2. **Check Bluetooth connection**:
   ```bash
   pactl list short sinks
   ```

3. **Set default audio sink**:
   ```bash
   pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX.1
   ```

### Wake Word Not Detected

1. **Check wake word setting**:
   ```bash
   curl http://192.168.1.81:5000/api/v1/voice/listen/status
   ```

2. **Test wake word detection**:
   ```bash
   curl -X POST http://192.168.1.81:5000/api/v1/voice/test-wake-word \
     -H "Content-Type: application/json" \
     -d '{"text": "hey assistant"}'
   ```

3. **Check logs**:
   ```bash
   sudo docker compose logs platform | grep -i "wake"
   ```

### Continuous Listening Not Working

This is expected if:
- Vosk model is not downloaded
- Microphone is not accessible
- STT engine is not initialized

The system will still work via API calls for testing.

## Next Steps

1. **For Production**: Download Vosk model or configure OpenAI STT
2. **For Testing**: Use the API endpoints to simulate voice input
3. **For Audio**: Ensure microphone is connected and accessible

## API Endpoints

- `POST /api/v1/voice/process` - Process voice command (simulates voice input)
- `POST /api/v1/voice/test-wake-word` - Test wake word with acknowledgment
- `GET /api/v1/voice/listen/status` - Check listening status
- `POST /api/v1/voice/listen/start` - Start listening
- `POST /api/v1/voice/listen/stop` - Stop listening



