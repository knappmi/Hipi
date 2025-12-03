"""Language management for multi-language support"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class LanguageManager:
    """Manages language settings and models"""
    
    # Supported languages with their codes and models
    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "stt_models": {
                "vosk": "vosk-model-small-en-us-0.15",
                "openai": "whisper-1"  # OpenAI supports all languages
            },
            "tts_voices": {
                "pyttsx3": ["english", "en-us", "en-gb"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "es": {
            "name": "Spanish",
            "stt_models": {
                "vosk": "vosk-model-small-es-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["spanish", "es"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "fr": {
            "name": "French",
            "stt_models": {
                "vosk": "vosk-model-small-fr-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["french", "fr"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "de": {
            "name": "German",
            "stt_models": {
                "vosk": "vosk-model-small-de-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["german", "de"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "it": {
            "name": "Italian",
            "stt_models": {
                "vosk": "vosk-model-small-it-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["italian", "it"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "pt": {
            "name": "Portuguese",
            "stt_models": {
                "vosk": "vosk-model-small-pt-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["portuguese", "pt"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "ru": {
            "name": "Russian",
            "stt_models": {
                "vosk": "vosk-model-small-ru-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["russian", "ru"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "zh": {
            "name": "Chinese",
            "stt_models": {
                "vosk": "vosk-model-small-cn-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["chinese", "zh"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        },
        "ja": {
            "name": "Japanese",
            "stt_models": {
                "vosk": "vosk-model-small-ja-0.22",
                "openai": "whisper-1"
            },
            "tts_voices": {
                "pyttsx3": ["japanese", "ja"],
                "openai": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        }
    }
    
    def __init__(self, current_language: str = "en"):
        self.current_language = current_language
        self.language_data = self.SUPPORTED_LANGUAGES.get(current_language, self.SUPPORTED_LANGUAGES["en"])
    
    def set_language(self, language_code: str) -> bool:
        """Set the current language"""
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            self.language_data = self.SUPPORTED_LANGUAGES[language_code]
            logger.info(f"Language set to: {self.language_data['name']} ({language_code})")
            return True
        else:
            logger.warning(f"Unsupported language code: {language_code}")
            return False
    
    def get_stt_model(self, engine: str) -> Optional[str]:
        """Get STT model name for current language and engine"""
        return self.language_data.get("stt_models", {}).get(engine)
    
    def get_tts_voices(self, engine: str) -> List[str]:
        """Get available TTS voices for current language and engine"""
        return self.language_data.get("tts_voices", {}).get(engine, [])
    
    def get_model_path(self, engine: str) -> Optional[Path]:
        """Get path to language model"""
        model_name = self.get_stt_model(engine)
        if not model_name:
            return None
        
        if engine == "vosk":
            return settings.data_dir / "vosk_models" / model_name
        return None
    
    def list_supported_languages(self) -> List[Dict[str, str]]:
        """List all supported languages"""
        return [
            {"code": code, "name": data["name"]}
            for code, data in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def is_model_available(self, engine: str) -> bool:
        """Check if language model is available"""
        if engine == "openai":
            return True  # OpenAI supports all languages
        
        model_path = self.get_model_path(engine)
        if model_path:
            return model_path.exists()
        
        return False

