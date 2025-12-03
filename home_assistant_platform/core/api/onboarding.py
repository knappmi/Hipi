"""Onboarding API endpoints"""

import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()


class OnboardingStep(BaseModel):
    step_id: str
    completed: bool
    data: Optional[Dict[str, Any]] = None


@router.get("/onboarding/status")
async def get_onboarding_status(request: Request):
    """Get onboarding status"""
    # Check if user has completed onboarding
    # This would check user preferences or database
    return {
        "completed": False,
        "current_step": "welcome",
        "steps": [
            {"id": "welcome", "title": "Welcome", "completed": False},
            {"id": "device_discovery", "title": "Discover Devices", "completed": False},
            {"id": "voice_setup", "title": "Voice Setup", "completed": False},
            {"id": "first_scene", "title": "Create First Scene", "completed": False},
            {"id": "complete", "title": "Complete", "completed": False}
        ]
    }


@router.post("/onboarding/complete-step")
async def complete_onboarding_step(request: Request, step: OnboardingStep):
    """Mark onboarding step as complete"""
    # Save onboarding progress
    return {"success": True, "message": f"Step {step.step_id} completed"}


@router.post("/onboarding/skip")
async def skip_onboarding(request: Request):
    """Skip onboarding"""
    return {"success": True, "message": "Onboarding skipped"}

