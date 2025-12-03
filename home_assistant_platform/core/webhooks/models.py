"""Webhook data models"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Webhook(Base):
    """Webhook configuration"""
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    method = Column(String, default="POST")  # GET, POST, PUT, DELETE
    headers = Column(JSON)  # Custom headers
    payload_template = Column(Text)  # Jinja2 template for payload
    secret = Column(String)  # Webhook secret for verification
    
    # Triggers
    trigger_on_device_change = Column(Boolean, default=False)
    trigger_on_scene_activate = Column(Boolean, default=False)
    trigger_on_automation_run = Column(Boolean, default=False)
    trigger_on_voice_command = Column(Boolean, default=False)
    trigger_on_custom_event = Column(Boolean, default=False)
    custom_event_types = Column(JSON)  # List of event types to trigger on
    
    # Status
    enabled = Column(Boolean, default=True)
    timeout = Column(Integer, default=10)  # Request timeout in seconds
    retry_count = Column(Integer, default=3)
    
    # Metadata
    user_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookLog(Base):
    """Webhook execution log"""
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    method = Column(String, default="POST")
    
    # Request
    request_payload = Column(JSON)
    request_headers = Column(JSON)
    
    # Response
    response_status = Column(Integer)
    response_body = Column(Text)
    response_time_ms = Column(Float)
    
    # Status
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    
    # Metadata
    triggered_by = Column(String)  # Event that triggered this
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
def get_webhooks_db():
    """Get database session for webhooks"""
    db_path = settings.data_dir / "webhooks.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

