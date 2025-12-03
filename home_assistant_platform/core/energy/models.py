"""Database models for energy monitoring system"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class DeviceEnergyReading(Base):
    """Energy consumption reading for a device"""
    __tablename__ = "device_energy_readings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    device_name = Column(String)
    
    # Energy data
    power_watts = Column(Float, nullable=False)  # Current power consumption in watts
    energy_kwh = Column(Float)  # Cumulative energy in kWh
    voltage = Column(Float)  # Voltage in volts
    current = Column(Float)  # Current in amps
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Metadata
    user_id = Column(String, default="default", index=True)
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )


class DeviceEnergyProfile(Base):
    """Energy profile for a device"""
    __tablename__ = "device_energy_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, unique=True)
    device_name = Column(String)
    device_type = Column(String)
    
    # Power ratings
    rated_power_watts = Column(Float)  # Manufacturer's rated power
    typical_power_watts = Column(Float)  # Typical power consumption
    standby_power_watts = Column(Float)  # Standby power consumption
    
    # Usage patterns
    average_daily_hours = Column(Float, default=0)  # Average hours per day
    average_daily_kwh = Column(Float, default=0)  # Average daily kWh
    
    # Cost
    cost_per_kwh = Column(Float, default=0.12)  # Cost per kWh in dollars
    
    # Metadata
    user_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EnergyAlert(Base):
    """Energy consumption alerts"""
    __tablename__ = "energy_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False)
    
    # Alert configuration
    alert_type = Column(String, nullable=False)  # high_consumption, threshold_exceeded, anomaly
    threshold_value = Column(Float)  # Threshold value (watts or kWh)
    
    # Alert status
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Metadata
    user_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)


class EnergySummary(Base):
    """Daily energy summary"""
    __tablename__ = "energy_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Total consumption
    total_kwh = Column(Float, nullable=False, default=0)
    total_cost = Column(Float, default=0)
    
    # Device breakdown
    device_breakdown = Column(JSON)  # {device_id: kwh, ...}
    
    # Peak consumption
    peak_power_watts = Column(Float, default=0)
    peak_time = Column(DateTime, nullable=True)
    
    # Metadata
    user_id = Column(String, default="default", index=True)
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
    )


# Database setup
def get_energy_db():
    """Get database session for energy system"""
    db_path = settings.data_dir / "energy.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

