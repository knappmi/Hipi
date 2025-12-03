"""Reminder scheduler - checks and triggers reminders"""

import logging
import asyncio
from datetime import datetime, timedelta
from home_assistant_platform.core.calendar.reminder_manager import ReminderManager

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Scheduler for checking and triggering reminders"""
    
    def __init__(self, reminder_manager: ReminderManager):
        self.reminder_manager = reminder_manager
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Reminder scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Reminder scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Check for reminders every minute
                self.reminder_manager.check_and_notify()
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in reminder scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(60)

