"""Voice processing API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import enhanced voice features
from home_assistant_platform.core.api.voice_enhanced import router as voice_enhanced_router

logger = logging.getLogger(__name__)
router = APIRouter()

# Include enhanced voice features
router.include_router(voice_enhanced_router, prefix="/enhanced", tags=["voice-enhanced"])


def get_voice_manager(request: Request):
    """Get voice manager from app state"""
    if not hasattr(request.app.state, 'voice_manager'):
        from home_assistant_platform.core.voice.voice_manager import VoiceManager
        request.app.state.voice_manager = VoiceManager()
    return request.app.state.voice_manager


class SpeakRequest(BaseModel):
    text: str


class VoiceSettingsRequest(BaseModel):
    voice_enabled: Optional[bool] = None
    wake_word: Optional[str] = None
    stt_engine: Optional[str] = None
    tts_engine: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_tts_voice: Optional[str] = None  # Voice selection for OpenAI TTS
    conversation_mode: Optional[bool] = None  # Conversation mode toggle


@router.get("/settings")
async def get_voice_settings(request: Request):
    """Get voice settings"""
    from home_assistant_platform.config.settings import settings
    return {
        "voice_enabled": settings.voice_enabled,
        "wake_word": settings.wake_word,
        "stt_engine": settings.stt_engine,
        "tts_engine": settings.tts_engine,
        "openai_enabled": settings.openai_enabled,
        "conversation_mode": settings.conversation_mode
    }


@router.post("/settings")
async def update_voice_settings(request: Request, settings_req: VoiceSettingsRequest):
    """Update voice settings"""
    from home_assistant_platform.config.settings import settings
    
    # Update settings (in production, save to config file)
    if settings_req.voice_enabled is not None:
        settings.voice_enabled = settings_req.voice_enabled
    
    if settings_req.wake_word:
        settings.wake_word = settings_req.wake_word
        # Update wake word detector if voice manager exists
        if hasattr(request.app.state, 'voice_manager') and request.app.state.voice_manager.wake_word_detector:
            was_listening = request.app.state.voice_manager.is_listening
            request.app.state.voice_manager.wake_word_detector.wake_word = settings_req.wake_word
            logger.info(f"Wake word updated to: {settings_req.wake_word}")
            # Log current detector state for debugging
            logger.info(f"Wake word detector now has: {request.app.state.voice_manager.wake_word_detector.wake_word}")
            # Ensure listening continues if it was active
            logger.info(f"Listening status before update: {was_listening}")
            logger.info(f"Listening status after update: {request.app.state.voice_manager.is_listening}")
            logger.info(f"STT engine available: {request.app.state.voice_manager.stt is not None and request.app.state.voice_manager.stt.engine is not None}")
            if was_listening and not request.app.state.voice_manager.is_listening:
                logger.warning("Listening stopped after wake word update, restarting...")
                request.app.state.voice_manager._start_background_listening()
            elif was_listening:
                logger.info("✓ Listening continues after wake word update")
    
    # Track if engines actually changed
    stt_engine_changed = False
    tts_engine_changed = False
    
    if settings_req.stt_engine:
        if settings.stt_engine != settings_req.stt_engine:
            stt_engine_changed = True
            settings.stt_engine = settings_req.stt_engine
            logger.info(f"STT engine changed to: {settings_req.stt_engine}")
    
    if settings_req.tts_engine:
        if settings.tts_engine != settings_req.tts_engine:
            tts_engine_changed = True
            settings.tts_engine = settings_req.tts_engine
            logger.info(f"TTS engine changed to: {settings_req.tts_engine}")
    
    if settings_req.openai_api_key:
        settings.openai_api_key = settings_req.openai_api_key
        settings.openai_enabled = True
    
    if settings_req.openai_tts_voice:
        settings.openai_tts_voice = settings_req.openai_tts_voice
        # Update TTS engine if using OpenAI
        if hasattr(request.app.state, 'voice_manager') and request.app.state.voice_manager.tts:
            if hasattr(request.app.state.voice_manager.tts, 'openai_voice'):
                request.app.state.voice_manager.tts.openai_voice = settings_req.openai_tts_voice
                logger.info(f"OpenAI TTS voice updated to: {settings_req.openai_tts_voice}")
    
    if settings_req.conversation_mode is not None:
        settings.conversation_mode = settings_req.conversation_mode
        if hasattr(request.app.state, 'voice_manager'):
            request.app.state.voice_manager.conversation_mode = settings_req.conversation_mode
            logger.info(f"Conversation mode updated to: {settings_req.conversation_mode}")
    
    # Reinitialize voice manager ONLY if engine actually changed
    if stt_engine_changed or tts_engine_changed:
        logger.info("Engine changed, reinitializing voice manager...")
        if hasattr(request.app.state, 'voice_manager'):
            was_listening = request.app.state.voice_manager.is_listening
            request.app.state.voice_manager.cleanup()
            del request.app.state.voice_manager
            # Recreate voice manager and agent
            from home_assistant_platform.core.voice.voice_manager import VoiceManager
            from home_assistant_platform.core.voice.agent import Agent
            from home_assistant_platform.core.voice.tools.time_tool import TimeTool
            from home_assistant_platform.core.voice.tools.joke_tool import JokeTool
            from home_assistant_platform.core.voice.tools.weather_tool import WeatherTool
            from home_assistant_platform.core.voice.tools.alarm_tool import AlarmTool
            from home_assistant_platform.core.voice.tools.help_tool import HelpTool
            
            request.app.state.voice_manager = VoiceManager()
            
            # Reinitialize agent and tools
            request.app.state.agent = Agent()
            request.app.state.agent.register_tool(TimeTool())
            request.app.state.agent.register_tool(JokeTool())
            request.app.state.agent.register_tool(WeatherTool())
            request.app.state.agent.register_tool(AlarmTool())
            request.app.state.agent.register_tool(HelpTool(request.app.state.agent))
            
            # Restart listening if it was active
            if was_listening:
                def handle_intent(intent: dict):
                    logger.info(f"Intent detected: {intent}")
                    intent_type = intent.get("intent", "unknown")
                    text = intent.get("text", "")
                    entities = intent.get("entities", [])
                    
                    # Use agent to route to appropriate tool
                    response = request.app.state.agent.handle_request(intent_type, text, entities)
                    
                    if response:
                        logger.info(f"Agent response: {response}")
                        request.app.state.voice_manager.speak(response)
                    elif intent_type != "unknown":
                        logger.info(f"Routing intent {intent_type} to plugins")
                        request.app.state.voice_manager.speak(f"Got it. {text}")
                    else:
                        logger.debug(f"Unknown intent: {text}")
                        request.app.state.voice_manager.speak("I'm sorry, I didn't understand that. Try asking for the time, a joke, or say help for more options.")
                request.app.state.voice_manager.start_listening(handle_intent)
                logger.info("Voice listening restarted after engine change")
    
    return {"success": True, "message": "Voice settings updated"}


@router.post("/speak")
async def speak_text(request: Request, speak_req: SpeakRequest):
    """Speak text using TTS"""
    try:
        voice_manager = get_voice_manager(request)
        if not voice_manager.enabled:
            return {
                "success": False,
                "error": "Voice processing is not enabled",
                "message": "Please enable voice processing in settings"
            }
        
        success = voice_manager.speak(speak_req.text)
        
        if not success:
            return {
                "success": False,
                "error": "TTS engine not available or failed",
                "message": "Text-to-speech engine may not be properly initialized. Check logs for details."
            }
        
        return {"success": True, "message": "Text spoken successfully"}
    except Exception as e:
        logger.error(f"Error in speak endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred while trying to speak the text"
        }


@router.post("/process")
async def process_command(request: Request, command_data: dict):
    """Process a voice command (simulates voice input)"""
    voice_manager = get_voice_manager(request)
    text = command_data.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Process as if it came from voice input (includes wake word detection)
    voice_manager._process_voice_input(text)
    
    intent = voice_manager.process_command(text)
    return intent


@router.post("/listen/start")
async def start_listening(request: Request):
    """Start continuous voice listening"""
    voice_manager = get_voice_manager(request)
    
    def handle_intent(intent: dict):
        """Handle detected intents"""
        logger.info(f"Intent detected via API: {intent}")
    
    voice_manager.start_listening(handle_intent)
    return {"success": True, "message": "Voice listening started"}


@router.post("/listen/stop")
async def stop_listening(request: Request):
    """Stop continuous voice listening"""
    voice_manager = get_voice_manager(request)
    voice_manager.stop_listening()
    return {"success": True, "message": "Voice listening stopped"}


@router.get("/listen/status")
async def listening_status(request: Request):
    """Get listening status"""
    from home_assistant_platform.config.settings import settings
    voice_manager = get_voice_manager(request)
    return {
        "listening": voice_manager.is_listening,
        "enabled": voice_manager.enabled,
        "awake": voice_manager.is_awake,
        "wake_word": settings.wake_word
    }


@router.post("/test-wake-word")
async def test_wake_word(request: Request, test_data: dict):
    """Test wake word detection with acknowledgment"""
    voice_manager = get_voice_manager(request)
    text = test_data.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Process as voice input (will trigger acknowledgment if wake word detected)
    voice_manager._process_voice_input(text)
    
    return {
        "success": True,
        "message": "Wake word test completed",
        "wake_word_detected": voice_manager.wake_word_detector.detect(text) if voice_manager.wake_word_detector else False
    }

