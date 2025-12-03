"""Calendar manager - handles calendar operations"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from icalendar import Calendar as ICalendar, Event as IEvent
import requests
from home_assistant_platform.core.calendar.models import (
    Calendar, CalendarEvent, get_calendar_db
)

logger = logging.getLogger(__name__)


class CalendarManager:
    """Manages calendar operations"""
    
    def __init__(self):
        self.db = get_calendar_db()
    
    def create_calendar(
        self,
        name: str,
        source_type: str = "local",
        source_url: Optional[str] = None,
        credentials: Optional[Dict] = None,
        user_id: str = "default"
    ) -> Calendar:
        """Create a new calendar"""
        calendar = Calendar(
            name=name,
            source_type=source_type,
            source_url=source_url,
            credentials=credentials,
            user_id=user_id
        )
        
        self.db.add(calendar)
        self.db.commit()
        
        logger.info(f"Created calendar: {name} ({source_type})")
        return calendar
    
    def get_calendars(self, user_id: str = "default") -> List[Calendar]:
        """Get all calendars for a user"""
        return self.db.query(Calendar).filter(
            Calendar.user_id == user_id,
            Calendar.is_active == True
        ).all()
    
    def create_event(
        self,
        calendar_id: int,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        all_day: bool = False,
        recurrence_rule: Optional[str] = None,
        user_id: str = "default"
    ) -> CalendarEvent:
        """Create a calendar event"""
        event = CalendarEvent(
            calendar_id=calendar_id,
            title=title,
            description=description,
            location=location,
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
            recurrence_rule=recurrence_rule,
            user_id=user_id
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Created event: {title} at {start_time}")
        return event
    
    def get_events(
        self,
        calendar_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: str = "default"
    ) -> List[CalendarEvent]:
        """Get events from calendar(s)"""
        query = self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id
        )
        
        if calendar_id:
            query = query.filter(CalendarEvent.calendar_id == calendar_id)
        
        if start_date:
            query = query.filter(CalendarEvent.start_time >= start_date)
        
        if end_date:
            query = query.filter(CalendarEvent.start_time <= end_date)
        
        return query.order_by(CalendarEvent.start_time).all()
    
    def get_upcoming_events(self, days: int = 7, user_id: str = "default") -> List[CalendarEvent]:
        """Get upcoming events"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        return self.get_events(start_date=start_date, end_date=end_date, user_id=user_id)
    
    def sync_ical_calendar(self, calendar_id: int) -> bool:
        """Sync calendar from iCal URL"""
        calendar = self.db.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar or not calendar.source_url:
            return False
        
        try:
            # Fetch iCal data
            response = requests.get(calendar.source_url, timeout=10)
            response.raise_for_status()
            
            # Parse iCal
            ical = ICalendar.from_ical(response.text)
            
            # Extract events
            events_added = 0
            for component in ical.walk():
                if component.name == "VEVENT":
                    title = str(component.get('summary', ''))
                    start = component.get('dtstart')
                    end = component.get('dtend')
                    description = str(component.get('description', ''))
                    location = str(component.get('location', ''))
                    uid = str(component.get('uid', ''))
                    
                    if start and end:
                        start_dt = start.dt
                        end_dt = end.dt
                        
                        # Check if event already exists
                        existing = self.db.query(CalendarEvent).filter(
                            CalendarEvent.external_id == uid,
                            CalendarEvent.calendar_id == calendar_id
                        ).first()
                        
                        if not existing:
                            self.create_event(
                                calendar_id=calendar_id,
                                title=title,
                                start_time=start_dt,
                                end_time=end_dt,
                                description=description,
                                location=location,
                                external_id=uid
                            )
                            events_added += 1
            
            logger.info(f"Synced {events_added} events from iCal calendar {calendar_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing iCal calendar: {e}", exc_info=True)
            return False
    
    def delete_event(self, event_id: int, user_id: str = "default") -> bool:
        """Delete an event"""
        event = self.db.query(CalendarEvent).filter(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == user_id
        ).first()
        
        if event:
            self.db.delete(event)
            self.db.commit()
            logger.info(f"Deleted event: {event_id}")
            return True
        return False

