"""Database models for automation system"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class DeviceAction(Base):
    """Record of device actions for pattern learning"""
    __tablename__ = "device_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    device_type = Column(String, nullable=False)  # light, thermostat, switch, etc.
    action = Column(String, nullable=False)  # turn_on, turn_off, set_temperature, etc.
    value = Column(String)  # Optional value (e.g., temperature setting)
    
    # Context
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    hour = Column(Integer)  # 0-23
    minute = Column(Integer)  # 0-59
    
    # Additional context (JSON)
    context = Column(JSON)  # weather, presence, etc.
    
    # User info (for multi-user support)
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Pattern(Base):
    """Detected usage patterns"""
    __tablename__ = "patterns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_type = Column(String, nullable=False)  # time_based, event_based, etc.
    
    # Pattern details
    device_id = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    value = Column(String)
    
    # Pattern conditions
    conditions = Column(JSON)  # {day_of_week: [0,1,2,3,4], hour: 19, minute: 0}
    
    # Statistics
    occurrence_count = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)  # 0.0-1.0
    last_occurrence = Column(DateTime)
    first_detected = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Automation(Base):
    """Automation rules"""
    __tablename__ = "automations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Trigger
    trigger_type = Column(String, nullable=False)  # time, pattern, event, manual
    trigger_config = Column(JSON)  # Trigger-specific configuration
    
    # Actions
    actions = Column(JSON, nullable=False)  # List of actions to execute
    
    # Conditions
    conditions = Column(JSON)  # Optional conditions
    
    # Status
    is_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_from_pattern = Column(Integer, ForeignKey('patterns.id'), nullable=True)
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pattern = relationship("Pattern", foreign_keys=[created_from_pattern])


class AutomationSuggestion(Base):
    """Suggested automations from pattern detection"""
    __tablename__ = "automation_suggestions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(Integer, ForeignKey('patterns.id'), nullable=False)
    
    # Suggestion details
    suggestion_text = Column(Text, nullable=False)
    automation_name = Column(String, nullable=False)
    automation_config = Column(JSON, nullable=False)
    
    # Status
    status = Column(String, default="pending")  # pending, accepted, rejected, dismissed
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    pattern = relationship("Pattern", foreign_keys=[pattern_id])


class AutomationExecution(Base):
    """Log of automation executions"""
    __tablename__ = "automation_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    automation_id = Column(Integer, ForeignKey('automations.id'), nullable=False)
    
    # Execution details
    trigger_type = Column(String, nullable=False)
    trigger_data = Column(JSON)
    actions_executed = Column(JSON)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    automation = relationship("Automation", foreign_keys=[automation_id])


# Database setup
def get_automation_db():
    """Get database session for automation system"""
    db_path = settings.data_dir / "automation.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

