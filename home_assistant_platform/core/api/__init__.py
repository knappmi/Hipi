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

router = APIRouter()

# Include sub-routers
router.include_router(plugins_router, prefix="/plugins", tags=["plugins"])
router.include_router(marketplace_router, prefix="/marketplace", tags=["marketplace"])
router.include_router(licensing_router, prefix="/license", tags=["licensing"])
router.include_router(voice_router, prefix="/voice", tags=["voice"])
router.include_router(settings_router, prefix="/settings", tags=["settings"])
router.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])


@router.get("/status")
async def api_status():
    """API status endpoint"""
    return {"status": "ok", "message": "API is running"}
