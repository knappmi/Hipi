"""Speech-to-Text engine"""

import logging
import json
from typing import Optional
from pathlib import Path

from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class STTEngine:
    """Speech-to-Text engine interface"""
    
    def __init__(self):
        self.engine_type = settings.stt_engine
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the STT engine"""
        if self.engine_type == "vosk":
            self._init_vosk()
        elif self.engine_type == "openai" and settings.openai_enabled:
            self._init_openai()
        else:
            logger.warning(f"Unknown STT engine: {self.engine_type}")
    
    def _init_vosk(self):
        """Initialize Vosk engine"""
        try:
            import vosk
            import pyaudio
            
            # Download model if not exists (simplified - in production, manage models properly)
            model_path = settings.data_dir / "vosk_models" / "vosk-model-small-en-us-0.15"
            
            if not model_path.exists():
                logger.warning("Vosk model not found. Please download a model.")
                return
            
            self.vosk_model = vosk.Model(str(model_path))
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            
            self.audio = pyaudio.PyAudio()
            
            # Find the best input device (prefer PulseAudio)
            input_device_index = None
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    # Prefer PulseAudio device
                    if 'pulse' in info['name'].lower():
                        input_device_index = i
                        logger.info(f"Using PulseAudio input device: {info['name']} (index {i})")
                        break
                    # Fallback to first available input device
                    elif input_device_index is None:
                        input_device_index = i
                        logger.info(f"Using input device: {info['name']} (index {i})")
            
            if input_device_index is None:
                logger.error("No input device found")
                return
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=4000
            )
            
            self.engine = "vosk"
            logger.info("Vosk STT engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Vosk: {e}", exc_info=True)
    
    def _init_openai(self):
        """Initialize OpenAI STT"""
        try:
            import openai
            
            api_key = settings.openai_api_key
            if not api_key or not api_key.strip():
                logger.warning("OpenAI API key not configured or empty")
                return
            
            # For OpenAI 0.28.1, use the old API style
            openai.api_key = api_key.strip()
            self.openai_client = openai
            self.engine = "openai"
            logger.info("OpenAI STT engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI STT: {e}", exc_info=True)
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data to text"""
        if not self.engine:
            logger.warning("STT engine not initialized")
            return None
        
        if self.engine == "vosk":
            return self._transcribe_vosk(audio_data)
        elif self.engine == "openai":
            return self._transcribe_openai(audio_data)
        
        return None
    
    def _transcribe_vosk(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Vosk"""
        try:
            if self.vosk_rec.AcceptWaveform(audio_data):
                result = json.loads(self.vosk_rec.Result())
                return result.get("text", "")
            else:
                partial = json.loads(self.vosk_rec.PartialResult())
                return partial.get("partial", "")
        except Exception as e:
            logger.error(f"Vosk transcription error: {e}")
            return None
    
    def _transcribe_openai(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using OpenAI"""
        try:
            # Save audio to temp file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # For OpenAI 0.28.1, use the old API style
                with open(tmp_path, "rb") as audio_file:
                    transcript = self.openai_client.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file
                    )
                    return transcript["text"]
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"OpenAI transcription error: {e}")
            return None
    
    def listen_continuous(self, callback):
        """Continuously listen and call callback with transcribed text"""
        if not self.engine:
            logger.warning("STT engine not initialized")
            return
        
        if self.engine == "vosk":
            self._listen_vosk_continuous(callback)
        else:
            # For other engines or when not available, use a polling approach
            logger.warning("Continuous listening not fully implemented for this engine")
            # This would need proper audio streaming implementation
    
    def _listen_vosk_continuous(self, callback):
        """Continuous listening with Vosk"""
        try:
            logger.info("Starting continuous Vosk listening loop...")
            while True:
                try:
                    data = self.stream.read(4000, exception_on_overflow=False)
                    if self.vosk_rec.AcceptWaveform(data):
                        result = json.loads(self.vosk_rec.Result())
                        text = result.get("text", "")
                        if text:
                            logger.info(f"Recognized text: {text}")
                            callback(text)
                    else:
                        # Get partial result for debugging
                        partial = json.loads(self.vosk_rec.PartialResult())
                        partial_text = partial.get("partial", "")
                        if partial_text:
                            logger.debug(f"Partial recognition: {partial_text}")
                except OSError as e:
                    # Handle audio device errors
                    if e.errno == -9999:  # Unanticipated host error
                        logger.warning(f"Audio device error: {e}. Attempting to reopen stream...")
                        try:
                            self.stream.stop_stream()
                            self.stream.close()
                            # Reopen stream
                            self.stream = self.audio.open(
                                format=pyaudio.paInt16,
                                channels=1,
                                rate=16000,
                                input=True,
                                input_device_index=self.stream._input_device_index if hasattr(self.stream, '_input_device_index') else None,
                                frames_per_buffer=4000
                            )
                            logger.info("Stream reopened successfully")
                        except Exception as reopen_error:
                            logger.error(f"Failed to reopen stream: {reopen_error}")
                            break
                    else:
                        logger.error(f"OSError in continuous listening: {e}")
                        break
                except Exception as e:
                    logger.error(f"Error in continuous listening loop: {e}", exc_info=True)
                    import time
                    time.sleep(0.1)  # Brief pause before retrying
        except Exception as e:
            logger.error(f"Continuous listening error: {e}", exc_info=True)
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()

