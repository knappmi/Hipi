"""Event dispatcher for webhook triggers"""

import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class EventDispatcher:
    """Dispatches events to webhooks"""
    
    def __init__(self, webhook_manager=None):
        self.webhook_manager = webhook_manager
        self._pending_tasks = []
    
    async def dispatch_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: str = "default"
    ):
        """Dispatch an event to all relevant webhooks"""
        if not self.webhook_manager:
            return
        
        # Get all webhooks
        webhooks = self.webhook_manager.list_webhooks(user_id)
        
        # Trigger relevant webhooks asynchronously
        for webhook in webhooks:
            if webhook.enabled:
                task = asyncio.create_task(
                    self.webhook_manager.trigger_webhook(
                        webhook.id,
                        event_type,
                        event_data,
                        user_id
                    )
                )
                self._pending_tasks.append(task)
        
        # Clean up completed tasks
        self._pending_tasks = [t for t in self._pending_tasks if not t.done()]
    
    async def device_changed(
        self,
        device_id: str,
        state: str,
        previous_state: Optional[str] = None,
        brightness: Optional[int] = None,
        user_id: str = "default"
    ):
        """Dispatch device change event"""
        await self.dispatch_event(
            "device_change",
            {
                "device_id": device_id,
                "state": state,
                "previous_state": previous_state,
                "brightness": brightness
            },
            user_id
        )
    
    async def scene_activated(
        self,
        scene_id: int,
        scene_name: str,
        user_id: str = "default"
    ):
        """Dispatch scene activation event"""
        await self.dispatch_event(
            "scene_activate",
            {
                "scene_id": scene_id,
                "scene_name": scene_name
            },
            user_id
        )
    
    async def automation_run(
        self,
        automation_id: int,
        automation_name: str,
        result: str,
        user_id: str = "default"
    ):
        """Dispatch automation execution event"""
        await self.dispatch_event(
            "automation_run",
            {
                "automation_id": automation_id,
                "automation_name": automation_name,
                "result": result
            },
            user_id
        )
    
    async def voice_command(
        self,
        command: str,
        intent: str,
        response: str,
        user_id: str = "default"
    ):
        """Dispatch voice command event"""
        await self.dispatch_event(
            "voice_command",
            {
                "command": command,
                "intent": intent,
                "response": response
            },
            user_id
        )
    
    async def custom_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: str = "default"
    ):
        """Dispatch custom event"""
        await self.dispatch_event(event_type, event_data, user_id)

