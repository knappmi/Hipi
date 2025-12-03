"""Model performance tracker"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, Any, List
from collections import defaultdict
from home_assistant_platform.core.ml_metrics.models import (
    ModelPerformance,
    PredictionLog,
    ModelTrainingLog,
    ModelComparison,
    get_metrics_db
)

logger = logging.getLogger(__name__)


class ModelPerformanceTracker:
    """Track and analyze model performance"""
    
    def __init__(self):
        self.db = get_metrics_db()
    
    def log_prediction(
        self,
        model_name: str,
        input_data: Dict[str, Any],
        prediction: Dict[str, Any],
        confidence: float,
        ground_truth: Optional[Dict[str, Any]] = None,
        user_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a prediction for analysis"""
        prediction_id = str(uuid.uuid4())
        
        with self.db() as db:
            is_correct = None
            if ground_truth:
                # Compare prediction with ground truth
                is_correct = self._compare_prediction(prediction, ground_truth)
            
            log = PredictionLog(
                model_name=model_name,
                prediction_id=prediction_id,
                input_data=input_data,
                prediction=prediction,
                confidence=confidence,
                ground_truth=ground_truth,
                is_correct=is_correct,
                user_id=user_id,
                context=context or {}
            )
            
            db.add(log)
            db.commit()
            
            # Update model performance metrics
            self._update_performance_metrics(model_name, is_correct, confidence)
        
        return prediction_id
    
    def _compare_prediction(self, prediction: Dict, ground_truth: Dict) -> bool:
        """Compare prediction with ground truth"""
        # Simple comparison - can be enhanced based on model type
        if isinstance(prediction, dict) and isinstance(ground_truth, dict):
            # Compare key fields
            for key in ground_truth:
                if key in prediction:
                    if prediction[key] != ground_truth[key]:
                        return False
            return True
        return prediction == ground_truth
    
    def _update_performance_metrics(
        self,
        model_name: str,
        is_correct: Optional[bool],
        confidence: float
    ):
        """Update performance metrics for a model"""
        with self.db() as db:
            perf = db.query(ModelPerformance).filter_by(
                model_name=model_name
            ).first()
            
            if not perf:
                perf = ModelPerformance(
                    model_name=model_name,
                    total_predictions=0,
                    correct_predictions=0,
                    incorrect_predictions=0,
                    confidence=0.0
                )
                db.add(perf)
            
            perf.total_predictions += 1
            perf.last_evaluated = datetime.utcnow()
            
            if is_correct is not None:
                if is_correct:
                    perf.correct_predictions += 1
                else:
                    perf.incorrect_predictions += 1
                
                # Update accuracy
                if perf.total_predictions > 0:
                    perf.accuracy = perf.correct_predictions / perf.total_predictions
            
            # Update average confidence
            if perf.total_predictions == 1:
                perf.confidence = confidence
            else:
                # Running average
                perf.confidence = (
                    (perf.confidence * (perf.total_predictions - 1) + confidence) /
                    perf.total_predictions
                )
            
            db.commit()
    
    def log_training(
        self,
        model_name: str,
        training_session_id: str,
        training_samples: int,
        validation_samples: int,
        training_accuracy: float,
        validation_accuracy: float,
        training_loss: Optional[float] = None,
        validation_loss: Optional[float] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        training_duration_seconds: Optional[float] = None,
        final_metrics: Optional[Dict[str, Any]] = None,
        status: str = "completed"
    ):
        """Log a model training session"""
        with self.db() as db:
            log = ModelTrainingLog(
                model_name=model_name,
                training_session_id=training_session_id,
                training_samples=training_samples,
                validation_samples=validation_samples,
                training_accuracy=training_accuracy,
                validation_accuracy=validation_accuracy,
                training_loss=training_loss,
                validation_loss=validation_loss,
                hyperparameters=hyperparameters or {},
                training_duration_seconds=training_duration_seconds,
                final_metrics=final_metrics or {},
                status=status
            )
            
            if status == "completed":
                log.completed_at = datetime.utcnow()
            
            db.add(log)
            db.commit()
            
            logger.info(f"Logged training session {training_session_id} for {model_name}")
    
    def get_model_performance(
        self,
        model_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get current performance metrics for a model"""
        with self.db() as db:
            perf = db.query(ModelPerformance).filter_by(
                model_name=model_name
            ).first()
            
            if not perf:
                return None
            
            return {
                "model_name": perf.model_name,
                "model_version": perf.model_version,
                "accuracy": perf.accuracy,
                "precision": perf.precision,
                "recall": perf.recall,
                "f1_score": perf.f1_score,
                "confidence": perf.confidence,
                "total_predictions": perf.total_predictions,
                "correct_predictions": perf.correct_predictions,
                "incorrect_predictions": perf.incorrect_predictions,
                "last_evaluated": perf.last_evaluated.isoformat() if perf.last_evaluated else None,
                "metadata": perf.extra_metadata or {}
            }
    
    def get_all_model_performance(self) -> List[Dict[str, Any]]:
        """Get performance metrics for all models"""
        with self.db() as db:
            models = db.query(ModelPerformance).all()
            return [
                {
                    "model_name": m.model_name,
                    "model_version": m.model_version,
                    "accuracy": m.accuracy,
                    "confidence": m.confidence,
                    "total_predictions": m.total_predictions,
                    "last_evaluated": m.last_evaluated.isoformat() if m.last_evaluated else None
                }
                for m in models
            ]
    
    def get_prediction_history(
        self,
        model_name: str,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get prediction history for a model"""
        with self.db() as db:
            query = db.query(PredictionLog).filter_by(model_name=model_name)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            logs = query.order_by(PredictionLog.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "prediction_id": log.prediction_id,
                    "input_data": log.input_data,
                    "prediction": log.prediction,
                    "confidence": log.confidence,
                    "ground_truth": log.ground_truth,
                    "is_correct": log.is_correct,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
    
    def calculate_precision_recall(
        self,
        model_name: str,
        class_label: Optional[str] = None
    ) -> Dict[str, float]:
        """Calculate precision and recall for a model"""
        with self.db() as db:
            logs = db.query(PredictionLog).filter_by(
                model_name=model_name
            ).filter(PredictionLog.is_correct.isnot(None)).all()
            
            if not logs:
                return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}
            
            true_positives = sum(1 for log in logs if log.is_correct)
            false_positives = sum(1 for log in logs if not log.is_correct)
            false_negatives = 0  # Would need ground truth for all negatives
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            # Update model performance
            perf = db.query(ModelPerformance).filter_by(model_name=model_name).first()
            if perf:
                perf.precision = precision
                perf.recall = recall
                perf.f1_score = f1_score
                db.commit()
            
            return {
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score
            }
    
    def get_training_history(
        self,
        model_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get training history for a model"""
        with self.db() as db:
            logs = db.query(ModelTrainingLog).filter_by(
                model_name=model_name
            ).order_by(ModelTrainingLog.started_at.desc()).limit(limit).all()
            
            return [
                {
                    "training_session_id": log.training_session_id,
                    "training_samples": log.training_samples,
                    "validation_samples": log.validation_samples,
                    "training_accuracy": log.training_accuracy,
                    "validation_accuracy": log.validation_accuracy,
                    "training_loss": log.training_loss,
                    "validation_loss": log.validation_loss,
                    "status": log.status,
                    "started_at": log.started_at.isoformat(),
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "training_duration_seconds": log.training_duration_seconds
                }
                for log in logs
            ]
    
    def compare_models(
        self,
        model_name: str,
        version_a: str,
        version_b: str
    ) -> Dict[str, Any]:
        """Compare two model versions"""
        with self.db() as db:
            perf_a = db.query(ModelPerformance).filter_by(
                model_name=model_name,
                model_version=version_a
            ).first()
            
            perf_b = db.query(ModelPerformance).filter_by(
                model_name=model_name,
                model_version=version_b
            ).first()
            
            if not perf_a or not perf_b:
                return {"error": "One or both model versions not found"}
            
            accuracy_diff = perf_b.accuracy - perf_a.accuracy if perf_b.accuracy and perf_a.accuracy else 0
            precision_diff = perf_b.precision - perf_a.precision if perf_b.precision and perf_a.precision else 0
            recall_diff = perf_b.recall - perf_a.recall if perf_b.recall and perf_a.recall else 0
            f1_diff = perf_b.f1_score - perf_a.f1_score if perf_b.f1_score and perf_a.f1_score else 0
            
            winner = version_b if accuracy_diff > 0 else version_a
            
            comparison = ModelComparison(
                model_name=model_name,
                version_a=version_a,
                version_b=version_b,
                accuracy_diff=accuracy_diff,
                precision_diff=precision_diff,
                recall_diff=recall_diff,
                f1_diff=f1_diff,
                winner_version=winner
            )
            
            db.add(comparison)
            db.commit()
            
            return {
                "model_name": model_name,
                "version_a": version_a,
                "version_b": version_b,
                "accuracy_diff": accuracy_diff,
                "precision_diff": precision_diff,
                "recall_diff": recall_diff,
                "f1_diff": f1_diff,
                "winner": winner
            }

