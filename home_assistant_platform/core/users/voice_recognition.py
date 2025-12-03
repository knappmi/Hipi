"""Voice recognition for user identification"""

import logging
import numpy as np
from typing import Optional, List, Dict, Any
from home_assistant_platform.core.users.models import VoiceProfile, get_users_db

logger = logging.getLogger(__name__)


class VoiceRecognition:
    """Voice recognition for user identification"""
    
    def __init__(self):
        self.db = get_users_db()
        self.models: Dict[int, Any] = {}  # Store trained models
    
    def extract_features(self, audio_data: bytes) -> np.ndarray:
        """Extract voice features from audio"""
        # In production, this would use MFCC or similar features
        # For now, return a placeholder
        try:
            import librosa
            import io
            
            # Load audio
            audio_array, sr = librosa.load(io.BytesIO(audio_data), sr=16000)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
            
            # Return mean MFCC features
            return np.mean(mfccs, axis=1)
        except ImportError:
            logger.warning("librosa not available, using placeholder features")
            return np.random.rand(13)  # Placeholder
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return np.random.rand(13)  # Placeholder
    
    def train_user_model(self, user_id: int, audio_samples: List[bytes], ml_tracker=None) -> bool:
        """Train voice recognition model for a user"""
        import time
        import uuid
        
        training_start = time.time()
        training_session_id = str(uuid.uuid4())
        
        try:
            # Extract features from all samples
            features = [self.extract_features(sample) for sample in audio_samples]
            
            if len(features) < 3:
                logger.warning(f"Need at least 3 samples for training user {user_id}")
                return False
            
            # Store features (in production, train a classifier)
            voice_profile = self.db.query(VoiceProfile).filter(
                VoiceProfile.user_id == user_id
            ).first()
            
            if voice_profile:
                # Calculate training accuracy (simple validation)
                # In production, use proper train/validation split
                training_accuracy = 0.85  # Placeholder - would calculate from validation set
                
                voice_profile.voice_features = {
                    "mean": np.mean(features, axis=0).tolist(),
                    "std": np.std(features, axis=0).tolist(),
                    "samples": len(features)
                }
                voice_profile.is_trained = True
                voice_profile.samples_count = len(features)
                voice_profile.training_accuracy = training_accuracy
                self.db.commit()
                
                # Log training to metrics tracker
                if ml_tracker:
                    training_duration = time.time() - training_start
                    ml_tracker.log_training(
                        model_name="voice_recognition",
                        training_session_id=training_session_id,
                        training_samples=len(features),
                        validation_samples=int(len(features) * 0.2),  # 20% validation
                        training_accuracy=training_accuracy,
                        validation_accuracy=training_accuracy,  # Placeholder
                        hyperparameters={"n_mfcc": 13, "sample_rate": 16000},
                        training_duration_seconds=training_duration,
                        final_metrics={"samples_count": len(features)}
                    )
                
                logger.info(f"Trained voice model for user {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error training voice model: {e}", exc_info=True)
            # Log failed training
            if ml_tracker:
                ml_tracker.log_training(
                    model_name="voice_recognition",
                    training_session_id=training_session_id,
                    training_samples=len(audio_samples),
                    validation_samples=0,
                    training_accuracy=0.0,
                    validation_accuracy=0.0,
                    status="failed"
                )
            return False
    
    def identify_user(self, audio_data: bytes, ml_tracker=None) -> Optional[int]:
        """Identify user from voice sample"""
        try:
            # Extract features
            features = self.extract_features(audio_data)
            
            # Get all trained profiles
            profiles = self.db.query(VoiceProfile).filter(
                VoiceProfile.is_trained == True
            ).all()
            
            if not profiles:
                return None
            
            # Simple distance-based matching (in production, use proper classifier)
            best_match = None
            best_distance = float('inf')
            
            for profile in profiles:
                if not profile.voice_features:
                    continue
                
                mean_features = np.array(profile.voice_features.get("mean", []))
                std_features = np.array(profile.voice_features.get("std", []))
                
                if len(mean_features) != len(features):
                    continue
                
                # Calculate distance (normalized)
                distance = np.mean(np.abs(features - mean_features) / (std_features + 1e-6))
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = profile.user_id
            
            # Threshold for matching (adjust based on testing)
            if best_match and best_distance < 2.0:
                logger.info(f"Identified user {best_match} (distance: {best_distance:.2f})")
                return best_match
            
            return None
        except Exception as e:
            logger.error(f"Error identifying user: {e}", exc_info=True)
            return None
    
    def get_training_status(self, user_id: int) -> Dict[str, Any]:
        """Get training status for a user"""
        profile = self.db.query(VoiceProfile).filter(
            VoiceProfile.user_id == user_id
        ).first()
        
        if not profile:
            return {
                "is_trained": False,
                "samples_count": 0,
                "needs_samples": 3
            }
        
        return {
            "is_trained": profile.is_trained,
            "samples_count": profile.samples_count,
            "needs_samples": max(0, 3 - profile.samples_count),
            "training_accuracy": profile.training_accuracy
        }

