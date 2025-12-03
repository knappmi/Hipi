# Audio Setup for Bluetooth Speakers

## Configuration Applied

The platform has been configured to access audio devices through Docker. Here's what was set up:

### Docker Configuration

1. **Audio Device Passthrough**: `/dev/snd` is mounted into the container
2. **PulseAudio Socket**: PulseAudio socket is mounted for Bluetooth audio
3. **User Permissions**: Container runs with audio group access

### Testing Audio

1. **Restart the platform:**
   ```bash
   sudo docker compose down
   sudo docker compose up -d
   ```

2. **Test from web UI:**
   - Go to Voice Settings page
   - Click "Test TTS" button
   - You should hear audio through your Bluetooth speakers

3. **Test from command line:**
   ```bash
   # Test espeak directly
   sudo docker compose exec platform espeak "Hello, this is a test"
   
   # Check audio devices in container
   sudo docker compose exec platform aplay -l
   ```

### Troubleshooting

#### No Audio Output

1. **Check if Bluetooth is connected:**
   ```bash
   pactl list short sinks
   # Should show: bluez_output.XX_XX_XX_XX_XX_XX.1
   ```

2. **Set Bluetooth as default sink:**
   ```bash
   pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX.1
   ```

3. **Test audio on host:**
   ```bash
   espeak "Test"
   # or
   aplay /usr/share/sounds/alsa/Front_Left.wav
   ```

4. **Check container logs:**
   ```bash
   sudo docker compose logs platform | grep -i "audio\|tts\|speak"
   ```

5. **Check PulseAudio in container:**
   ```bash
   sudo docker compose exec platform ls -la /run/user/1000/pulse/
   ```

#### Permission Issues

If you get permission errors:

```bash
# Add your user to audio group (if not already)
sudo usermod -aG audio $USER

# Check audio group ID
getent group audio

# Restart Docker service
sudo systemctl restart docker
```

#### PulseAudio Socket Not Found

If PulseAudio socket doesn't exist:

```bash
# Check if PulseAudio is running
systemctl --user status pulseaudio

# Start PulseAudio if needed
systemctl --user start pulseaudio

# Check socket location
ls -la /run/user/1000/pulse/
```

### Alternative: Use ALSA Directly

If PulseAudio doesn't work, you can configure the container to use ALSA directly:

1. **Update docker-compose.yml** to remove PulseAudio mounts
2. **Use espeak with ALSA:**
   ```bash
   espeak -a 200 -s 150 "Hello"
   ```

### Using OpenAI TTS (Better Quality)

For better quality audio, use OpenAI TTS:

1. Get an OpenAI API key
2. Go to Voice Settings in web UI
3. Select "OpenAI" as TTS Engine
4. Enter your API key
5. Test - this will generate MP3 files and play them

### Manual Audio Test in Container

```bash
# Enter container
sudo docker compose exec platform bash

# Test espeak
espeak "Hello from container"

# List audio devices
aplay -l

# Test with aplay (if you have a WAV file)
aplay /path/to/test.wav
```

## Notes

- **pyttsx3** may not work well in Docker containers
- **espeak** works better as it uses command-line interface
- **OpenAI TTS** provides best quality but requires internet and API key
- Bluetooth audio requires PulseAudio/PipeWire to be running on the host



