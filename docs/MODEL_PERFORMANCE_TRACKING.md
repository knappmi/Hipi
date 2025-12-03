# Model Performance Tracking

Comprehensive system for tracking and analyzing ML model performance across the platform.

## Overview

The platform includes several ML models that benefit from performance tracking:
- **Voice Recognition**: User identification from voice samples
- **Pattern Learning**: Learning device usage patterns
- **Automation Suggestions**: Generating automation recommendations
- **Intent Processing**: Understanding voice commands
- **STT/TTS Models**: Speech-to-text and text-to-speech accuracy

## Features

### 1. **Prediction Logging**
Track every prediction made by models:
- Input data
- Model output
- Confidence scores
- Ground truth (when available)
- Correctness flag

### 2. **Performance Metrics**
Automatic calculation of:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1 Score**: Harmonic mean of precision and recall
- **Confidence**: Average prediction confidence

### 3. **Training Tracking**
Monitor model training sessions:
- Training/validation accuracy
- Loss metrics
- Hyperparameters
- Training duration
- Training history

### 4. **Model Comparison**
Compare different model versions:
- Side-by-side metrics
- Performance deltas
- Winner identification

## API Usage

### Log a Prediction

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ml-metrics/predictions",
    json={
        "model_name": "voice_recognition",
        "input_data": {"audio_length": 2.5, "sample_rate": 16000},
        "prediction": {"user_id": 1, "confidence": 0.92},
        "confidence": 0.92,
        "ground_truth": {"user_id": 1},
        "context": {"device": "living_room_mic"}
    }
)
```

### Get Model Performance

```bash
curl http://localhost:8000/api/v1/ml-metrics/models/voice_recognition
```

Response:
```json
{
    "model_name": "voice_recognition",
    "model_version": "1.0",
    "accuracy": 0.87,
    "precision": 0.85,
    "recall": 0.89,
    "f1_score": 0.87,
    "confidence": 0.91,
    "total_predictions": 1250,
    "correct_predictions": 1087,
    "incorrect_predictions": 163,
    "last_evaluated": "2024-01-15T10:30:00Z"
}
```

### Log Training Session

```python
response = requests.post(
    "http://localhost:8000/api/v1/ml-metrics/training",
    json={
        "model_name": "voice_recognition",
        "training_session_id": "train_20240115_001",
        "training_samples": 1000,
        "validation_samples": 200,
        "training_accuracy": 0.92,
        "validation_accuracy": 0.88,
        "training_loss": 0.15,
        "validation_loss": 0.22,
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 50
        },
        "training_duration_seconds": 1250.5
    }
)
```

### Get Prediction History

```bash
curl "http://localhost:8000/api/v1/ml-metrics/models/voice_recognition/predictions?limit=50"
```

### Get Training History

```bash
curl http://localhost:8000/api/v1/ml-metrics/models/voice_recognition/training
```

### Compare Model Versions

```bash
curl -X POST "http://localhost:8000/api/v1/ml-metrics/models/voice_recognition/compare?version_a=1.0&version_b=1.1"
```

## Integration Examples

### Voice Recognition Integration

```python
from home_assistant_platform.core.ml_metrics.tracker import ModelPerformanceTracker

tracker = ModelPerformanceTracker()

# After identifying user
user_id = voice_recognition.identify_user(audio_data, ml_tracker=tracker)

# Log the prediction
tracker.log_prediction(
    model_name="voice_recognition",
    input_data={"audio_length": len(audio_data)},
    prediction={"user_id": user_id, "confidence": confidence},
    confidence=confidence,
    ground_truth={"user_id": actual_user_id} if known else None
)
```

### Pattern Learning Integration

```python
# After detecting a pattern
pattern = pattern_learner.detect_pattern(device_id)

# Log pattern detection
tracker.log_prediction(
    model_name="pattern_learner",
    input_data={"device_id": device_id, "action_count": len(actions)},
    prediction={"pattern_type": pattern.type, "confidence": pattern.confidence},
    confidence=pattern.confidence
)
```

### Automation Suggestion Integration

```python
# After generating suggestion
suggestion = suggestion_engine.generate_suggestion(pattern)

# Track suggestion acceptance
if user_accepts:
    tracker.log_prediction(
        model_name="suggestion_engine",
        input_data={"pattern_id": pattern.id},
        prediction={"suggestion_id": suggestion.id, "accepted": True},
        confidence=suggestion.confidence,
        ground_truth={"accepted": True}
    )
```

## Metrics Dashboard

### Key Metrics to Monitor

1. **Voice Recognition**
   - Accuracy: Target > 90%
   - Confidence: Average > 0.85
   - False positive rate: < 5%

2. **Pattern Learning**
   - Pattern detection accuracy
   - Confidence in detected patterns
   - Pattern prediction success rate

3. **Automation Suggestions**
   - Suggestion acceptance rate
   - User satisfaction with suggestions
   - Automation success rate

4. **Intent Processing**
   - Intent recognition accuracy
   - Command understanding rate
   - False positive rate

## Performance Targets

### Voice Recognition
- **Accuracy**: > 90%
- **Precision**: > 0.88
- **Recall**: > 0.90
- **F1 Score**: > 0.89

### Pattern Learning
- **Pattern Detection Accuracy**: > 85%
- **Confidence**: > 0.75
- **False Positive Rate**: < 10%

### Automation Suggestions
- **Acceptance Rate**: > 60%
- **User Satisfaction**: > 4.0/5.0
- **Automation Success**: > 95%

## Best Practices

1. **Log All Predictions**: Track every model prediction
2. **Include Ground Truth**: When available, provide ground truth for accuracy calculation
3. **Regular Evaluation**: Periodically calculate precision/recall
4. **Monitor Trends**: Track performance over time
5. **Compare Versions**: Compare new model versions before deployment
6. **User Feedback**: Incorporate user feedback into ground truth

## Database Schema

### ModelPerformance
- Model name and version
- Accuracy, precision, recall, F1
- Total/correct/incorrect predictions
- Average confidence

### PredictionLog
- Individual prediction records
- Input/output data
- Confidence scores
- Ground truth
- Correctness flag

### ModelTrainingLog
- Training session details
- Training/validation metrics
- Hyperparameters
- Training duration

### ModelComparison
- Version comparisons
- Performance deltas
- Winner identification

## CLI Usage

```bash
# List all tracked models
hap ml-metrics list

# Get model performance
hap ml-metrics performance voice_recognition

# View prediction history
hap ml-metrics predictions voice_recognition --limit 50

# View training history
hap ml-metrics training voice_recognition

# Compare model versions
hap ml-metrics compare voice_recognition --version-a 1.0 --version-b 1.1
```

## Future Enhancements

1. **Real-time Dashboards**: Web UI for model performance
2. **Alerting**: Alerts when performance drops
3. **A/B Testing**: Built-in A/B testing framework
4. **Model Versioning**: Automatic model versioning
5. **Performance Reports**: Automated performance reports
6. **Drift Detection**: Detect model performance drift

