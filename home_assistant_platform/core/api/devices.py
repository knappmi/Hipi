"""Device control API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()


class DeviceControlRequest(BaseModel):
    action: str  # turn_on, turn_off, set_brightness, set_color, set_temperature
    value: Optional[Any] = None


class DeviceAddRequest(BaseModel):
    id: str
    name: str
    type: str
    state: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def get_device_manager(request: Request):
    """Get unified device manager from app state"""
    if hasattr(request.app.state, 'device_manager'):
        return request.app.state.device_manager
    else:
        from home_assistant_platform.core.devices.unified_manager import UnifiedDeviceManager
        request.app.state.device_manager = UnifiedDeviceManager()
        return request.app.state.device_manager


@router.get("")
async def list_devices(request: Request):
    """List all devices"""
    device_manager = get_device_manager(request)
    devices = device_manager.list_devices()
    return {"devices": devices, "count": len(devices)}


@router.get("/{device_id}")
async def get_device(request: Request, device_id: str):
    """Get device information"""
    device_manager = get_device_manager(request)
    device = await device_manager.get_device_state(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"device": device}


@router.post("/{device_id}/control")
async def control_device(request: Request, device_id: str, control_req: DeviceControlRequest):
    """Control a device"""
    device_manager = get_device_manager(request)
    
    # Verify device exists
    device = await device_manager.get_device_state(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    success = False
    action = control_req.action.lower()
    device_type = device.get("type", "unknown")
    
    if action == "turn_on":
        success = await device_manager.turn_on_device(device_id)
    elif action == "turn_off":
        success = await device_manager.turn_off_device(device_id)
    elif action == "set_brightness":
        if control_req.value is None:
            raise HTTPException(status_code=400, detail="Brightness value required")
        success = await device_manager.set_brightness(device_id, int(control_req.value))
    elif action == "set_color":
        if control_req.value is None:
            raise HTTPException(status_code=400, detail="Color value required")
        success = await device_manager.set_color(device_id, str(control_req.value))
    elif action == "set_temperature":
        if control_req.value is None:
            raise HTTPException(status_code=400, detail="Temperature value required")
        success = await device_manager.set_temperature(device_id, float(control_req.value))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    
    if success:
        # Record action for pattern learning
        if hasattr(request.app.state, 'pattern_learner'):
            value_str = str(control_req.value) if control_req.value is not None else None
            request.app.state.pattern_learner.record_action(
                device_id=device_id,
                device_type=device_type,
                action=action,
                value=value_str,
                user_id="default"
            )
        
        # Get updated state
        updated_state = await device_manager.get_device_state(device_id)
        previous_state = device.get("state", "unknown")
        new_state = updated_state.get("state", "unknown")
        
        # Trigger webhook event
        if hasattr(request.app.state, 'event_dispatcher') and previous_state != new_state:
            await request.app.state.event_dispatcher.device_changed(
                device_id=device_id,
                state=new_state,
                previous_state=previous_state,
                brightness=updated_state.get("brightness"),
                user_id="default"
            )
        
        return {
            "success": True,
            "message": f"Device {device_id} {action} executed",
            "device": updated_state
        }
    else:
        raise HTTPException(status_code=500, detail=f"Failed to execute {action} on device {device_id}")


@router.post("/{device_id}/turn_on")
async def turn_on_device(request: Request, device_id: str):
    """Turn on a device"""
    device_manager = get_device_manager(request)
    device = await device_manager.get_device_state(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    success = await device_manager.turn_on_device(device_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to turn on device")
    
    # Record action for pattern learning
    if hasattr(request.app.state, 'pattern_learner'):
        request.app.state.pattern_learner.record_action(
            device_id=device_id,
            device_type=device.get("type", "unknown"),
            action="turn_on",
            user_id="default"
        )
    
    state = await device_manager.get_device_state(device_id)
    return {"success": True, "device": state}


@router.post("/{device_id}/turn_off")
async def turn_off_device(request: Request, device_id: str):
    """Turn off a device"""
    device_manager = get_device_manager(request)
    device = await device_manager.get_device_state(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    success = await device_manager.turn_off_device(device_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to turn off device")
    
    # Record action for pattern learning
    if hasattr(request.app.state, 'pattern_learner'):
        request.app.state.pattern_learner.record_action(
            device_id=device_id,
            device_type=device.get("type", "unknown"),
            action="turn_off",
            user_id="default"
        )
    
    state = await device_manager.get_device_state(device_id)
    return {"success": True, "device": state}


@router.post("/discover")
async def discover_devices(request: Request):
    """Discover WiFi devices on the network"""
    device_manager = get_device_manager(request)
    
    if hasattr(device_manager, 'discover_wifi_devices'):
        devices = await device_manager.discover_wifi_devices()
        return {
            "success": True,
            "discovered": len(devices),
            "devices": devices
        }
    else:
        return {
            "success": False,
            "message": "WiFi device discovery not available"
        }


@router.post("/add")
async def add_device(request: Request, device_req: DeviceAddRequest):
    """Manually add a device"""
    device_manager = get_device_manager(request)
    
    if hasattr(device_manager, 'registry'):
        device = {
            "id": device_req.id,
            "name": device_req.name,
            "type": device_req.type,
            "state": device_req.state or "off",
            "source": "manual",
            **(device_req.metadata or {})
        }
        device_manager.registry.add_device(device, "manual")
        return {"success": True, "device": device}
    else:
        raise HTTPException(status_code=500, detail="Device registry not available")


@router.delete("/{device_id}")
async def remove_device(request: Request, device_id: str):
    """Remove a device"""
    device_manager = get_device_manager(request)
    
    if hasattr(device_manager, 'registry'):
        device_manager.registry.remove_device(device_id)
        return {"success": True, "message": f"Device {device_id} removed"}
    else:
        raise HTTPException(status_code=500, detail="Device registry not available")

