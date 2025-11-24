"""Text-to-Speech engine"""

import logging
from typing import Optional
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine interface"""
    
    def __init__(self):
        self.engine_type = settings.tts_engine
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        if self.engine_type == "pyttsx3":
            self._init_pyttsx3()
        elif self.engine_type == "openai" and settings.openai_enabled:
            self._init_openai()
        else:
            logger.warning(f"Unknown TTS engine: {self.engine_type}")
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        try:
            import pyttsx3
            
            self.tts = pyttsx3.init()
            
            # Configure voice properties - try to find the best voice
            voices = self.tts.getProperty('voices')
            if voices:
                # Priority order for better voices
                preferred_voices = [
                    'samantha', 'susan', 'karen', 'fiona',  # macOS voices
                    'female', 'zira', 'hazel',  # Windows voices
                    'english', 'en-us', 'en-gb'  # Generic English
                ]
                
                best_voice = None
                for preferred in preferred_voices:
                    for voice in voices:
                        if preferred.lower() in voice.name.lower():
                            best_voice = voice
                            break
                    if best_voice:
                        break
                
                if best_voice:
                    self.tts.setProperty('voice', best_voice.id)
                    logger.info(f"Selected voice: {best_voice.name}")
                else:
                    # Use first available voice
                    if voices:
                        self.tts.setProperty('voice', voices[0].id)
                        logger.info(f"Using default voice: {voices[0].name}")
            
            # Optimize speech parameters for more natural sound
            self.tts.setProperty('rate', 160)  # Slightly faster for more natural flow
            self.tts.setProperty('volume', 0.95)  # Higher volume
            
            self.engine = "pyttsx3"
            logger.info("pyttsx3 TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
    
    def _init_openai(self):
        """Initialize OpenAI TTS"""
        try:
            import openai
            
            api_key = settings.openai_api_key
            if not api_key or not api_key.strip():
                logger.warning("OpenAI API key not configured or empty")
                return
            
            # For OpenAI 0.28.1, use the old API style
            openai.api_key = api_key.strip()
            self.openai_client = openai
            # Default to a more natural-sounding voice
            # Options: alloy, echo, fable, onyx, nova, shimmer
            self.openai_voice = getattr(settings, 'openai_tts_voice', 'nova')  # 'nova' is more natural
            self.engine = "openai"
            logger.info(f"OpenAI TTS engine initialized with voice: {self.openai_voice}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI TTS: {e}", exc_info=True)
    
    def speak(self, text: str) -> bool:
        """Convert text to speech and speak it"""
        if not self.engine:
            logger.warning("TTS engine not initialized")
            return False
        
        if self.engine == "pyttsx3":
            return self._speak_pyttsx3(text)
        elif self.engine == "openai":
            return self._speak_openai(text)
        
        return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3"""
        try:
            # Set audio driver for pyttsx3
            # Try to use ALSA or PulseAudio
            import os
            # Set PULSE_RUNTIME_PATH if available
            if 'PULSE_RUNTIME_PATH' in os.environ:
                os.environ['PULSE_RUNTIME_PATH'] = os.environ['PULSE_RUNTIME_PATH']
            
            self.tts.say(text)
            self.tts.runAndWait()
            logger.info(f"Spoke text: {text[:50]}...")
            return True
        except Exception as e:
            logger.warning(f"pyttsx3 speech error: {e}")
            # Fallback to espeak via command line (works better in Docker)
            return self._speak_espeak(text)
    
    def _speak_openai(self, text: str) -> bool:
        """Speak using OpenAI TTS"""
        try:
            import tempfile
            import os
            import subprocess
            
            # Use better voice (nova is more natural, shimmer is also good)
            voice = getattr(self, 'openai_voice', 'nova')
            
            # For OpenAI 0.28.1, use the old API style
            response = self.openai_client.Audio.speech(
                model="tts-1",  # Use tts-1-hd for even better quality (costs more)
                voice=voice,
                input=text
            )
            
            # Save to temp file and play
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            try:
                # Try mpg123 first (better for MP3)
                subprocess.run(["mpg123", "-q", tmp_path], check=True, capture_output=True, timeout=30)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                try:
                    # Fallback to ffplay if available
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path], 
                                 check=True, capture_output=True, timeout=30)
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    # Last resort: try aplay (may not work for MP3)
                    try:
                        subprocess.run(["aplay", tmp_path], check=True, capture_output=True, timeout=30)
                    except:
                        logger.warning("No audio player found for MP3 playback")
                        return False
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
            logger.info(f"Spoke text using OpenAI TTS: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            return False
    
    def save_to_file(self, text: str, output_path: str) -> bool:
        """Save speech to audio file"""
        if not self.engine:
            return False
        
        if self.engine == "pyttsx3":
            try:
                self.tts.save_to_file(text, output_path)
                self.tts.runAndWait()
                return True
            except Exception as e:
                logger.error(f"Failed to save TTS to file: {e}")
                return False
        elif self.engine == "openai":
            try:
                # For OpenAI 0.28.1, use the old API style
                response = self.openai_client.Audio.speech(
                    model="tts-1",
                    voice="alloy",
                    input=text
                )
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            except Exception as e:
                logger.error(f"Failed to save OpenAI TTS to file: {e}")
                return False
        
        return False
    
    def _speak_espeak(self, text: str) -> bool:
        """Fallback: Speak using espeak command line (works in Docker)"""
        try:
            import subprocess
            # Use espeak with better parameters for less robotic sound
            # -s: speed (lower = slower, more natural)
            # -p: pitch (50-99, higher = higher pitch)
            # -a: amplitude (0-200, higher = louder)
            # -v: voice (try mb-en1 for better English)
            result = subprocess.run(
                ['espeak', '-s', '160', '-p', '60', '-a', '100', '-v', 'en', text],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"Spoke text using espeak: {text[:50]}...")
                return True
            else:
                logger.warning(f"espeak failed: {result.stderr.decode()}")
                return False
        except FileNotFoundError:
            logger.error("espeak not found. Install with: apt-get install espeak")
            return False
        except Exception as e:
            logger.error(f"espeak error: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'tts'):
            try:
                self.tts.stop()
            except:
                pass

