"""ML Metrics API endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

router = APIRouter()


class PredictionLogRequest(BaseModel):
    model_name: str
    input_data: Dict[str, Any]
    prediction: Dict[str, Any]
    confidence: float
    ground_truth: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class TrainingLogRequest(BaseModel):
    model_name: str
    training_session_id: str
    training_samples: int
    validation_samples: int
    training_accuracy: float
    validation_accuracy: float
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    training_duration_seconds: Optional[float] = None
    final_metrics: Optional[Dict[str, Any]] = None
    status: str = "completed"


@router.get("/ml-metrics/models")
async def list_models(request: Request):
    """List all tracked models"""
    tracker = request.app.state.ml_tracker
    models = tracker.get_all_model_performance()
    return {"models": models}


@router.get("/ml-metrics/models/{model_name}")
async def get_model_performance(request: Request, model_name: str):
    """Get performance metrics for a specific model"""
    tracker = request.app.state.ml_tracker
    performance = tracker.get_model_performance(model_name)
    
    if not performance:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    return performance


@router.post("/ml-metrics/predictions")
async def log_prediction(request: Request, log_req: PredictionLogRequest):
    """Log a prediction for performance tracking"""
    tracker = request.app.state.ml_tracker
    prediction_id = tracker.log_prediction(
        model_name=log_req.model_name,
        input_data=log_req.input_data,
        prediction=log_req.prediction,
        confidence=log_req.confidence,
        ground_truth=log_req.ground_truth,
        context=log_req.context
    )
    
    return {"success": True, "prediction_id": prediction_id}


@router.get("/ml-metrics/models/{model_name}/predictions")
async def get_prediction_history(
    request: Request,
    model_name: str,
    limit: int = 100,
    user_id: Optional[str] = None
):
    """Get prediction history for a model"""
    tracker = request.app.state.ml_tracker
    history = tracker.get_prediction_history(model_name, limit, user_id)
    return {"predictions": history}


@router.post("/ml-metrics/training")
async def log_training(request: Request, training_req: TrainingLogRequest):
    """Log a model training session"""
    tracker = request.app.state.ml_tracker
    tracker.log_training(
        model_name=training_req.model_name,
        training_session_id=training_req.training_session_id,
        training_samples=training_req.training_samples,
        validation_samples=training_req.validation_samples,
        training_accuracy=training_req.training_accuracy,
        validation_accuracy=training_req.validation_accuracy,
        training_loss=training_req.training_loss,
        validation_loss=training_req.validation_loss,
        hyperparameters=training_req.hyperparameters,
        training_duration_seconds=training_req.training_duration_seconds,
        final_metrics=training_req.final_metrics,
        status=training_req.status
    )
    
    return {"success": True, "message": "Training logged"}


@router.get("/ml-metrics/models/{model_name}/training")
async def get_training_history(request: Request, model_name: str, limit: int = 20):
    """Get training history for a model"""
    tracker = request.app.state.ml_tracker
    history = tracker.get_training_history(model_name, limit)
    return {"training_sessions": history}


@router.get("/ml-metrics/models/{model_name}/metrics")
async def get_detailed_metrics(request: Request, model_name: str):
    """Get detailed metrics including precision, recall, F1"""
    tracker = request.app.state.ml_tracker
    metrics = tracker.calculate_precision_recall(model_name)
    performance = tracker.get_model_performance(model_name)
    
    if not performance:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    return {
        **performance,
        **metrics
    }


@router.post("/ml-metrics/models/{model_name}/compare")
async def compare_models(
    request: Request,
    model_name: str,
    version_a: str,
    version_b: str
):
    """Compare two model versions"""
    tracker = request.app.state.ml_tracker
    comparison = tracker.compare_models(model_name, version_a, version_b)
    
    if "error" in comparison:
        raise HTTPException(status_code=404, detail=comparison["error"])
    
    return comparison

