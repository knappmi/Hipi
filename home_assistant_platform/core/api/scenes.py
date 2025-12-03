"""Scenes and enhanced automation API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from home_assistant_platform.core.automation.scene_manager import SceneManager
from home_assistant_platform.core.automation.enhanced_automation import EnhancedAutomationManager

logger = logging.getLogger(__name__)
router = APIRouter()


class SceneCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    device_states: List[Dict[str, Any]]


class SceneUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    device_states: Optional[List[Dict[str, Any]]] = None


class SceneAutomationRequest(BaseModel):
    name: str
    scene_name: str
    trigger_type: str = "time"
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None


def get_scene_manager(request: Request) -> SceneManager:
    """Get scene manager from app state"""
    if not hasattr(request.app.state, 'scene_manager'):
        from home_assistant_platform.core.devices.unified_manager import UnifiedDeviceManager
        device_manager = request.app.state.device_manager if hasattr(request.app.state, 'device_manager') else UnifiedDeviceManager()
        request.app.state.scene_manager = SceneManager(device_manager)
    return request.app.state.scene_manager


def get_enhanced_automation_manager(request: Request) -> EnhancedAutomationManager:
    """Get enhanced automation manager from app state"""
    if not hasattr(request.app.state, 'enhanced_automation_manager'):
        from home_assistant_platform.core.automation.executor import AutomationExecutor
        automation_executor = request.app.state.automation_executor if hasattr(request.app.state, 'automation_executor') else None
        scene_manager = get_scene_manager(request)
        request.app.state.enhanced_automation_manager = EnhancedAutomationManager(automation_executor, scene_manager)
    return request.app.state.enhanced_automation_manager


@router.get("/scenes")
async def list_scenes(request: Request, user_id: str = "default"):
    """List all scenes"""
    manager = get_scene_manager(request)
    scenes = manager.list_scenes(user_id=user_id)
    
    return {
        "scenes": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "icon": s.icon,
                "device_count": len(s.device_states),
                "created_at": s.created_at.isoformat()
            }
            for s in scenes
        ]
    }


@router.get("/scenes/{scene_id}")
async def get_scene(request: Request, scene_id: int, user_id: str = "default"):
    """Get scene details"""
    manager = get_scene_manager(request)
    scene = manager.get_scene(scene_id, user_id=user_id)
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    return {
        "scene": {
            "id": scene.id,
            "name": scene.name,
            "description": scene.description,
            "icon": scene.icon,
            "device_states": scene.device_states,
            "created_at": scene.created_at.isoformat()
        }
    }


@router.post("/scenes")
async def create_scene(request: Request, scene_req: SceneCreateRequest, user_id: str = "default"):
    """Create a new scene"""
    manager = get_scene_manager(request)
    scene = manager.create_scene(
        name=scene_req.name,
        device_states=scene_req.device_states,
        description=scene_req.description,
        icon=scene_req.icon,
        user_id=user_id
    )
    
    return {
        "success": True,
        "scene": {
            "id": scene.id,
            "name": scene.name,
            "device_states": scene.device_states
        }
    }


@router.post("/scenes/{scene_id}/activate")
async def activate_scene(request: Request, scene_id: int, user_id: str = "default"):
    """Activate a scene"""
    manager = get_scene_manager(request)
    success = await manager.activate_scene(scene_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Scene not found or failed to activate")
    
    scene = manager.get_scene(scene_id, user_id=user_id)
    
    # Trigger webhook event
    if hasattr(request.app.state, 'event_dispatcher') and scene:
        await request.app.state.event_dispatcher.scene_activated(
            scene_id=scene_id,
            scene_name=scene.name,
            user_id=user_id
        )
    
    return {
        "success": True,
        "message": f"Scene '{scene.name}' activated",
        "scene": {
            "id": scene.id,
            "name": scene.name
        }
    }


@router.post("/scenes/activate/{scene_name}")
async def activate_scene_by_name(request: Request, scene_name: str, user_id: str = "default"):
    """Activate a scene by name"""
    manager = get_scene_manager(request)
    success = await manager.activate_scene_by_name(scene_name, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Scene '{scene_name}' not found")
    
    scene = manager.get_scene_by_name(scene_name, user_id=user_id)
    
    # Trigger webhook event
    if hasattr(request.app.state, 'event_dispatcher') and scene:
        await request.app.state.event_dispatcher.scene_activated(
            scene_id=scene.id,
            scene_name=scene.name,
            user_id=user_id
        )
    
    return {
        "success": True,
        "message": f"Scene '{scene.name}' activated",
        "scene": {
            "id": scene.id,
            "name": scene.name
        }
    }


@router.put("/scenes/{scene_id}")
async def update_scene(request: Request, scene_id: int, scene_req: SceneUpdateRequest, user_id: str = "default"):
    """Update a scene"""
    manager = get_scene_manager(request)
    success = manager.update_scene(
        scene_id=scene_id,
        name=scene_req.name,
        device_states=scene_req.device_states,
        description=scene_req.description,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    return {"success": True, "message": "Scene updated"}


@router.delete("/scenes/{scene_id}")
async def delete_scene(request: Request, scene_id: int, user_id: str = "default"):
    """Delete a scene"""
    manager = get_scene_manager(request)
    success = manager.delete_scene(scene_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    return {"success": True, "message": "Scene deleted"}


@router.post("/automations/scene")
async def create_scene_automation(request: Request, automation_req: SceneAutomationRequest, user_id: str = "default"):
    """Create automation that activates a scene"""
    manager = get_enhanced_automation_manager(request)
    automation = manager.create_scene_automation(
        name=automation_req.name,
        scene_name=automation_req.scene_name,
        trigger_type=automation_req.trigger_type,
        trigger_config=automation_req.trigger_config,
        conditions=automation_req.conditions,
        user_id=user_id
    )
    
    if not automation:
        raise HTTPException(status_code=400, detail="Failed to create scene automation")
    
    return {
        "success": True,
        "automation": {
            "id": automation.id,
            "name": automation.name,
            "scene_name": automation_req.scene_name
        }
    }


@router.post("/automations/{automation_id}/enable")
async def enable_automation(request: Request, automation_id: int, user_id: str = "default"):
    """Enable an automation"""
    manager = get_enhanced_automation_manager(request)
    success = manager.enable_automation(automation_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    return {"success": True, "message": "Automation enabled"}


@router.post("/automations/{automation_id}/disable")
async def disable_automation(request: Request, automation_id: int, user_id: str = "default"):
    """Disable an automation"""
    manager = get_enhanced_automation_manager(request)
    success = manager.disable_automation(automation_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    return {"success": True, "message": "Automation disabled"}

