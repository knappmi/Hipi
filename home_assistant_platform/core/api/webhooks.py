"""Webhook API endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class WebhookCreate(BaseModel):
    name: str
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    payload_template: Optional[str] = None
    secret: Optional[str] = None
    trigger_on_device_change: bool = False
    trigger_on_scene_activate: bool = False
    trigger_on_automation_run: bool = False
    trigger_on_voice_command: bool = False
    trigger_on_custom_event: bool = False
    custom_event_types: Optional[List[str]] = None
    enabled: bool = True
    timeout: int = 10
    retry_count: int = 3


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    payload_template: Optional[str] = None
    enabled: Optional[bool] = None
    timeout: Optional[int] = None
    retry_count: Optional[int] = None


@router.get("/webhooks")
async def list_webhooks(request: Request):
    """List all webhooks"""
    webhook_manager = request.app.state.webhook_manager
    webhooks = webhook_manager.list_webhooks()
    return [
        {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "method": w.method,
            "enabled": w.enabled,
            "triggers": {
                "device_change": w.trigger_on_device_change,
                "scene_activate": w.trigger_on_scene_activate,
                "automation_run": w.trigger_on_automation_run,
                "voice_command": w.trigger_on_voice_command,
                "custom_event": w.trigger_on_custom_event
            },
            "created_at": w.created_at.isoformat()
        }
        for w in webhooks
    ]


@router.post("/webhooks")
async def create_webhook(request: Request, webhook_data: WebhookCreate):
    """Create a new webhook"""
    webhook_manager = request.app.state.webhook_manager
    webhook = webhook_manager.create_webhook(
        name=webhook_data.name,
        url=webhook_data.url,
        method=webhook_data.method,
        headers=webhook_data.headers,
        payload_template=webhook_data.payload_template,
        secret=webhook_data.secret,
        trigger_on_device_change=webhook_data.trigger_on_device_change,
        trigger_on_scene_activate=webhook_data.trigger_on_scene_activate,
        trigger_on_automation_run=webhook_data.trigger_on_automation_run,
        trigger_on_voice_command=webhook_data.trigger_on_voice_command,
        trigger_on_custom_event=webhook_data.trigger_on_custom_event,
        custom_event_types=webhook_data.custom_event_types,
        enabled=webhook_data.enabled,
        timeout=webhook_data.timeout,
        retry_count=webhook_data.retry_count
    )
    return {
        "id": webhook.id,
        "name": webhook.name,
        "url": webhook.url,
        "created_at": webhook.created_at.isoformat()
    }


@router.get("/webhooks/{webhook_id}")
async def get_webhook(request: Request, webhook_id: int):
    """Get webhook details"""
    webhook_manager = request.app.state.webhook_manager
    webhook = webhook_manager.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {
        "id": webhook.id,
        "name": webhook.name,
        "url": webhook.url,
        "method": webhook.method,
        "headers": webhook.headers,
        "payload_template": webhook.payload_template,
        "enabled": webhook.enabled,
        "triggers": {
            "device_change": webhook.trigger_on_device_change,
            "scene_activate": webhook.trigger_on_scene_activate,
            "automation_run": webhook.trigger_on_automation_run,
            "voice_command": webhook.trigger_on_voice_command,
            "custom_event": webhook.trigger_on_custom_event,
            "custom_event_types": webhook.custom_event_types
        },
        "timeout": webhook.timeout,
        "retry_count": webhook.retry_count,
        "created_at": webhook.created_at.isoformat()
    }


@router.post("/webhooks/{webhook_id}/trigger")
async def trigger_webhook(
    request: Request,
    webhook_id: int,
    event_type: str,
    event_data: Dict[str, Any]
):
    """Manually trigger a webhook"""
    webhook_manager = request.app.state.webhook_manager
    success = await webhook_manager.trigger_webhook(webhook_id, event_type, event_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to trigger webhook")
    return {"success": True, "message": "Webhook triggered"}


@router.get("/webhooks/{webhook_id}/logs")
async def get_webhook_logs(request: Request, webhook_id: int, limit: int = 100):
    """Get webhook execution logs"""
    webhook_manager = request.app.state.webhook_manager
    logs = webhook_manager.get_webhook_logs(webhook_id, limit)
    return [
        {
            "id": log.id,
            "webhook_id": log.webhook_id,
            "url": log.url,
            "method": log.method,
            "response_status": log.response_status,
            "response_time_ms": log.response_time_ms,
            "success": log.success,
            "error_message": log.error_message,
            "triggered_by": log.triggered_by,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(request: Request, webhook_id: int):
    """Delete a webhook"""
    webhook_manager = request.app.state.webhook_manager
    success = webhook_manager.delete_webhook(webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"success": True, "message": "Webhook deleted"}

