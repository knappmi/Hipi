"""Reminder manager - handles reminders and notifications"""

import logging
import re
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Optional, Any
from dateutil import parser as date_parser
from home_assistant_platform.core.calendar.models import (
    Reminder, ReminderNotification, get_calendar_db
)

logger = logging.getLogger(__name__)


class ReminderManager:
    """Manages reminders and notifications"""
    
    def __init__(self):
        self.db = get_calendar_db()
        self.notification_callback: Optional[callable] = None
    
    def create_reminder(
        self,
        title: str,
        reminder_time: datetime,
        description: Optional[str] = None,
        recurrence_type: Optional[str] = None,
        recurrence_interval: int = 1,
        recurrence_end_date: Optional[datetime] = None,
        priority: str = "normal",
        voice_command: Optional[str] = None,
        user_id: str = "default"
    ) -> Reminder:
        """Create a reminder"""
        reminder = Reminder(
            title=title,
            description=description,
            reminder_time=reminder_time,
            recurrence_type=recurrence_type,
            recurrence_interval=recurrence_interval,
            recurrence_end_date=recurrence_end_date,
            priority=priority,
            voice_command=voice_command,
            user_id=user_id
        )
        
        self.db.add(reminder)
        self.db.commit()
        
        logger.info(f"Created reminder: {title} at {reminder_time}")
        return reminder
    
    def parse_reminder_from_text(self, text: str, user_id: str = "default") -> Optional[Reminder]:
        """Parse reminder from natural language text"""
        text_lower = text.lower()
        
        # Extract title (everything after "remind me to" or "reminder")
        title_match = re.search(r"(?:remind me to|reminder|remind me|set reminder for)\s+(.+?)(?:\s+at|\s+on|$)", text_lower)
        if not title_match:
            return None
        
        title = title_match.group(1).strip()
        
        # Extract time
        reminder_time = self._parse_time_from_text(text_lower)
        if not reminder_time:
            # Default to 1 hour from now if no time specified
            reminder_time = datetime.now() + timedelta(hours=1)
        
        # Extract recurrence
        recurrence_type = None
        if "daily" in text_lower or "every day" in text_lower:
            recurrence_type = "daily"
        elif "weekly" in text_lower or "every week" in text_lower:
            recurrence_type = "weekly"
        elif "monthly" in text_lower or "every month" in text_lower:
            recurrence_type = "monthly"
        elif "yearly" in text_lower or "every year" in text_lower:
            recurrence_type = "yearly"
        
        return self.create_reminder(
            title=title,
            reminder_time=reminder_time,
            recurrence_type=recurrence_type,
            voice_command=text,
            user_id=user_id
        )
    
    def _parse_time_from_text(self, text: str) -> Optional[datetime]:
        """Parse time from natural language"""
        now = datetime.now()
        
        # Try dateutil parser first
        try:
            parsed = date_parser.parse(text, default=now)
            if parsed != now or "today" in text.lower() or "tomorrow" in text.lower():
                return parsed
        except:
            pass
        
        # Parse common time patterns
        time_patterns = [
            (r"at (\d{1,2}):(\d{2})\s*(am|pm)?", self._parse_time_with_am_pm),
            (r"at (\d{1,2})\s*(am|pm)", self._parse_time_with_am_pm),
            (r"in (\d+)\s*(minute|hour|day|week)s?", self._parse_relative_time),
            (r"(\d+)\s*(minute|hour|day|week)s?\s+from now", self._parse_relative_time),
        ]
        
        for pattern, parser_func in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                result = parser_func(match, now)
                if result:
                    return result
        
        # Check for "today", "tomorrow"
        if "today" in text.lower():
            # Try to find time
            time_match = re.search(r"(\d{1,2}):?(\d{2})?\s*(am|pm)?", text.lower())
            if time_match:
                return self._parse_time_with_am_pm(time_match, now)
            return now.replace(hour=12, minute=0, second=0, microsecond=0)
        
        if "tomorrow" in text.lower():
            tomorrow = now + timedelta(days=1)
            time_match = re.search(r"(\d{1,2}):?(\d{2})?\s*(am|pm)?", text.lower())
            if time_match:
                return self._parse_time_with_am_pm(time_match, tomorrow)
            return tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
        
        return None
    
    def _parse_time_with_am_pm(self, match, base_date: datetime) -> datetime:
        """Parse time with AM/PM"""
        hour = int(match.group(1))
        minute = 0
        am_pm = None
        
        # Check if group 2 is a number (minute) or AM/PM
        if len(match.groups()) >= 2 and match.group(2):
            try:
                minute = int(match.group(2))
                if len(match.groups()) >= 3:
                    am_pm = match.group(3)
            except ValueError:
                # Group 2 is AM/PM, not a minute
                am_pm = match.group(2)
        elif len(match.groups()) >= 2:
            am_pm = match.group(2)
        
        if am_pm:
            if am_pm.lower() == "pm" and hour != 12:
                hour += 12
            elif am_pm.lower() == "am" and hour == 12:
                hour = 0
        elif hour < 7:  # Assume PM if hour is small and no AM/PM
            hour += 12
        
        return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _parse_relative_time(self, match, base_date: datetime) -> datetime:
        """Parse relative time (in X minutes/hours)"""
        amount = int(match.group(1))
        unit = match.group(2).lower()
        
        if unit.startswith("minute"):
            return base_date + timedelta(minutes=amount)
        elif unit.startswith("hour"):
            return base_date + timedelta(hours=amount)
        elif unit.startswith("day"):
            return base_date + timedelta(days=amount)
        elif unit.startswith("week"):
            return base_date + timedelta(weeks=amount)
        
        return base_date
    
    def get_reminders(
        self,
        user_id: str = "default",
        completed: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Reminder]:
        """Get reminders"""
        query = self.db.query(Reminder).filter(Reminder.user_id == user_id)
        
        if completed is not None:
            query = query.filter(Reminder.completed == completed)
        
        if start_date:
            query = query.filter(Reminder.reminder_time >= start_date)
        
        if end_date:
            query = query.filter(Reminder.reminder_time <= end_date)
        
        return query.order_by(Reminder.reminder_time).all()
    
    def get_upcoming_reminders(self, hours: int = 24, user_id: str = "default") -> List[Reminder]:
        """Get upcoming reminders"""
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        return self.get_reminders(
            user_id=user_id,
            completed=False,
            start_date=now,
            end_date=end_time
        )
    
    def complete_reminder(self, reminder_id: int, user_id: str = "default") -> bool:
        """Mark reminder as completed"""
        reminder = self.db.query(Reminder).filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        ).first()
        
        if reminder:
            reminder.completed = True
            reminder.completed_at = datetime.utcnow()
            self.db.commit()
            
            # Create next occurrence if recurring
            if reminder.recurrence_type and reminder.recurrence_type != "none":
                self._create_next_occurrence(reminder)
            
            logger.info(f"Completed reminder: {reminder_id}")
            return True
        return False
    
    def _create_next_occurrence(self, reminder: Reminder):
        """Create next occurrence for recurring reminder"""
        next_time = reminder.reminder_time
        
        if reminder.recurrence_type == "daily":
            next_time += timedelta(days=reminder.recurrence_interval)
        elif reminder.recurrence_type == "weekly":
            next_time += timedelta(weeks=reminder.recurrence_interval)
        elif reminder.recurrence_type == "monthly":
            # Add approximately 30 days
            next_time += timedelta(days=30 * reminder.recurrence_interval)
        elif reminder.recurrence_type == "yearly":
            next_time += timedelta(days=365 * reminder.recurrence_interval)
        
        # Check if we should create next occurrence
        if reminder.recurrence_end_date and next_time > reminder.recurrence_end_date:
            return
        
        if reminder.recurrence_count:
            # Count existing occurrences
            existing_count = self.db.query(Reminder).filter(
                Reminder.voice_command == reminder.voice_command,
                Reminder.user_id == reminder.user_id
            ).count()
            if existing_count >= reminder.recurrence_count:
                return
        
        # Create new reminder
        new_reminder = Reminder(
            title=reminder.title,
            description=reminder.description,
            reminder_time=next_time,
            recurrence_type=reminder.recurrence_type,
            recurrence_interval=reminder.recurrence_interval,
            recurrence_end_date=reminder.recurrence_end_date,
            recurrence_count=reminder.recurrence_count,
            priority=reminder.priority,
            voice_command=reminder.voice_command,
            user_id=reminder.user_id
        )
        
        self.db.add(new_reminder)
        self.db.commit()
        logger.info(f"Created next occurrence for reminder: {reminder.title}")
    
    def delete_reminder(self, reminder_id: int, user_id: str = "default") -> bool:
        """Delete a reminder"""
        reminder = self.db.query(Reminder).filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        ).first()
        
        if reminder:
            self.db.delete(reminder)
            self.db.commit()
            logger.info(f"Deleted reminder: {reminder_id}")
            return True
        return False
    
    def check_and_notify(self, user_id: str = "default"):
        """Check for reminders that need notification"""
        now = datetime.now()
        upcoming = self.get_upcoming_reminders(hours=1, user_id=user_id)
        
        for reminder in upcoming:
            # Check if notification already sent
            existing = self.db.query(ReminderNotification).filter(
                ReminderNotification.reminder_id == reminder.id,
                ReminderNotification.notification_time <= now,
                ReminderNotification.delivered == True
            ).first()
            
            if not existing and reminder.reminder_time <= now:
                # Create notification
                notification = ReminderNotification(
                    reminder_id=reminder.id,
                    notification_time=now,
                    notification_type="voice"
                )
                self.db.add(notification)
                self.db.commit()
                
                # Trigger callback if set
                if self.notification_callback:
                    self.notification_callback(reminder)
                
                logger.info(f"Notification sent for reminder: {reminder.title}")
    
    def set_notification_callback(self, callback: callable):
        """Set callback for notifications"""
        self.notification_callback = callback

