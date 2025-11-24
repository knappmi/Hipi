"""Main application entry point"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from home_assistant_platform.config.settings import settings
from home_assistant_platform.config.logging_config import setup_logging
from home_assistant_platform.core.api import router as api_router

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.platform_name} v{settings.platform_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize components
    try:
        # Import and initialize components here
        from home_assistant_platform.core.licensing.license_validator import LicenseValidator
        from home_assistant_platform.core.plugin_manager.docker_manager import DockerManager
        from home_assistant_platform.core.voice.voice_manager import VoiceManager
        
        app.state.license_validator = LicenseValidator()
        app.state.docker_manager = DockerManager()
        
        # Initialize voice manager and start listening
        if settings.voice_enabled:
            from home_assistant_platform.core.voice.agent import Agent
            from home_assistant_platform.core.voice.tools.time_tool import TimeTool
            from home_assistant_platform.core.voice.tools.joke_tool import JokeTool
            from home_assistant_platform.core.voice.tools.weather_tool import WeatherTool
            from home_assistant_platform.core.voice.tools.alarm_tool import AlarmTool
            from home_assistant_platform.core.voice.tools.help_tool import HelpTool
            
            app.state.voice_manager = VoiceManager()
            
            # Initialize agent and register tools
            app.state.agent = Agent()
            app.state.agent.register_tool(TimeTool())
            app.state.agent.register_tool(JokeTool())
            app.state.agent.register_tool(WeatherTool())
            app.state.agent.register_tool(AlarmTool())
            app.state.agent.register_tool(HelpTool(app.state.agent))
            
            logger.info(f"Agent initialized with {len(app.state.agent.tools)} tools")
            
            # Start continuous listening with intent handler
            def handle_intent(intent: dict):
                """Handle detected intents using agentic system"""
                logger.info(f"Intent detected: {intent}")
                intent_type = intent.get("intent", "unknown")
                text = intent.get("text", "")
                entities = intent.get("entities", [])
                
                # Use agent to route to appropriate tool
                response = app.state.agent.handle_request(intent_type, text, entities)
                
                if response:
                    # Tool handled the request
                    logger.info(f"Agent response: {response}")
                    app.state.voice_manager.speak(response)
                elif intent_type != "unknown":
                    # Known intent but no tool - route to plugins
                    logger.info(f"Routing intent {intent_type} to plugins")
                    app.state.voice_manager.speak(f"Got it. {text}")
                else:
                    # Unknown intent
                    logger.debug(f"Unknown intent: {text}")
                    app.state.voice_manager.speak("I'm sorry, I didn't understand that. Try asking for the time, a joke, or say help for more options.")
            
            app.state.voice_manager.start_listening(handle_intent)
            logger.info("Voice listening started")
        
        logger.info("Platform initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize platform: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down platform")
    if hasattr(app.state, 'voice_manager'):
        app.state.voice_manager.stop_listening()
        app.state.voice_manager.cleanup()
    if hasattr(app.state, 'docker_manager'):
        await app.state.docker_manager.cleanup()


# Create FastAPI application
app = FastAPI(
    title=settings.platform_name,
    version=settings.platform_version,
    description="Developer-friendly Home Assistant alternative for Raspberry Pi",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.platform_name,
        "version": settings.platform_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.platform_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "home_assistant_platform.core.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

