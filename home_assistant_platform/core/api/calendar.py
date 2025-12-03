"""Calendar and reminder API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from home_assistant_platform.core.calendar.calendar_manager import CalendarManager
from home_assistant_platform.core.calendar.reminder_manager import ReminderManager

logger = logging.getLogger(__name__)
router = APIRouter()


class CalendarCreateRequest(BaseModel):
    name: str
    source_type: str = "local"  # local, google, ical
    source_url: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None


class EventCreateRequest(BaseModel):
    calendar_id: int
    title: str
    start_time: str  # ISO format
    end_time: str  # ISO format
    description: Optional[str] = None
    location: Optional[str] = None
    all_day: bool = False
    recurrence_rule: Optional[str] = None


class ReminderCreateRequest(BaseModel):
    title: str
    reminder_time: str  # ISO format
    description: Optional[str] = None
    recurrence_type: Optional[str] = None  # daily, weekly, monthly, yearly
    recurrence_interval: int = 1
    priority: str = "normal"


class ReminderVoiceRequest(BaseModel):
    text: str  # Natural language reminder text


def get_calendar_manager(request: Request) -> CalendarManager:
    """Get calendar manager from app state"""
    if not hasattr(request.app.state, 'calendar_manager'):
        request.app.state.calendar_manager = CalendarManager()
    return request.app.state.calendar_manager


def get_reminder_manager(request: Request) -> ReminderManager:
    """Get reminder manager from app state"""
    if not hasattr(request.app.state, 'reminder_manager'):
        request.app.state.reminder_manager = ReminderManager()
    return request.app.state.reminder_manager


# Calendar endpoints
@router.get("/calendars")
async def list_calendars(request: Request, user_id: str = "default"):
    """List all calendars"""
    manager = get_calendar_manager(request)
    calendars = manager.get_calendars(user_id=user_id)
    
    return {
        "calendars": [
            {
                "id": c.id,
                "name": c.name,
                "source_type": c.source_type,
                "color": c.color,
                "is_active": c.is_active
            }
            for c in calendars
        ]
    }


@router.post("/calendars")
async def create_calendar(request: Request, calendar_req: CalendarCreateRequest, user_id: str = "default"):
    """Create a new calendar"""
    manager = get_calendar_manager(request)
    calendar = manager.create_calendar(
        name=calendar_req.name,
        source_type=calendar_req.source_type,
        source_url=calendar_req.source_url,
        credentials=calendar_req.credentials,
        user_id=user_id
    )
    
    return {
        "success": True,
        "calendar": {
            "id": calendar.id,
            "name": calendar.name,
            "source_type": calendar.source_type
        }
    }


@router.post("/calendars/{calendar_id}/sync")
async def sync_calendar(request: Request, calendar_id: int):
    """Sync calendar from external source"""
    manager = get_calendar_manager(request)
    success = manager.sync_ical_calendar(calendar_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to sync calendar")
    
    return {"success": True, "message": "Calendar synced"}


# Event endpoints
@router.get("/events")
async def list_events(
    request: Request,
    calendar_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: str = "default"
):
    """List events"""
    manager = get_calendar_manager(request)
    
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    events = manager.get_events(
        calendar_id=calendar_id,
        start_date=start_dt,
        end_date=end_dt,
        user_id=user_id
    )
    
    return {
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "location": e.location,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "all_day": e.all_day,
                "calendar_id": e.calendar_id
            }
            for e in events
        ]
    }


@router.get("/events/upcoming")
async def get_upcoming_events(request: Request, days: int = 7, user_id: str = "default"):
    """Get upcoming events"""
    manager = get_calendar_manager(request)
    events = manager.get_upcoming_events(days=days, user_id=user_id)
    
    return {
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "location": e.location
            }
            for e in events
        ]
    }


@router.post("/events")
async def create_event(request: Request, event_req: EventCreateRequest, user_id: str = "default"):
    """Create an event"""
    manager = get_calendar_manager(request)
    
    start_time = datetime.fromisoformat(event_req.start_time)
    end_time = datetime.fromisoformat(event_req.end_time)
    
    event = manager.create_event(
        calendar_id=event_req.calendar_id,
        title=event_req.title,
        start_time=start_time,
        end_time=end_time,
        description=event_req.description,
        location=event_req.location,
        all_day=event_req.all_day,
        recurrence_rule=event_req.recurrence_rule,
        user_id=user_id
    )
    
    return {
        "success": True,
        "event": {
            "id": event.id,
            "title": event.title,
            "start_time": event.start_time.isoformat()
        }
    }


# Reminder endpoints
@router.get("/reminders")
async def list_reminders(
    request: Request,
    completed: Optional[bool] = None,
    user_id: str = "default"
):
    """List reminders"""
    manager = get_reminder_manager(request)
    reminders = manager.get_reminders(user_id=user_id, completed=completed)
    
    return {
        "reminders": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "reminder_time": r.reminder_time.isoformat(),
                "completed": r.completed,
                "recurrence_type": r.recurrence_type,
                "priority": r.priority
            }
            for r in reminders
        ]
    }


@router.get("/reminders/upcoming")
async def get_upcoming_reminders(request: Request, hours: int = 24, user_id: str = "default"):
    """Get upcoming reminders"""
    manager = get_reminder_manager(request)
    reminders = manager.get_upcoming_reminders(hours=hours, user_id=user_id)
    
    return {
        "reminders": [
            {
                "id": r.id,
                "title": r.title,
                "reminder_time": r.reminder_time.isoformat(),
                "recurrence_type": r.recurrence_type
            }
            for r in reminders
        ]
    }


@router.post("/reminders")
async def create_reminder(request: Request, reminder_req: ReminderCreateRequest, user_id: str = "default"):
    """Create a reminder"""
    manager = get_reminder_manager(request)
    
    reminder_time = datetime.fromisoformat(reminder_req.reminder_time)
    
    reminder = manager.create_reminder(
        title=reminder_req.title,
        reminder_time=reminder_time,
        description=reminder_req.description,
        recurrence_type=reminder_req.recurrence_type,
        recurrence_interval=reminder_req.recurrence_interval,
        priority=reminder_req.priority,
        user_id=user_id
    )
    
    return {
        "success": True,
        "reminder": {
            "id": reminder.id,
            "title": reminder.title,
            "reminder_time": reminder.reminder_time.isoformat()
        }
    }


@router.post("/reminders/voice")
async def create_reminder_from_voice(request: Request, voice_req: ReminderVoiceRequest, user_id: str = "default"):
    """Create reminder from voice command"""
    manager = get_reminder_manager(request)
    
    reminder = manager.parse_reminder_from_text(voice_req.text, user_id=user_id)
    
    if not reminder:
        raise HTTPException(status_code=400, detail="Could not parse reminder from text")
    
    return {
        "success": True,
        "reminder": {
            "id": reminder.id,
            "title": reminder.title,
            "reminder_time": reminder.reminder_time.isoformat(),
            "recurrence_type": reminder.recurrence_type
        }
    }


@router.post("/reminders/{reminder_id}/complete")
async def complete_reminder(request: Request, reminder_id: int, user_id: str = "default"):
    """Mark reminder as completed"""
    manager = get_reminder_manager(request)
    success = manager.complete_reminder(reminder_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return {"success": True, "message": "Reminder completed"}


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(request: Request, reminder_id: int, user_id: str = "default"):
    """Delete a reminder"""
    manager = get_reminder_manager(request)
    success = manager.delete_reminder(reminder_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return {"success": True, "message": "Reminder deleted"}

