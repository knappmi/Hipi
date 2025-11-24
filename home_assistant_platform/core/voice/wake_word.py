"""Wake word detection"""

import logging
from typing import Callable, Optional
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Wake word detection system"""
    
    def __init__(self, wake_word: Optional[str] = None):
        self.wake_word = wake_word or settings.wake_word
        self.detector = None
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize wake word detector"""
        # For now, use a simple keyword matching approach
        # In production, use Porcupine or similar library
        logger.info(f"Wake word detector initialized for: {self.wake_word}")
    
    def detect(self, text: str) -> bool:
        """Check if wake word is present in text"""
        if not self.wake_word:
            return True  # Always active if no wake word
        
        if not text:
            return False
        
        text_lower = text.lower().strip()
        wake_word_lower = self.wake_word.lower()
        
        # Remove all spaces and special characters for comparison
        text_normalized = ''.join(c for c in text_lower if c.isalnum())
        wake_word_normalized = ''.join(c for c in wake_word_lower if c.isalnum())
        
        # Direct match (case-insensitive, ignoring spaces)
        if wake_word_normalized in text_normalized:
            return True
        
        # Handle underscore-separated wake words (e.g., "hey_assistant")
        wake_words = self.wake_word.split('_')
        
        if len(wake_words) > 1:
            # Multi-word wake word - check if all words appear in order
            wake_words_lower = [w.lower() for w in wake_words]
            text_words = text_lower.split()
            
            # Check if all wake words appear in sequence
            wake_idx = 0
            for word in text_words:
                if wake_idx < len(wake_words_lower):
                    # Check if current wake word is in this text word
                    if wake_words_lower[wake_idx] in word or word in wake_words_lower[wake_idx]:
                        wake_idx += 1
                        if wake_idx >= len(wake_words_lower):
                            return True
            
            # Check if combined words match (e.g., "hi pie" -> "hipi")
            text_combined = ''.join(text_words)
            wake_combined = ''.join(wake_words_lower)
            if wake_combined in text_combined or text_combined.startswith(wake_combined):
                return True
        else:
            # Single word wake word (e.g., "HiPi")
            wake_word_single = wake_words[0].lower()
            
            # Check exact match
            if wake_word_single in text_lower:
                return True
            
            # Check if it matches when spoken as multiple words
            # "HiPi" should match "hi pie", "hi pi", "hipi", etc.
            text_no_spaces = text_lower.replace(' ', '')
            if wake_word_single in text_no_spaces:
                return True
            
            # Also check if the wake word can be split into words that appear in text
            # For "hipi", check if "hi" and "pi" appear together
            if len(wake_word_single) >= 2:
                # Try splitting the wake word in different ways
                for i in range(1, len(wake_word_single)):
                    part1 = wake_word_single[:i]
                    part2 = wake_word_single[i:]
                    # Check if both parts appear in text (e.g., "hi" and "pi" in "hi pie")
                    if part1 in text_lower and part2 in text_lower:
                        # Check if they appear close together (within 2 words)
                        text_words = text_lower.split()
                        for j in range(len(text_words)):
                            if part1 in text_words[j]:
                                # Check next few words for part2
                                for k in range(j, min(j+3, len(text_words))):
                                    if part2 in text_words[k]:
                                        return True
        
        return False
    
    def listen_continuous(self, stt_callback: Callable, on_wake: Callable):
        """Continuously listen for wake word"""
        def check_wake(text: str):
            if self.detect(text):
                logger.info(f"Wake word detected: {self.wake_word}")
                on_wake(text)
            else:
                stt_callback(text)
        
        # This would integrate with STT engine for continuous listening
        # For now, it's a placeholder
        logger.info("Continuous wake word detection started")

