"""Settings API endpoints"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ResourceLimitsRequest(BaseModel):
    max_cpu: Optional[float] = None
    max_memory: Optional[str] = None


@router.get("/resources")
async def get_resource_limits(request: Request):
    """Get resource limits"""
    from home_assistant_platform.config.settings import settings
    return {
        "max_cpu": settings.plugin_max_cpu,
        "max_memory": settings.plugin_max_memory
    }


@router.post("/resources")
async def update_resource_limits(request: Request, limits: ResourceLimitsRequest):
    """Update resource limits"""
    from home_assistant_platform.config.settings import settings
    
    if limits.max_cpu is not None:
        if limits.max_cpu < 0.1 or limits.max_cpu > 1.0:
            raise HTTPException(status_code=400, detail="CPU limit must be between 0.1 and 1.0")
        settings.plugin_max_cpu = limits.max_cpu
    
    if limits.max_memory:
        settings.plugin_max_memory = limits.max_memory
    
    return {
        "success": True,
        "message": "Resource limits updated",
        "max_cpu": settings.plugin_max_cpu,
        "max_memory": settings.plugin_max_memory
    }

