"""Database models for ML performance tracking"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class ModelPerformance(Base):
    """Track model performance metrics"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)  # e.g., "voice_recognition", "pattern_learner"
    model_version = Column(String, default="1.0")
    
    # Metrics
    accuracy = Column(Float)  # Overall accuracy
    precision = Column(Float)  # Precision score
    recall = Column(Float)  # Recall score
    f1_score = Column(Float)  # F1 score
    confidence = Column(Float)  # Average confidence
    
    # Usage stats
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    incorrect_predictions = Column(Integer, default=0)
    
    # Timestamps
    last_evaluated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    extra_metadata = Column(JSON)  # Additional metrics or context


class PredictionLog(Base):
    """Log individual predictions for analysis"""
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)
    prediction_id = Column(String)  # Unique ID for this prediction
    
    # Prediction details
    input_data = Column(JSON)  # Input to the model
    prediction = Column(JSON)  # Model output
    confidence = Column(Float)  # Prediction confidence
    
    # Ground truth (if available)
    ground_truth = Column(JSON)  # Actual/expected result
    is_correct = Column(Boolean)  # Whether prediction was correct
    
    # Context
    user_id = Column(String, default="default")
    context = Column(JSON)  # Additional context
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelTrainingLog(Base):
    """Track model training sessions"""
    __tablename__ = "model_training_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)
    training_session_id = Column(String, nullable=False)
    
    # Training metrics
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    training_accuracy = Column(Float)
    validation_accuracy = Column(Float)
    training_loss = Column(Float)
    validation_loss = Column(Float)
    
    # Training config
    hyperparameters = Column(JSON)
    training_duration_seconds = Column(Float)
    
    # Results
    final_metrics = Column(JSON)
    
    # Status
    status = Column(String, default="completed")  # started, completed, failed
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class ModelComparison(Base):
    """Compare different model versions"""
    __tablename__ = "model_comparisons"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)
    version_a = Column(String, nullable=False)
    version_b = Column(String, nullable=False)
    
    # Comparison metrics
    accuracy_diff = Column(Float)
    precision_diff = Column(Float)
    recall_diff = Column(Float)
    f1_diff = Column(Float)
    
    # Winner
    winner_version = Column(String)
    
    # Test set info
    test_samples = Column(Integer)
    
    # Timestamp
    compared_at = Column(DateTime, default=datetime.utcnow)


# Database setup
def get_metrics_db():
    """Get database session for metrics"""
    db_path = settings.data_dir / "ml_metrics.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

