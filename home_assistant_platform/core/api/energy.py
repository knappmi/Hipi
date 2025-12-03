"""Energy monitoring API endpoints"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from home_assistant_platform.core.energy.monitor import EnergyMonitor

logger = logging.getLogger(__name__)
router = APIRouter()


class EnergyReadingRequest(BaseModel):
    device_id: str
    power_watts: float
    device_name: Optional[str] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    energy_kwh: Optional[float] = None


class DeviceProfileRequest(BaseModel):
    device_id: str
    device_name: str
    rated_power_watts: Optional[float] = None
    typical_power_watts: Optional[float] = None
    standby_power_watts: Optional[float] = None
    cost_per_kwh: Optional[float] = None


class EnergyAlertRequest(BaseModel):
    device_id: str
    alert_type: str  # high_consumption, threshold_exceeded
    threshold_value: float


def get_energy_monitor(request: Request) -> EnergyMonitor:
    """Get energy monitor from app state"""
    if not hasattr(request.app.state, 'energy_monitor'):
        request.app.state.energy_monitor = EnergyMonitor()
    return request.app.state.energy_monitor


@router.post("/readings")
async def record_reading(request: Request, reading_req: EnergyReadingRequest, user_id: str = "default"):
    """Record an energy reading"""
    monitor = get_energy_monitor(request)
    reading = monitor.record_reading(
        device_id=reading_req.device_id,
        power_watts=reading_req.power_watts,
        device_name=reading_req.device_name,
        voltage=reading_req.voltage,
        current=reading_req.current,
        energy_kwh=reading_req.energy_kwh,
        user_id=user_id
    )
    
    return {
        "success": True,
        "reading": {
            "id": reading.id,
            "device_id": reading.device_id,
            "power_watts": reading.power_watts,
            "timestamp": reading.timestamp.isoformat()
        }
    }


@router.get("/readings/{device_id}")
async def get_device_readings(
    request: Request,
    device_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    user_id: str = "default"
):
    """Get energy readings for a device"""
    monitor = get_energy_monitor(request)
    
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None
    
    readings = monitor.get_device_readings(device_id, start_dt, end_dt, user_id)
    
    return {
        "readings": [
            {
                "id": r.id,
                "power_watts": r.power_watts,
                "energy_kwh": r.energy_kwh,
                "voltage": r.voltage,
                "current": r.current,
                "timestamp": r.timestamp.isoformat()
            }
            for r in readings
        ]
    }


@router.get("/current")
async def get_current_power(request: Request, device_id: Optional[str] = None, user_id: str = "default"):
    """Get current power consumption"""
    monitor = get_energy_monitor(request)
    
    if device_id:
        power = monitor.get_current_power(device_id, user_id)
        if power is None:
            raise HTTPException(status_code=404, detail="Device not found or no readings")
        return {
            "device_id": device_id,
            "power_watts": power,
            "power_kilowatts": power / 1000
        }
    else:
        total_power = monitor.get_total_power(user_id)
        return {
            "total_power_watts": total_power,
            "total_power_kilowatts": total_power / 1000
        }


@router.get("/consumption/{device_id}")
async def get_energy_consumption(
    request: Request,
    device_id: str,
    start_time: str,
    end_time: str,
    user_id: str = "default"
):
    """Calculate energy consumption for a time period"""
    monitor = get_energy_monitor(request)
    
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    consumption = monitor.calculate_energy_consumption(device_id, start_dt, end_dt, user_id)
    
    return {
        "device_id": device_id,
        "start_time": start_time,
        "end_time": end_time,
        **consumption
    }


@router.get("/summary")
async def get_daily_summary(request: Request, date: Optional[str] = None, user_id: str = "default"):
    """Get daily energy summary"""
    monitor = get_energy_monitor(request)
    
    if date:
        summary_date = datetime.fromisoformat(date)
    else:
        summary_date = datetime.now()
    
    summary = monitor.get_daily_summary(summary_date, user_id)
    return {"summary": summary}


@router.get("/insights")
async def get_energy_insights(request: Request, days: int = 7, user_id: str = "default"):
    """Get energy consumption insights"""
    monitor = get_energy_monitor(request)
    insights = monitor.get_energy_insights(days=days, user_id=user_id)
    return {"insights": insights}


@router.post("/profiles")
async def create_device_profile(request: Request, profile_req: DeviceProfileRequest, user_id: str = "default"):
    """Create or update device energy profile"""
    monitor = get_energy_monitor(request)
    profile = monitor.create_device_profile(
        device_id=profile_req.device_id,
        device_name=profile_req.device_name,
        rated_power_watts=profile_req.rated_power_watts,
        typical_power_watts=profile_req.typical_power_watts,
        standby_power_watts=profile_req.standby_power_watts,
        cost_per_kwh=profile_req.cost_per_kwh,
        user_id=user_id
    )
    
    return {
        "success": True,
        "profile": {
            "id": profile.id,
            "device_id": profile.device_id,
            "device_name": profile.device_name,
            "rated_power_watts": profile.rated_power_watts,
            "typical_power_watts": profile.typical_power_watts
        }
    }


@router.post("/alerts")
async def create_alert(request: Request, alert_req: EnergyAlertRequest, user_id: str = "default"):
    """Create an energy alert"""
    monitor = get_energy_monitor(request)
    alert = monitor.create_alert(
        device_id=alert_req.device_id,
        alert_type=alert_req.alert_type,
        threshold_value=alert_req.threshold_value,
        user_id=user_id
    )
    
    return {
        "success": True,
        "alert": {
            "id": alert.id,
            "device_id": alert.device_id,
            "alert_type": alert.alert_type,
            "threshold_value": alert.threshold_value
        }
    }

