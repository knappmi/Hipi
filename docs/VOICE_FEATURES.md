# Voice Features

## Multi-Language Support
- **9 Languages**: English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese
- **Dynamic Switching**: Change language via API
- **Model Management**: Automatic model detection for Vosk
- **OpenAI Support**: All languages via OpenAI Whisper

**API**: `GET/POST /api/v1/voice/enhanced/languages`

## Custom Wake Word Training
- Train custom wake words with audio samples
- Minimum 5 samples required
- Session management and progress tracking

**API**: `POST /api/v1/voice/enhanced/wake-words/train`

## Voice Cloning (ElevenLabs)
- Clone voices from audio samples
- Custom TTS voices
- Voice management (list, set, delete)

**API**: `POST /api/v1/voice/enhanced/voice-cloning/clone`

## Voice Activity Detection
- Adaptive threshold (adjusts to noise)
- Silence detection
- Energy level monitoring
- Configurable parameters

**API**: `GET /api/v1/voice/enhanced/vad/status`

## Offline Mode
- Local STT with Vosk models
- Local TTS with pyttsx3
- Model availability checking
- Graceful fallback

See [ENHANCED_VOICE_FEATURES.md](../ENHANCED_VOICE_FEATURES.md) for details.

