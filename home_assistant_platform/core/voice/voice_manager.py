"""Voice manager - orchestrates STT, TTS, wake word, and intent processing"""

import logging
import asyncio
import threading
import subprocess
from typing import Optional, Callable
from home_assistant_platform.config.settings import settings
from home_assistant_platform.core.voice.stt_engine import STTEngine
from home_assistant_platform.core.voice.tts_engine import TTSEngine
from home_assistant_platform.core.voice.wake_word import WakeWordDetector
from home_assistant_platform.core.voice.intent_processor import IntentProcessor
from home_assistant_platform.core.voice.audio_utils import play_acknowledgment

logger = logging.getLogger(__name__)


class VoiceManager:
    """Manages all voice processing components"""
    
    def __init__(self):
        self.enabled = settings.voice_enabled
        self.stt: Optional[STTEngine] = None
        self.tts: Optional[TTSEngine] = None
        self.wake_word_detector: Optional[WakeWordDetector] = None
        self.intent_processor: Optional[IntentProcessor] = None
        self.is_listening = False
        self.is_awake = False  # Track if wake word was detected
        self.conversation_mode = settings.conversation_mode  # Conversation mode state
        self.conversation_context = []  # Store conversation history for context
        self.on_intent_callback: Optional[Callable] = None
        self.listening_thread: Optional[threading.Thread] = None
        
        if self.enabled:
            self._initialize()
            # Auto-start listening if enabled
            if self.enabled:
                self._start_background_listening()
    
    def _initialize(self):
        """Initialize voice components"""
        try:
            self.stt = STTEngine()
            self.tts = TTSEngine()
            self.wake_word_detector = WakeWordDetector()
            self.intent_processor = IntentProcessor()
            logger.info("Voice manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize voice manager: {e}")
            self.enabled = False
    
    def _play_acknowledgment(self):
        """Play acknowledgment sound when wake word is detected"""
        try:
            play_acknowledgment()
            logger.info("Acknowledgment sound played")
        except Exception as e:
            logger.debug(f"Could not play acknowledgment: {e}")
    
    def _start_background_listening(self):
        """Start continuous listening in background thread"""
        if self.is_listening:
            return
        
        def listening_loop():
            """Main listening loop"""
            logger.info("Starting continuous voice listening...")
            self.is_listening = True
            
            # Try to start actual audio listening if STT is available
            if self.stt and self.stt.engine:
                try:
                    # Use STT engine's continuous listening
                    self.stt.listen_continuous(self._process_voice_input)
                except Exception as e:
                    logger.warning(f"Could not start STT continuous listening: {e}")
                    logger.info("Voice listening active but waiting for manual input via API")
            else:
                logger.info("STT engine not available - voice listening ready for API input")
                # Keep thread alive but don't consume CPU
                import time
                while self.is_listening:
                    time.sleep(1)
        
        self.listening_thread = threading.Thread(target=listening_loop, daemon=True)
        self.listening_thread.start()
        logger.info("Background listening thread started")
    
    def start_listening(self, on_intent: Callable):
        """Start continuous voice listening"""
        if not self.enabled or not self.stt:
            logger.warning("Voice processing not enabled or initialized")
            return
        
        self.on_intent_callback = on_intent
        self._start_background_listening()
    
    def _process_voice_input(self, text: str):
        """Process voice input with wake word detection"""
        if not text or not text.strip():
            return
        
        text = text.strip()
        logger.info(f"Received voice input: {text}")  # Changed to INFO for visibility
        
        # Check for wake word
        if self.wake_word_detector:
            wake_word_detected = self.wake_word_detector.detect(text)
            
            if wake_word_detected:
                if not self.is_awake:
                    # Wake word detected - play acknowledgment and enter listening mode
                    logger.info(f"Wake word detected: {self.wake_word_detector.wake_word}")
                    self.is_awake = True
                    self._play_acknowledgment()
                    # Remove wake word from text
                    wake_words = self.wake_word_detector.wake_word.split('_')
                    for word in wake_words:
                        text = text.replace(word, '', 1).strip()
                    
                    if not text:
                        # Only wake word, wait for next command
                        logger.info("Awake and waiting for command...")
                        return
                    # If there's text after wake word, process it
                    logger.info(f"Processing command after wake word: {text}")
                else:
                    # Already awake, this might be a new wake word or continuation
                    # Remove wake word if present
                    wake_words = self.wake_word_detector.wake_word.split('_')
                    for word in wake_words:
                        text = text.replace(word, '', 1).strip()
                
                # Process the command
                if text:
                    intent = self.intent_processor.process(text)
                    if intent and self.on_intent_callback:
                        self.on_intent_callback(intent)
                    self.is_awake = False  # Reset after processing
            else:
                # No wake word in this text
                if self.is_awake or self.conversation_mode:
                    # We're already awake from previous wake word OR in conversation mode
                    logger.info(f"Processing command (awake: {self.is_awake}, conversation: {self.conversation_mode}): {text}")
                    intent = self.intent_processor.process(text)
                    
                    # Check for conversation mode toggle commands
                    if intent and intent.get("intent") == "toggle_conversation":
                        self.conversation_mode = not self.conversation_mode
                        settings.conversation_mode = self.conversation_mode
                        response = "Conversation mode enabled" if self.conversation_mode else "Conversation mode disabled"
                        self.speak(response)
                        logger.info(f"Conversation mode toggled: {self.conversation_mode}")
                        if not self.conversation_mode:
                            self.is_awake = False  # Exit conversation mode
                        return
                    
                    if intent and self.on_intent_callback:
                        self.on_intent_callback(intent)
                    
                    # In conversation mode, stay awake; otherwise reset
                    if not self.conversation_mode:
                        self.is_awake = False  # Reset after processing
                    else:
                        # Stay awake in conversation mode, add to context
                        self.conversation_context.append({"user": text, "intent": intent})
                        # Keep last 5 exchanges for context
                        if len(self.conversation_context) > 5:
                            self.conversation_context.pop(0)
                elif not settings.wake_word or settings.wake_word == "":
                    # Always listening mode
                    intent = self.intent_processor.process(text)
                    if intent and self.on_intent_callback:
                        self.on_intent_callback(intent)
                else:
                    # Not awake and wake word required - ignore
                    logger.debug(f"Ignoring input (no wake word): {text}")
        else:
            # No wake word detector - process directly
            intent = self.intent_processor.process(text)
            if intent and self.on_intent_callback:
                self.on_intent_callback(intent)
    
    def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=2)
        logger.info("Voice listening stopped")
    
    def speak(self, text: str) -> bool:
        """Speak text using TTS"""
        if not self.enabled or not self.tts:
            return False
        return self.tts.speak(text)
    
    def process_command(self, text: str) -> Optional[dict]:
        """Process a text command and return intent"""
        if not self.intent_processor:
            return None
        return self.intent_processor.process(text)
    
    def cleanup(self):
        """Cleanup voice resources"""
        if self.stt:
            self.stt.cleanup()
        if self.tts:
            self.tts.cleanup()
        self.is_listening = False

