# Microphone Input Setup and Verification

## Status: ✅ Working

The container can access the microphone through PulseAudio. The system is now continuously listening for voice input.

## How to Verify Microphone Input

### 1. Check Logs for Listening Activity

```bash
# Watch logs in real-time
sudo docker compose logs -f platform | grep -E "Recognized|Partial|listening"
```

When you speak, you should see:
- `"Recognized text: <your words>"` - when complete phrases are recognized
- `"Partial recognition: <partial words>"` - during speech (if debug logging is enabled)

### 2. Test Microphone Directly

```bash
# Run the test script
sudo docker compose exec platform python3 /app/test_microphone.py
```

This will:
- Detect the PulseAudio input device
- Listen for 5 seconds
- Show "✓ Audio detected!" when it hears sound

### 3. Check Device Detection

```bash
# List available input devices
sudo docker compose exec platform python3 -c "
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f\"Device {i}: {info['name']} - Input channels: {info['maxInputChannels']}\")
p.terminate()
"
```

You should see:
- `Device 7: pulse` - This is the device being used

### 4. Monitor Application Logs

```bash
# Watch all voice-related logs
sudo docker compose logs -f platform | grep -i voice
```

## Current Configuration

- **Input Device**: PulseAudio (device index 7)
- **Sample Rate**: 16000 Hz
- **Channels**: Mono (1 channel)
- **Buffer Size**: 4000 frames
- **STT Engine**: Vosk (local, no API key needed)

## Troubleshooting

### No Audio Detected

1. **Check microphone is connected**:
   ```bash
   arecord -l  # On host
   ```

2. **Verify PulseAudio is running**:
   ```bash
   pulseaudio --check -v
   ```

3. **Check container has access**:
   ```bash
   sudo docker compose exec platform ls -la /run/user/1000/pulse/
   ```

### Continuous Listening Not Working

1. **Check if STT engine initialized**:
   ```bash
   sudo docker compose logs platform | grep "Vosk STT engine initialized"
   ```

2. **Verify listening loop started**:
   ```bash
   sudo docker compose logs platform | grep "Starting continuous Vosk listening loop"
   ```

3. **Check for errors**:
   ```bash
   sudo docker compose logs platform | grep -i error
   ```

### Audio Device Errors

If you see "Unanticipated host error" (-9999):
- The stream will automatically attempt to reopen
- Check logs for "Stream reopened successfully"
- If errors persist, restart the container

## Testing Wake Word

The system is listening for your wake word ("HiPi" by default). When detected:

1. You'll hear an acknowledgment beep
2. The system will process your command
3. Check logs for: `"Wake word detected: HiPi"`

## Next Steps

- Speak clearly into your microphone
- Say your wake word followed by a command (e.g., "Hi Pie turn on the lights")
- Monitor logs to see recognition results
- Adjust microphone sensitivity in your system settings if needed



