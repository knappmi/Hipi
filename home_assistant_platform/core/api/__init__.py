"""REST API routes"""

from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from home_assistant_platform.core.api.plugins import router as plugins_router
from home_assistant_platform.core.api.marketplace import router as marketplace_router
from home_assistant_platform.core.api.licensing import router as licensing_router
from home_assistant_platform.core.api.voice import router as voice_router
from home_assistant_platform.core.api.settings import router as settings_router
from home_assistant_platform.core.api.telemetry import router as telemetry_router
from home_assistant_platform.core.api.automation import router as automation_router
from home_assistant_platform.core.api.devices import router as devices_router
from home_assistant_platform.core.api.calendar import router as calendar_router
from home_assistant_platform.core.api.scenes import router as scenes_router
from home_assistant_platform.core.api.media import router as media_router
from home_assistant_platform.core.api.users import router as users_router
from home_assistant_platform.core.api.energy import router as energy_router
from home_assistant_platform.core.api.webhooks import router as webhooks_router
from home_assistant_platform.core.api.automation_advanced import router as automation_advanced_router
from home_assistant_platform.core.api.onboarding import router as onboarding_router
from home_assistant_platform.core.api.ml_metrics import router as ml_metrics_router

router = APIRouter()

# Include sub-routers
router.include_router(plugins_router, prefix="/plugins", tags=["plugins"])
router.include_router(marketplace_router, prefix="/marketplace", tags=["marketplace"])
router.include_router(licensing_router, prefix="/license", tags=["licensing"])
router.include_router(voice_router, prefix="/voice", tags=["voice"])
router.include_router(settings_router, prefix="/settings", tags=["settings"])
router.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])
router.include_router(automation_router, prefix="/automation", tags=["automation"])
router.include_router(devices_router, prefix="/devices", tags=["devices"])
router.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
router.include_router(scenes_router, prefix="/scenes", tags=["scenes"])
router.include_router(media_router, prefix="/media", tags=["media"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(energy_router, prefix="/energy", tags=["energy"])
router.include_router(webhooks_router, prefix="", tags=["webhooks"])
router.include_router(automation_advanced_router, prefix="", tags=["automation-advanced"])
router.include_router(onboarding_router, prefix="", tags=["onboarding"])
router.include_router(ml_metrics_router, prefix="", tags=["ml-metrics"])


@router.get("/status")
async def api_status():
    """API status endpoint"""
    return {"status": "ok", "message": "API is running"}
