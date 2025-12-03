"""Database models for calendar and reminder system"""

import logging
from datetime import datetime, time
from typing import Optional, Dict, List, Any
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Calendar(Base):
    """Calendar source"""
    __tablename__ = "calendars"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # google, ical, local
    source_url = Column(String)  # For iCal URLs
    credentials = Column(JSON)  # Encrypted credentials
    color = Column(String, default="#4285f4")
    is_active = Column(Boolean, default=True)
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("CalendarEvent", back_populates="calendar")


class CalendarEvent(Base):
    """Calendar event"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    calendar_id = Column(Integer, ForeignKey('calendars.id'), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)
    
    # Recurrence
    recurrence_rule = Column(String)  # RRULE format
    recurrence_id = Column(Integer)  # Link to parent event
    
    # External ID (for sync)
    external_id = Column(String, index=True)
    
    # Metadata
    attendees = Column(JSON)  # List of attendees
    reminders = Column(JSON)  # List of reminder times
    
    user_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calendar = relationship("Calendar", back_populates="events")


class Reminder(Base):
    """Reminder/Task"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Reminder time
    reminder_time = Column(DateTime, nullable=False, index=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Recurrence
    recurrence_type = Column(String)  # none, daily, weekly, monthly, yearly
    recurrence_interval = Column(Integer, default=1)  # Every N days/weeks/etc
    recurrence_end_date = Column(DateTime, nullable=True)
    recurrence_count = Column(Integer, nullable=True)  # Max occurrences
    
    # Priority
    priority = Column(String, default="normal")  # low, normal, high
    
    # Voice command that created it
    voice_command = Column(Text)
    
    user_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReminderNotification(Base):
    """Reminder notification log"""
    __tablename__ = "reminder_notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reminder_id = Column(Integer, ForeignKey('reminders.id'), nullable=False)
    
    notification_time = Column(DateTime, nullable=False, index=True)
    notification_type = Column(String, default="voice")  # voice, push, email
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reminder = relationship("Reminder", foreign_keys=[reminder_id])


# Database setup
def get_calendar_db():
    """Get database session for calendar system"""
    db_path = settings.data_dir / "calendar.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

