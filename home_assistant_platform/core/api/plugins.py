"""Plugin management API endpoints"""

from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from typing import List, Dict, Optional
from pydantic import BaseModel

router = APIRouter()


def get_plugin_manager(request: Request):
    """Get plugin manager from app state"""
    if not hasattr(request.app.state, 'plugin_manager'):
        from home_assistant_platform.core.plugin_manager.plugin_manager import PluginManager
        from home_assistant_platform.core.plugin_manager.docker_manager import DockerManager
        docker_manager = request.app.state.docker_manager
        request.app.state.plugin_manager = PluginManager(docker_manager)
    return request.app.state.plugin_manager


@router.get("")
async def list_plugins(request: Request):
    """List all installed plugins"""
    plugin_manager = get_plugin_manager(request)
    plugins = plugin_manager.list_plugins()
    return plugins


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str, request: Request):
    """Get plugin details"""
    plugin_manager = get_plugin_manager(request)
    plugin = plugin_manager.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    status = await plugin_manager.get_plugin_status(plugin_id)
    return status


@router.post("/{plugin_id}/start")
async def start_plugin(plugin_id: str, request: Request):
    """Start a plugin"""
    plugin_manager = get_plugin_manager(request)
    success = plugin_manager.start_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start plugin")
    return {"success": True, "message": f"Plugin {plugin_id} started"}


@router.post("/{plugin_id}/stop")
async def stop_plugin(plugin_id: str, request: Request):
    """Stop a plugin"""
    plugin_manager = get_plugin_manager(request)
    success = plugin_manager.stop_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop plugin")
    return {"success": True, "message": f"Plugin {plugin_id} stopped"}


@router.post("/{plugin_id}/restart")
async def restart_plugin(plugin_id: str, request: Request):
    """Restart a plugin"""
    plugin_manager = get_plugin_manager(request)
    success = plugin_manager.restart_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to restart plugin")
    return {"success": True, "message": f"Plugin {plugin_id} restarted"}


@router.delete("/{plugin_id}")
async def uninstall_plugin(plugin_id: str, request: Request):
    """Uninstall a plugin"""
    plugin_manager = get_plugin_manager(request)
    success = plugin_manager.uninstall_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to uninstall plugin")
    return {"success": True, "message": f"Plugin {plugin_id} uninstalled"}


@router.get("/{plugin_id}/logs")
async def get_plugin_logs(plugin_id: str, request: Request, tail: int = 100):
    """Get plugin container logs"""
    docker_manager = request.app.state.docker_manager
    logs = docker_manager.get_container_logs(plugin_id, tail)
    return {"logs": logs}


@router.post("/{plugin_id}/command")
async def execute_plugin_command(plugin_id: str, request: Request, command_data: Dict):
    """Execute a command on a plugin"""
    plugin_manager = get_plugin_manager(request)
    command = command_data.get("command")
    params = command_data.get("params", {})
    
    result = await plugin_manager.execute_plugin_command(plugin_id, command, params)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to execute command")
    return result

