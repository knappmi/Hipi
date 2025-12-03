"""Enhanced voice features API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from home_assistant_platform.core.voice.language_manager import LanguageManager
from home_assistant_platform.core.voice.wake_word_trainer import WakeWordTrainer
from home_assistant_platform.core.voice.voice_cloning import VoiceCloningManager
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class LanguageChangeRequest(BaseModel):
    language_code: str


class WakeWordTrainingRequest(BaseModel):
    wake_word: str
    description: Optional[str] = None


class VoiceCloningRequest(BaseModel):
    voice_name: str
    description: Optional[str] = None


def get_language_manager(request: Request) -> LanguageManager:
    """Get language manager from app state"""
    if not hasattr(request.app.state, 'language_manager'):
        request.app.state.language_manager = LanguageManager(settings.language)
    return request.app.state.language_manager


def get_wake_word_trainer(request: Request) -> WakeWordTrainer:
    """Get wake word trainer from app state"""
    if not hasattr(request.app.state, 'wake_word_trainer'):
        request.app.state.wake_word_trainer = WakeWordTrainer()
    return request.app.state.wake_word_trainer


def get_voice_cloning_manager(request: Request) -> VoiceCloningManager:
    """Get voice cloning manager from app state"""
    if not hasattr(request.app.state, 'voice_cloning_manager'):
        manager = VoiceCloningManager()
        if settings.elevenlabs_api_key:
            manager.configure_elevenlabs(settings.elevenlabs_api_key)
        request.app.state.voice_cloning_manager = manager
    return request.app.state.voice_cloning_manager


@router.get("/languages")
async def list_languages(request: Request):
    """List all supported languages"""
    language_manager = get_language_manager(request)
    languages = language_manager.list_supported_languages()
    current_language = language_manager.current_language
    
    return {
        "languages": languages,
        "current_language": current_language,
        "current_language_name": language_manager.language_data["name"]
    }


@router.post("/languages")
async def change_language(request: Request, lang_req: LanguageChangeRequest):
    """Change the current language"""
    language_manager = get_language_manager(request)
    
    success = language_manager.set_language(lang_req.language_code)
    if not success:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang_req.language_code}")
    
    # Update settings
    settings.language = lang_req.language_code
    
    # Check if model is available
    model_available = language_manager.is_model_available(settings.stt_engine)
    
    return {
        "success": True,
        "language": lang_req.language_code,
        "language_name": language_manager.language_data["name"],
        "model_available": model_available,
        "message": "Language changed. Please restart voice services to apply changes."
    }


@router.get("/wake-words/trained")
async def list_trained_wake_words(request: Request, user_id: str = "default"):
    """List trained wake words"""
    trainer = get_wake_word_trainer(request)
    words = trainer.list_trained_words(user_id=user_id)
    return {"wake_words": words}


@router.post("/wake-words/train")
async def start_wake_word_training(request: Request, training_req: WakeWordTrainingRequest, user_id: str = "default"):
    """Start training a new wake word"""
    trainer = get_wake_word_trainer(request)
    session = trainer.start_training(training_req.wake_word, user_id)
    return {
        "success": True,
        "session": session,
        "message": f"Training started. Provide {session['min_samples']} audio samples."
    }


@router.post("/wake-words/train/{session_id}/sample")
async def add_training_sample(
    request: Request,
    session_id: str,
    audio_file: UploadFile = File(...),
    transcription: Optional[str] = None
):
    """Add a training sample for wake word"""
    trainer = get_wake_word_trainer(request)
    
    # Read audio data
    audio_data = await audio_file.read()
    
    # Get transcription if not provided
    if not transcription:
        # Use STT to transcribe
        if hasattr(request.app.state, 'voice_manager'):
            # Would need to integrate with STT engine
            transcription = "wake_word_sample"  # Placeholder
    
    success = trainer.add_training_sample(session_id, audio_data, transcription or "")
    
    if not success:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    session = trainer.get_training_status(session_id)
    
    return {
        "success": True,
        "session": session,
        "samples_collected": len(session.get("samples", [])),
        "samples_needed": session.get("min_samples", 5)
    }


@router.post("/wake-words/train/{session_id}/finish")
async def finish_wake_word_training(request: Request, session_id: str):
    """Finish training and activate wake word"""
    trainer = get_wake_word_trainer(request)
    success = trainer.finish_training(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Training not complete or session not found")
    
    session = trainer.get_training_status(session_id)
    return {
        "success": True,
        "session": session,
        "message": "Wake word training complete and activated"
    }


@router.delete("/wake-words/{wake_word_id}")
async def delete_trained_wake_word(request: Request, wake_word_id: str):
    """Delete a trained wake word"""
    trainer = get_wake_word_trainer(request)
    success = trainer.delete_trained_word(wake_word_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Wake word not found")
    
    return {"success": True, "message": "Wake word deleted"}


@router.get("/voice-cloning/voices")
async def list_cloned_voices(request: Request):
    """List cloned voices"""
    manager = get_voice_cloning_manager(request)
    
    if not settings.elevenlabs_enabled:
        return {
            "enabled": False,
            "message": "ElevenLabs not enabled. Configure ELEVENLABS_API_KEY to enable."
        }
    
    voices = manager.list_cloned_voices()
    return {
        "enabled": True,
        "voices": voices,
        "current_voice": manager.current_voice_id
    }


@router.post("/voice-cloning/clone")
async def clone_voice(
    request: Request,
    cloning_req: VoiceCloningRequest,
    audio_samples: List[UploadFile] = File(...)
):
    """Clone a voice from audio samples"""
    manager = get_voice_cloning_manager(request)
    
    if not settings.elevenlabs_enabled:
        raise HTTPException(status_code=400, detail="ElevenLabs not enabled")
    
    # Read audio samples
    samples_data = []
    for audio_file in audio_samples:
        data = await audio_file.read()
        samples_data.append(data)
    
    if len(samples_data) < 1:
        raise HTTPException(status_code=400, detail="At least one audio sample required")
    
    voice_id = await manager.clone_voice(
        cloning_req.voice_name,
        samples_data,
        cloning_req.description
    )
    
    if not voice_id:
        raise HTTPException(status_code=500, detail="Failed to clone voice")
    
    return {
        "success": True,
        "voice_id": voice_id,
        "message": "Voice cloned successfully"
    }


@router.post("/voice-cloning/set-voice")
async def set_current_voice(request: Request, voice_id: str):
    """Set the current voice to use"""
    manager = get_voice_cloning_manager(request)
    success = manager.set_current_voice(voice_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {
        "success": True,
        "voice_id": voice_id,
        "message": "Voice set as current"
    }


@router.delete("/voice-cloning/{voice_id}")
async def delete_cloned_voice(request: Request, voice_id: str):
    """Delete a cloned voice"""
    manager = get_voice_cloning_manager(request)
    success = manager.delete_voice(voice_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"success": True, "message": "Voice deleted"}


@router.get("/vad/status")
async def get_vad_status(request: Request):
    """Get Voice Activity Detection status"""
    return {
        "enabled": settings.vad_enabled,
        "energy_threshold": settings.vad_energy_threshold,
        "silence_duration": settings.vad_silence_duration
    }

