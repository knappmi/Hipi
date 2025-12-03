"""Webhook manager - handles webhook execution"""

import logging
import asyncio
import aiohttp
import time
from typing import Dict, Optional, Any, List
from datetime import datetime
from jinja2 import Template
from home_assistant_platform.core.webhooks.models import Webhook, WebhookLog, get_webhooks_db

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manages webhook execution"""
    
    def __init__(self):
        self.db = get_webhooks_db()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup async session"""
        if self.session:
            await self.session.close()
    
    def create_webhook(
        self,
        name: str,
        url: str,
        method: str = "POST",
        headers: Optional[Dict] = None,
        payload_template: Optional[str] = None,
        secret: Optional[str] = None,
        trigger_on_device_change: bool = False,
        trigger_on_scene_activate: bool = False,
        trigger_on_automation_run: bool = False,
        trigger_on_voice_command: bool = False,
        trigger_on_custom_event: bool = False,
        custom_event_types: Optional[List[str]] = None,
        enabled: bool = True,
        timeout: int = 10,
        retry_count: int = 3,
        user_id: str = "default"
    ) -> Webhook:
        """Create a new webhook"""
        with self.db() as db:
            webhook = Webhook(
                name=name,
                url=url,
                method=method,
                headers=headers or {},
                payload_template=payload_template,
                secret=secret,
                trigger_on_device_change=trigger_on_device_change,
                trigger_on_scene_activate=trigger_on_scene_activate,
                trigger_on_automation_run=trigger_on_automation_run,
                trigger_on_voice_command=trigger_on_voice_command,
                trigger_on_custom_event=trigger_on_custom_event,
                custom_event_types=custom_event_types or [],
                enabled=enabled,
                timeout=timeout,
                retry_count=retry_count,
                user_id=user_id
            )
            db.add(webhook)
            db.commit()
            db.refresh(webhook)
            logger.info(f"Created webhook: {name} -> {url}")
            return webhook
    
    def list_webhooks(self, user_id: str = "default") -> List[Webhook]:
        """List all webhooks"""
        with self.db() as db:
            return db.query(Webhook).filter_by(user_id=user_id).all()
    
    def get_webhook(self, webhook_id: int, user_id: str = "default") -> Optional[Webhook]:
        """Get webhook by ID"""
        with self.db() as db:
            return db.query(Webhook).filter_by(id=webhook_id, user_id=user_id).first()
    
    async def trigger_webhook(
        self,
        webhook_id: int,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: str = "default"
    ) -> bool:
        """Trigger a webhook"""
        webhook = self.get_webhook(webhook_id, user_id)
        if not webhook or not webhook.enabled:
            return False
        
        # Check if webhook should be triggered for this event
        should_trigger = False
        if event_type == "device_change" and webhook.trigger_on_device_change:
            should_trigger = True
        elif event_type == "scene_activate" and webhook.trigger_on_scene_activate:
            should_trigger = True
        elif event_type == "automation_run" and webhook.trigger_on_automation_run:
            should_trigger = True
        elif event_type == "voice_command" and webhook.trigger_on_voice_command:
            should_trigger = True
        elif event_type in webhook.custom_event_types and webhook.trigger_on_custom_event:
            should_trigger = True
        
        if not should_trigger:
            return False
        
        # Execute webhook
        return await self._execute_webhook(webhook, event_type, event_data)
    
    async def _execute_webhook(
        self,
        webhook: Webhook,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Execute a webhook request"""
        if not self.session:
            await self.initialize()
        
        # Prepare payload
        payload = self._prepare_payload(webhook, event_type, event_data)
        
        # Prepare headers
        headers = webhook.headers.copy() if webhook.headers else {}
        headers.setdefault("Content-Type", "application/json")
        if webhook.secret:
            headers["X-Webhook-Secret"] = webhook.secret
        
        # Execute request with retries
        success = False
        error_message = None
        response_status = None
        response_body = None
        response_time_ms = 0
        
        for attempt in range(webhook.retry_count):
            try:
                start_time = time.time()
                
                async with self.session.request(
                    method=webhook.method,
                    url=webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=webhook.timeout)
                ) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    response_status = response.status
                    response_body = await response.text()
                    
                    if response.status < 400:
                        success = True
                        break
                    else:
                        error_message = f"HTTP {response.status}: {response_body[:200]}"
            
            except asyncio.TimeoutError:
                error_message = f"Timeout after {webhook.timeout}s"
            except Exception as e:
                error_message = str(e)
            
            if attempt < webhook.retry_count - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Log execution
        self._log_webhook(
            webhook,
            payload,
            headers,
            response_status,
            response_body,
            response_time_ms,
            success,
            error_message,
            event_type
        )
        
        return success
    
    def _prepare_payload(
        self,
        webhook: Webhook,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare webhook payload"""
        if webhook.payload_template:
            # Use Jinja2 template
            template = Template(webhook.payload_template)
            payload_str = template.render(
                event_type=event_type,
                event_data=event_data,
                timestamp=datetime.utcnow().isoformat()
            )
            import json
            return json.loads(payload_str)
        else:
            # Default payload
            return {
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
                "webhook_name": webhook.name
            }
    
    def _log_webhook(
        self,
        webhook: Webhook,
        request_payload: Dict,
        request_headers: Dict,
        response_status: Optional[int],
        response_body: Optional[str],
        response_time_ms: float,
        success: bool,
        error_message: Optional[str],
        triggered_by: str
    ):
        """Log webhook execution"""
        with self.db() as db:
            log = WebhookLog(
                webhook_id=webhook.id,
                url=webhook.url,
                method=webhook.method,
                request_payload=request_payload,
                request_headers=request_headers,
                response_status=response_status,
                response_body=response_body[:1000] if response_body else None,  # Limit size
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message,
                triggered_by=triggered_by
            )
            db.add(log)
            db.commit()
    
    def get_webhook_logs(
        self,
        webhook_id: Optional[int] = None,
        limit: int = 100,
        user_id: str = "default"
    ) -> List[WebhookLog]:
        """Get webhook execution logs"""
        with self.db() as db:
            query = db.query(WebhookLog)
            if webhook_id:
                query = query.filter_by(webhook_id=webhook_id)
            return query.order_by(WebhookLog.created_at.desc()).limit(limit).all()
    
    def delete_webhook(self, webhook_id: int, user_id: str = "default") -> bool:
        """Delete a webhook"""
        with self.db() as db:
            webhook = db.query(Webhook).filter_by(id=webhook_id, user_id=user_id).first()
            if not webhook:
                return False
            db.delete(webhook)
            db.commit()
            logger.info(f"Deleted webhook: {webhook.name}")
            return True

