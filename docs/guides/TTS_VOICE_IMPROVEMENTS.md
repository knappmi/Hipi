# TTS Voice Quality Improvements

## Overview

The TTS system has been improved to provide less robotic, more natural-sounding voices.

## Voice Options

### 1. OpenAI TTS (Best Quality - Recommended)

**Requires**: OpenAI API key

**Available Voices**:
- **Nova** (Default) - Natural-sounding female voice ⭐ Recommended
- **Shimmer** - Natural female voice
- **Alloy** - Neutral voice
- **Echo** - Male voice
- **Fable** - British male voice
- **Onyx** - Deep male voice

**How to Use**:
1. Go to Voice Settings in web UI
2. Select "OpenAI" as TTS Engine
3. Enter your OpenAI API key
4. Select your preferred voice (Nova recommended)
5. Click "Update"

**Cost**: ~$0.015 per 1000 characters (very affordable)

### 2. pyttsx3 (Local - Improved)

**No API key needed** - Works offline

**Improvements**:
- Better voice selection (prefers natural-sounding voices)
- Optimized speech rate (160 WPM for natural flow)
- Higher volume (95%)
- Automatic voice selection (prefers female voices like Samantha, Susan, Karen)

**Current Status**: Uses best available system voice

### 3. espeak (Fallback - Improved)

**No API key needed** - Works offline

**Improvements**:
- Better parameters for less robotic sound
- Optimized pitch and speed
- Uses English voice variant

**Note**: Still somewhat robotic, but improved

## Quick Setup for Best Quality

### Option 1: OpenAI TTS (Recommended)

1. Get API key from https://platform.openai.com
2. In Voice Settings:
   - TTS Engine: **OpenAI**
   - OpenAI API Key: **[your key]**
   - OpenAI Voice: **Nova**
3. Test with "Test Voice" button

### Option 2: Improve Local Voice

The system will automatically:
- Select the best available voice
- Optimize speech parameters
- Use improved espeak settings as fallback

## Voice Comparison

| Engine | Quality | Cost | Setup |
|--------|---------|------|-------|
| OpenAI TTS | ⭐⭐⭐⭐⭐ Excellent | $0.015/1K chars | API key needed |
| pyttsx3 | ⭐⭐⭐ Good | Free | Automatic |
| espeak | ⭐⭐ Fair | Free | Automatic |

## Testing

```bash
# Test current TTS
curl -X POST http://localhost:5000/api/v1/voice/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, this is a test of the voice quality"}'
```

## Tips for Best Results

1. **Use OpenAI TTS** for production - best quality
2. **Nova voice** sounds most natural
3. **Keep sentences short** for better clarity
4. **Test different voices** to find your preference

## Future Enhancements

- Piper TTS (neural, local, high quality)
- Coqui TTS (open-source neural TTS)
- Voice cloning
- Custom voice training



