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
        
        # Initialize automation system
        from home_assistant_platform.core.automation.pattern_learner import PatternLearner
        from home_assistant_platform.core.automation.suggestion_engine import SuggestionEngine
        from home_assistant_platform.core.automation.executor import AutomationExecutor
        from home_assistant_platform.core.automation.device_manager import MockDeviceManager
        from home_assistant_platform.core.automation.scheduler import AutomationScheduler
        
        app.state.license_validator = LicenseValidator()
        app.state.docker_manager = DockerManager()
        
        # Initialize automation components with unified device manager
        from home_assistant_platform.core.devices.unified_manager import UnifiedDeviceManager
        app.state.device_manager = UnifiedDeviceManager()
        app.state.pattern_learner = PatternLearner()
        app.state.suggestion_engine = SuggestionEngine()
        app.state.automation_executor = AutomationExecutor(app.state.device_manager)
        app.state.automation_scheduler = AutomationScheduler(app.state.automation_executor)
        
        # Start automation scheduler
        await app.state.automation_scheduler.start()
        logger.info("Automation system initialized")
        
        # Initialize scene manager
        from home_assistant_platform.core.automation.scene_manager import SceneManager
        app.state.scene_manager = SceneManager(app.state.device_manager)
        
        # Initialize enhanced automation manager
        from home_assistant_platform.core.automation.enhanced_automation import EnhancedAutomationManager
        app.state.enhanced_automation_manager = EnhancedAutomationManager(
            app.state.automation_executor,
            app.state.scene_manager
        )
        logger.info("Scene and enhanced automation system initialized")
        
        # Initialize calendar and reminder system
        from home_assistant_platform.core.calendar.calendar_manager import CalendarManager
        from home_assistant_platform.core.calendar.reminder_manager import ReminderManager
        from home_assistant_platform.core.calendar.scheduler import ReminderScheduler
        
        app.state.calendar_manager = CalendarManager()
        app.state.reminder_manager = ReminderManager()
        app.state.reminder_scheduler = ReminderScheduler(app.state.reminder_manager)
        
        # Set up reminder notifications callback
        def on_reminder_notification(reminder):
            """Handle reminder notification"""
            if hasattr(app.state, 'voice_manager'):
                message = f"Reminder: {reminder.title}"
                app.state.voice_manager.speak(message)
        
        app.state.reminder_manager.set_notification_callback(on_reminder_notification)
        
        # Start reminder scheduler
        await app.state.reminder_scheduler.start()
        logger.info("Calendar and reminder system initialized")
        
        # Initialize voice manager and start listening
        if settings.voice_enabled:
            from home_assistant_platform.core.voice.agent import Agent
            from home_assistant_platform.core.voice.tools.time_tool import TimeTool
            from home_assistant_platform.core.voice.tools.joke_tool import JokeTool
            from home_assistant_platform.core.voice.tools.weather_tool import WeatherTool
            from home_assistant_platform.core.voice.tools.alarm_tool import AlarmTool
            from home_assistant_platform.core.voice.tools.help_tool import HelpTool
            from home_assistant_platform.core.voice.tools.search_tool import SearchTool
            from home_assistant_platform.core.voice.tools.reminder_tool import ReminderTool
            from home_assistant_platform.core.voice.tools.scene_tool import SceneTool
            from home_assistant_platform.core.voice.tools.media_tool import MediaTool
            from home_assistant_platform.core.voice.tools.user_tool import UserTool
            from home_assistant_platform.core.voice.tools.energy_tool import EnergyTool
            
            app.state.voice_manager = VoiceManager()
            
            # Initialize media manager
            from home_assistant_platform.core.media.device_manager import MediaDeviceManager
            app.state.media_manager = MediaDeviceManager()
            
            # Initialize user manager
            from home_assistant_platform.core.users.user_manager import UserManager
            app.state.user_manager = UserManager()
            
            # Initialize voice recognition
            from home_assistant_platform.core.users.voice_recognition import VoiceRecognition
            app.state.voice_recognition = VoiceRecognition()
            
            # Initialize energy monitor
            from home_assistant_platform.core.energy.monitor import EnergyMonitor
            app.state.energy_monitor = EnergyMonitor()
            logger.info("Energy monitoring system initialized")
            
            # Initialize webhook manager
            from home_assistant_platform.core.webhooks.webhook_manager import WebhookManager
            from home_assistant_platform.core.webhooks.event_dispatcher import EventDispatcher
            app.state.webhook_manager = WebhookManager()
            await app.state.webhook_manager.initialize()
            app.state.event_dispatcher = EventDispatcher(app.state.webhook_manager)
            logger.info("Webhook system initialized")
            
            # Initialize script executor
            from home_assistant_platform.core.automation.script_executor import ScriptExecutor
            app.state.script_executor = ScriptExecutor()
            logger.info("Script executor initialized")
            
            # Initialize ML metrics tracker
            from home_assistant_platform.core.ml_metrics.tracker import ModelPerformanceTracker
            app.state.ml_tracker = ModelPerformanceTracker()
            logger.info("ML metrics tracker initialized")
            
            # Create default user if none exists
            if not app.state.user_manager.list_users():
                app.state.user_manager.create_user("default", display_name="Default User")
                app.state.user_manager.set_current_user(1)
                logger.info("Created default user")
            
            # Initialize natural agent with personality
            from home_assistant_platform.core.voice.natural_agent import NaturalAgent
            app.state.agent = NaturalAgent(app.state.user_manager)
            
            # Register tools
            app.state.agent.register_tool(TimeTool())
            app.state.agent.register_tool(JokeTool())
            app.state.agent.register_tool(WeatherTool())
            app.state.agent.register_tool(AlarmTool())
            app.state.agent.register_tool(SearchTool())
            app.state.agent.register_tool(ReminderTool(app.state.reminder_manager))
            app.state.agent.register_tool(SceneTool(app.state.scene_manager))
            app.state.agent.register_tool(MediaTool(app.state.media_manager))
            app.state.agent.register_tool(UserTool(app.state.user_manager))
            app.state.agent.register_tool(EnergyTool(app.state.energy_monitor))
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
    if hasattr(app.state, 'automation_scheduler'):
        await app.state.automation_scheduler.stop()
    if hasattr(app.state, 'reminder_scheduler'):
        await app.state.reminder_scheduler.stop()
    if hasattr(app.state, 'docker_manager'):
        await app.state.docker_manager.cleanup()
        
        # Cleanup webhook manager
        if hasattr(app.state, 'webhook_manager'):
            await app.state.webhook_manager.cleanup()


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

