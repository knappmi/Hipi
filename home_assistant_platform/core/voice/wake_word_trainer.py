"""Wake word training system"""

import logging
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class WakeWordTrainer:
    """Train and manage custom wake words"""
    
    def __init__(self):
        self.trained_wake_words: Dict[str, Dict] = {}
        self.training_data_dir = settings.data_dir / "wake_words"
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        self._load_trained_words()
    
    def _load_trained_words(self):
        """Load trained wake words from disk"""
        config_file = self.training_data_dir / "trained_words.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.trained_wake_words = json.load(f)
                logger.info(f"Loaded {len(self.trained_wake_words)} trained wake words")
            except Exception as e:
                logger.error(f"Error loading trained wake words: {e}")
    
    def _save_trained_words(self):
        """Save trained wake words to disk"""
        config_file = self.training_data_dir / "trained_words.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.trained_wake_words, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving trained wake words: {e}")
    
    def start_training(self, wake_word: str, user_id: str = "default") -> Dict[str, any]:
        """Start training a new wake word"""
        wake_word_id = f"{user_id}_{wake_word.lower().replace(' ', '_')}"
        
        training_session = {
            "id": wake_word_id,
            "wake_word": wake_word,
            "user_id": user_id,
            "status": "training",
            "samples": [],
            "created_at": datetime.utcnow().isoformat(),
            "min_samples": 5,  # Minimum samples needed
            "confidence_threshold": 0.7
        }
        
        self.trained_wake_words[wake_word_id] = training_session
        self._save_trained_words()
        
        logger.info(f"Started training wake word: {wake_word} (ID: {wake_word_id})")
        return training_session
    
    def add_training_sample(self, wake_word_id: str, audio_data: bytes, transcription: str) -> bool:
        """Add a training sample"""
        if wake_word_id not in self.trained_wake_words:
            logger.error(f"Wake word {wake_word_id} not found")
            return False
        
        session = self.trained_wake_words[wake_word_id]
        
        # Save audio sample
        sample_id = f"{wake_word_id}_{len(session['samples'])}"
        sample_file = self.training_data_dir / f"{sample_id}.wav"
        
        try:
            with open(sample_file, 'wb') as f:
                f.write(audio_data)
            
            sample = {
                "id": sample_id,
                "file": str(sample_file),
                "transcription": transcription,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            session["samples"].append(sample)
            
            # Check if we have enough samples
            if len(session["samples"]) >= session["min_samples"]:
                session["status"] = "ready"
                logger.info(f"Wake word {wake_word_id} training complete ({len(session['samples'])} samples)")
            
            self._save_trained_words()
            return True
            
        except Exception as e:
            logger.error(f"Error saving training sample: {e}")
            return False
    
    def get_training_status(self, wake_word_id: str) -> Optional[Dict]:
        """Get training status"""
        return self.trained_wake_words.get(wake_word_id)
    
    def finish_training(self, wake_word_id: str) -> bool:
        """Finish training and activate wake word"""
        if wake_word_id not in self.trained_wake_words:
            return False
        
        session = self.trained_wake_words[wake_word_id]
        
        if len(session["samples"]) < session["min_samples"]:
            logger.warning(f"Not enough samples for {wake_word_id} ({len(session['samples'])}/{session['min_samples']})")
            return False
        
        session["status"] = "active"
        session["activated_at"] = datetime.utcnow().isoformat()
        self._save_trained_words()
        
        logger.info(f"Wake word {wake_word_id} activated")
        return True
    
    def list_trained_words(self, user_id: Optional[str] = None) -> List[Dict]:
        """List trained wake words"""
        words = list(self.trained_wake_words.values())
        if user_id:
            words = [w for w in words if w.get("user_id") == user_id]
        return words
    
    def delete_trained_word(self, wake_word_id: str) -> bool:
        """Delete a trained wake word"""
        if wake_word_id not in self.trained_wake_words:
            return False
        
        session = self.trained_wake_words[wake_word_id]
        
        # Delete audio samples
        for sample in session.get("samples", []):
            sample_file = Path(sample.get("file", ""))
            if sample_file.exists():
                try:
                    sample_file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete sample file: {e}")
        
        del self.trained_wake_words[wake_word_id]
        self._save_trained_words()
        
        logger.info(f"Deleted wake word: {wake_word_id}")
        return True

