# Audio Troubleshooting Guide

## Current Configuration

The platform is now configured with:
- Audio device passthrough (`/dev/snd`)
- PulseAudio socket mounted
- espeak installed and working
- TTS engine with espeak fallback

## Testing Audio

### 1. Test from Container
```bash
sudo docker compose exec platform espeak "Hello, this is a test"
```

### 2. Test from Web UI
- Go to Voice Settings
- Click "Test TTS" button
- You should hear audio

### 3. Check Audio Output
```bash
# On the Raspberry Pi (host)
pactl list short sinks
# Should show your Bluetooth speaker

# Set Bluetooth as default (if not already)
pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX.1
```

## Common Issues

### No Audio Output

**Problem**: espeak runs but no sound comes out

**Solution 1**: Check if Bluetooth is the default sink
```bash
pactl set-default-sink bluez_output.41_42_90_CD_7B_C1.1
```

**Solution 2**: Test audio on host first
```bash
# On Raspberry Pi
espeak "Test from host"
# If this works, the issue is container audio passthrough
```

**Solution 3**: Use PulseAudio directly in container
```bash
sudo docker compose exec platform bash
# Inside container:
export PULSE_SERVER=unix:/run/user/1000/pulse/native
espeak "Test with PulseAudio"
```

### Permission Errors

If you see permission errors:
```bash
# Check PulseAudio socket permissions
ls -la /run/user/1000/pulse/

# Fix permissions if needed
sudo chmod 755 /run/user/1000/pulse
sudo chmod 644 /run/user/1000/pulse/native
```

### Container Can't Access Audio

**Option 1**: Run container as root (current setup)
- Already configured in docker-compose.yml

**Option 2**: Add user to audio group
```bash
sudo usermod -aG audio $USER
# Then restart Docker
sudo systemctl restart docker
```

## Using OpenAI TTS (Better Quality)

For better quality audio that works reliably:

1. Get OpenAI API key from https://platform.openai.com
2. Go to Voice Settings in web UI
3. Select "OpenAI" as TTS Engine
4. Enter your API key
5. Test - this generates MP3 files and plays them

## Manual Audio Test

```bash
# Enter container
sudo docker compose exec platform bash

# Test espeak
espeak "Hello from container"

# Test with specific audio device
PULSE_SERVER=unix:/run/user/1000/pulse/native espeak "Test"

# List available audio devices
aplay -l
```

## Next Steps

1. **Test the web UI**: Go to Voice Settings and click "Test TTS"
2. **Check logs**: `sudo docker compose logs platform | grep -i "tts\|audio\|speak"`
3. **Verify Bluetooth**: Make sure your Bluetooth speaker is connected and working
4. **Try OpenAI TTS**: For better quality and reliability

## Notes

- **pyttsx3** may not work well in Docker containers
- **espeak** works better but has robotic voice
- **OpenAI TTS** provides best quality but requires internet and API key
- Audio in Docker requires proper device and socket passthrough



