# Voice Testing Guide

## ✅ System Status: WORKING

All components are functioning:
- ✅ Microphone input detected
- ✅ Speech recognition working (Vosk)
- ✅ Wake word detection working
- ✅ Continuous listening active

## How to Test

### 1. Monitor Logs in Real-Time

```bash
sudo docker compose logs -f platform | grep -E "Recognized|Received voice|Wake word|Acknowledgment"
```

### 2. Say Your Wake Word

**Your wake word is: "HiPi" (sounds like "Hi Pie")**

Try saying:
- **"Hi Pie"** - Should trigger wake word
- **"hipi"** - Should trigger wake word  
- **"Hi Pie turn on the lights"** - Should trigger wake word + process command
- **"huh"** - Will NOT trigger (not the wake word)

### 3. What You Should See in Logs

When you say the wake word correctly:

```
INFO - Recognized text: hi pie turn on the lights
INFO - Received voice input: hi pie turn on the lights
INFO - Wake word detected: HiPi
INFO - Acknowledgment sound played
```

### 4. Current Wake Word

Check current wake word:
```bash
curl -s http://localhost:5000/api/v1/voice/listen/status | python3 -m json.tool
```

Update wake word:
```bash
curl -X POST http://localhost:5000/api/v1/voice/settings \
  -H "Content-Type: application/json" \
  -d '{"wake_word":"HiPi"}'
```

## Troubleshooting

### No Recognition

1. **Check microphone is working**:
   ```bash
   sudo docker compose exec platform python3 /app/test_microphone.py
   ```

2. **Check if listening is active**:
   ```bash
   sudo docker compose logs platform | grep "Starting continuous Vosk listening"
   ```

3. **Verify device**:
   ```bash
   sudo docker compose logs platform | grep "Using.*input device"
   ```
   Should show: `Using PulseAudio input device: pulse (index 7)`

### Wake Word Not Detected

1. **Check current wake word**:
   ```bash
   curl -s http://localhost:5000/api/v1/voice/listen/status | grep wake_word
   ```

2. **Test wake word detection**:
   ```bash
   sudo docker compose exec platform python3 -c "
   from home_assistant_platform.core.voice.wake_word import WakeWordDetector
   d = WakeWordDetector('HiPi')
   print('Test:', d.detect('hi pie'))
   "
   ```

3. **Make sure you're saying it correctly**:
   - Say "Hi Pie" (two words, like "high pie")
   - Or "hipi" (one word)
   - NOT "huh" or other sounds

### No Audio Output

1. **Check TTS is working**:
   ```bash
   curl -X POST http://localhost:5000/api/v1/voice/speak \
     -H "Content-Type: application/json" \
     -d '{"text":"Testing audio output"}'
   ```

2. **Check Bluetooth speakers are connected**:
   ```bash
   bluetoothctl devices
   ```

## Expected Behavior

1. **Say "Hi Pie"** → System detects wake word → Plays beep → Listens for command
2. **Say "Hi Pie turn on the lights"** → System detects wake word → Processes "turn on the lights" → Responds
3. **Say random words** → System recognizes but ignores (no wake word)

## Next Steps

1. Speak clearly into your microphone
2. Say "Hi Pie" followed by a command
3. Watch the logs to see recognition results
4. Adjust microphone sensitivity in system settings if needed



