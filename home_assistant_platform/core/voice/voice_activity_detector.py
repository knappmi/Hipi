"""Voice Activity Detection (VAD) - improved silence detection"""

import logging
import numpy as np
from typing import Optional, Callable
from collections import deque

logger = logging.getLogger(__name__)


class VoiceActivityDetector:
    """Advanced Voice Activity Detection"""
    
    def __init__(
        self,
        energy_threshold: float = 0.01,
        silence_duration: float = 0.5,
        frame_duration: float = 0.03,
        sample_rate: int = 16000
    ):
        self.energy_threshold = energy_threshold
        self.silence_duration = silence_duration
        self.frame_duration = frame_duration
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration)
        
        # Adaptive threshold
        self.adaptive_threshold = energy_threshold
        self.noise_level = 0.0
        self.speech_level = 0.0
        
        # Silence detection
        self.silence_frames = 0
        self.silence_frame_threshold = int(silence_duration / frame_duration)
        
        # History for smoothing
        self.energy_history = deque(maxlen=10)
        self.is_speaking = False
    
    def detect_voice_activity(self, audio_data: bytes) -> bool:
        """Detect if audio contains voice activity"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            audio_array /= 32768.0  # Normalize to [-1, 1]
            
            # Calculate energy (RMS)
            energy = np.sqrt(np.mean(audio_array ** 2))
            
            # Update adaptive threshold
            self._update_adaptive_threshold(energy)
            
            # Check if energy exceeds threshold
            is_voice = energy > self.adaptive_threshold
            
            # Update silence counter
            if is_voice:
                self.silence_frames = 0
                self.is_speaking = True
            else:
                self.silence_frames += 1
                if self.silence_frames >= self.silence_frame_threshold:
                    self.is_speaking = False
            
            self.energy_history.append(energy)
            
            return is_voice
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def _update_adaptive_threshold(self, energy: float):
        """Update adaptive threshold based on noise and speech levels"""
        if not self.is_speaking:
            # Update noise level (exponential moving average)
            self.noise_level = 0.9 * self.noise_level + 0.1 * energy
        else:
            # Update speech level
            self.speech_level = 0.9 * self.speech_level + 0.1 * energy
        
        # Set threshold between noise and speech
        if self.speech_level > 0:
            self.adaptive_threshold = self.noise_level + 0.3 * (self.speech_level - self.noise_level)
        else:
            self.adaptive_threshold = self.energy_threshold
    
    def is_silence(self) -> bool:
        """Check if currently in silence"""
        return not self.is_speaking
    
    def reset(self):
        """Reset VAD state"""
        self.silence_frames = 0
        self.is_speaking = False
        self.energy_history.clear()
        self.noise_level = 0.0
        self.speech_level = 0.0
    
    def get_energy_level(self) -> float:
        """Get current energy level"""
        if self.energy_history:
            return np.mean(list(self.energy_history))
        return 0.0

