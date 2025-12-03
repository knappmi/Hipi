"""Voice cloning support - ElevenLabs and other services"""

import logging
from typing import Optional, Dict, Any
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class VoiceCloningManager:
    """Manage voice cloning for custom TTS voices"""
    
    def __init__(self):
        self.elevenlabs_api_key: Optional[str] = None
        self.cloned_voices: Dict[str, Dict[str, Any]] = {}
        self.current_voice_id: Optional[str] = None
    
    def configure_elevenlabs(self, api_key: str):
        """Configure ElevenLabs API"""
        self.elevenlabs_api_key = api_key
        logger.info("ElevenLabs API configured")
    
    async def clone_voice(self, voice_name: str, audio_samples: list, description: Optional[str] = None) -> Optional[str]:
        """Clone a voice from audio samples"""
        if not self.elevenlabs_api_key:
            logger.error("ElevenLabs API key not configured")
            return None
        
        try:
            import requests
            
            # ElevenLabs API endpoint
            url = "https://api.elevenlabs.io/v1/voices/add"
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Prepare form data
            files = []
            for i, audio_data in enumerate(audio_samples):
                files.append(("files", (f"sample_{i}.wav", audio_data, "audio/wav")))
            
            data = {
                "name": voice_name,
                "description": description or f"Cloned voice: {voice_name}"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                voice_data = response.json()
                voice_id = voice_data.get("voice_id")
                
                self.cloned_voices[voice_id] = {
                    "id": voice_id,
                    "name": voice_name,
                    "description": description,
                    "created_at": voice_data.get("created_at")
                }
                
                logger.info(f"Voice cloned successfully: {voice_name} (ID: {voice_id})")
                return voice_id
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except ImportError:
            logger.error("requests library required for ElevenLabs integration")
            return None
        except Exception as e:
            logger.error(f"Error cloning voice: {e}", exc_info=True)
            return None
    
    async def synthesize_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Synthesize speech using cloned voice"""
        if not self.elevenlabs_api_key:
            logger.error("ElevenLabs API key not configured")
            return None
        
        voice_id = voice_id or self.current_voice_id
        if not voice_id:
            logger.error("No voice ID specified")
            return None
        
        try:
            import requests
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # or "eleven_monolingual_v1"
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"ElevenLabs synthesis error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}", exc_info=True)
            return None
    
    def list_cloned_voices(self) -> list:
        """List all cloned voices"""
        return list(self.cloned_voices.values())
    
    def set_current_voice(self, voice_id: str) -> bool:
        """Set the current voice to use"""
        if voice_id in self.cloned_voices:
            self.current_voice_id = voice_id
            logger.info(f"Current voice set to: {self.cloned_voices[voice_id]['name']}")
            return True
        return False
    
    def delete_voice(self, voice_id: str) -> bool:
        """Delete a cloned voice"""
        if not self.elevenlabs_api_key:
            return False
        
        try:
            import requests
            
            url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
            headers = {"xi-api-key": self.elevenlabs_api_key}
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                if voice_id in self.cloned_voices:
                    del self.cloned_voices[voice_id]
                if self.current_voice_id == voice_id:
                    self.current_voice_id = None
                logger.info(f"Voice deleted: {voice_id}")
                return True
            else:
                logger.error(f"Error deleting voice: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting voice: {e}")
            return False

