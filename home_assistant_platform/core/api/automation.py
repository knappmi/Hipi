"""Automation API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from home_assistant_platform.core.automation.pattern_learner import PatternLearner
from home_assistant_platform.core.automation.suggestion_engine import SuggestionEngine
from home_assistant_platform.core.automation.executor import AutomationExecutor
from home_assistant_platform.core.automation.device_manager import MockDeviceManager
from home_assistant_platform.core.automation.models import (
    Pattern, Automation, AutomationSuggestion, get_automation_db
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Global instances (will be initialized in main.py)
pattern_learner: Optional[PatternLearner] = None
suggestion_engine: Optional[SuggestionEngine] = None
automation_executor: Optional[AutomationExecutor] = None
device_manager: Optional[MockDeviceManager] = None


def get_automation_components(request: Request):
    """Get automation components from app state"""
    global pattern_learner, suggestion_engine, automation_executor, device_manager
    
    if not pattern_learner:
        if hasattr(request.app.state, 'pattern_learner'):
            pattern_learner = request.app.state.pattern_learner
        else:
            pattern_learner = PatternLearner()
    
    if not suggestion_engine:
        if hasattr(request.app.state, 'suggestion_engine'):
            suggestion_engine = request.app.state.suggestion_engine
        else:
            suggestion_engine = SuggestionEngine()
    
    if not automation_executor:
        if hasattr(request.app.state, 'automation_executor'):
            automation_executor = request.app.state.automation_executor
        else:
            device_manager = MockDeviceManager()
            automation_executor = AutomationExecutor(device_manager)
    
    if not device_manager:
        if hasattr(request.app.state, 'device_manager'):
            device_manager = request.app.state.device_manager
        else:
            device_manager = MockDeviceManager()
    
    return pattern_learner, suggestion_engine, automation_executor, device_manager


class DeviceActionRequest(BaseModel):
    device_id: str
    device_type: str
    action: str
    value: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_id: str = "default"


class AutomationCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    conditions: Optional[Dict[str, Any]] = None


@router.post("/actions/record")
async def record_action(request: Request, action_req: DeviceActionRequest):
    """Record a device action for pattern learning"""
    pattern_learner, _, _, _ = get_automation_components(request)
    
    pattern_learner.record_action(
        device_id=action_req.device_id,
        device_type=action_req.device_type,
        action=action_req.action,
        value=action_req.value,
        context=action_req.context,
        user_id=action_req.user_id
    )
    
    return {"success": True, "message": "Action recorded"}


@router.get("/patterns")
async def get_patterns(request: Request, device_id: Optional[str] = None, user_id: str = "default"):
    """Get detected patterns"""
    pattern_learner, _, _, _ = get_automation_components(request)
    
    patterns = pattern_learner.get_patterns(device_id=device_id, user_id=user_id)
    
    return {
        "patterns": [
            {
                "id": p.id,
                "device_id": p.device_id,
                "device_type": p.device_type,
                "action": p.action,
                "pattern_type": p.pattern_type,
                "conditions": p.conditions,
                "confidence": p.confidence,
                "occurrence_count": p.occurrence_count,
                "last_occurrence": p.last_occurrence.isoformat() if p.last_occurrence else None
            }
            for p in patterns
        ]
    }


@router.get("/suggestions")
async def get_suggestions(request: Request, user_id: str = "default"):
    """Get automation suggestions"""
    _, suggestion_engine, _, _ = get_automation_components(request)
    
    suggestions = suggestion_engine.get_pending_suggestions(user_id=user_id)
    
    return {
        "suggestions": [
            {
                "id": s.id,
                "pattern_id": s.pattern_id,
                "suggestion_text": s.suggestion_text,
                "automation_name": s.automation_name,
                "automation_config": s.automation_config,
                "created_at": s.created_at.isoformat()
            }
            for s in suggestions
        ]
    }


@router.post("/suggestions/{suggestion_id}/accept")
async def accept_suggestion(request: Request, suggestion_id: int, user_id: str = "default"):
    """Accept an automation suggestion"""
    _, suggestion_engine, automation_executor, _ = get_automation_components(request)
    
    success = suggestion_engine.accept_suggestion(suggestion_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Create automation from suggestion
    automation = automation_executor.create_automation_from_suggestion(suggestion_id, user_id)
    
    if automation:
        return {
            "success": True,
            "message": "Suggestion accepted and automation created",
            "automation_id": automation.id
        }
    else:
        return {
            "success": False,
            "message": "Suggestion accepted but failed to create automation"
        }


@router.post("/suggestions/{suggestion_id}/reject")
async def reject_suggestion(request: Request, suggestion_id: int, user_id: str = "default"):
    """Reject an automation suggestion"""
    _, suggestion_engine, _, _ = get_automation_components(request)
    
    success = suggestion_engine.reject_suggestion(suggestion_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return {"success": True, "message": "Suggestion rejected"}


@router.get("/automations")
async def list_automations(request: Request, user_id: str = "default"):
    """List all automations"""
    db = get_automation_db()
    
    automations = db.query(Automation).filter(
        Automation.user_id == user_id
    ).all()
    
    return {
        "automations": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "trigger_type": a.trigger_type,
                "trigger_config": a.trigger_config,
                "actions": a.actions,
                "is_enabled": a.is_enabled,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat()
            }
            for a in automations
        ]
    }


@router.post("/automations")
async def create_automation(request: Request, automation_req: AutomationCreateRequest, user_id: str = "default"):
    """Create a new automation"""
    db = get_automation_db()
    
    automation = Automation(
        name=automation_req.name,
        description=automation_req.description,
        trigger_type=automation_req.trigger_type,
        trigger_config=automation_req.trigger_config,
        actions=automation_req.actions,
        conditions=automation_req.conditions,
        user_id=user_id,
        is_enabled=True,
        is_active=True
    )
    
    db.add(automation)
    db.commit()
    
    return {
        "success": True,
        "message": "Automation created",
        "automation_id": automation.id
    }


@router.post("/automations/{automation_id}/execute")
async def execute_automation(request: Request, automation_id: int):
    """Manually execute an automation"""
    _, _, automation_executor, _ = get_automation_components(request)
    
    success = await automation_executor.execute_automation(automation_id)
    
    return {"success": success, "message": "Automation executed" if success else "Failed to execute automation"}


@router.get("/devices")
async def list_devices(request: Request):
    """List all devices"""
    _, _, _, device_manager = get_automation_components(request)
    
    devices = device_manager.list_devices()
    return {"devices": devices}


@router.post("/devices/{device_id}/actions")
async def execute_device_action(
    request: Request,
    device_id: str,
    action: str,
    value: Optional[str] = None
):
    """Execute a device action and record it for pattern learning"""
    pattern_learner, _, automation_executor, device_manager = get_automation_components(request)
    
    # Get device info
    device_state = await device_manager.get_device_state(device_id)
    if not device_state:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_type = device_state.get("type", "unknown")
    
    # Execute action
    success = False
    if action == "turn_on":
        success = await device_manager.turn_on_device(device_id)
    elif action == "turn_off":
        success = await device_manager.turn_off_device(device_id)
    elif action == "set_temperature" and value:
        success = await device_manager.set_temperature(device_id, float(value))
    elif action == "set_brightness" and value:
        success = await device_manager.set_brightness(device_id, int(value))
    
    if success:
        # Record action for pattern learning
        pattern_learner.record_action(
            device_id=device_id,
            device_type=device_type,
            action=action,
            value=value,
            user_id="default"
        )
        
        # Check for new suggestions
        _, suggestion_engine, _, _ = get_automation_components(request)
        patterns = pattern_learner.get_patterns(device_id=device_id, min_confidence=0.6)
        for pattern in patterns:
            suggestion_engine.generate_suggestions(pattern)
    
    return {"success": success, "message": f"Action {action} executed" if success else "Failed to execute action"}

