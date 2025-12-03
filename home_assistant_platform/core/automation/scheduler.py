"""Automation scheduler - handles time-based automation triggers"""

import logging
import asyncio
from datetime import datetime, time
from typing import List, Dict, Optional
from home_assistant_platform.core.automation.models import Automation, get_automation_db
from home_assistant_platform.core.automation.executor import AutomationExecutor

logger = logging.getLogger(__name__)


class AutomationScheduler:
    """Schedules and triggers time-based automations"""
    
    def __init__(self, executor: AutomationExecutor):
        self.executor = executor
        self.db = get_automation_db()
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Automation scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Automation scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_and_trigger_automations()
                # Check every minute
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _check_and_trigger_automations(self):
        """Check for automations that should be triggered"""
        try:
            now = datetime.now()
            current_time = now.time()
            current_day = now.weekday()
            
            # Get all enabled time-based automations
            automations = self.db.query(Automation).filter(
                Automation.is_enabled == True,
                Automation.is_active == True,
                Automation.trigger_type == "time"
            ).all()
            
            for automation in automations:
                trigger_config = automation.trigger_config or {}
                
                # Check time match (within 1 minute window)
                trigger_time_str = trigger_config.get("time")
                if trigger_time_str:
                    trigger_time = time.fromisoformat(trigger_time_str)
                    time_diff = abs(
                        (current_time.hour * 60 + current_time.minute) -
                        (trigger_time.hour * 60 + trigger_time.minute)
                    )
                    
                    if time_diff <= 1:  # Within 1 minute
                        # Check day of week
                        days_of_week = trigger_config.get("days_of_week", [])
                        if not days_of_week or current_day in days_of_week:
                            # Trigger automation
                            logger.info(f"Triggering automation: {automation.name}")
                            await self.executor.execute_automation(
                                automation.id,
                                trigger_data={
                                    "triggered_at": now.isoformat(),
                                    "trigger_type": "time"
                                }
                            )
        
        except Exception as e:
            logger.error(f"Error checking automations: {e}", exc_info=True)

