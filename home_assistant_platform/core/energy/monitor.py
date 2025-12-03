"""Energy monitor - tracks and analyzes energy consumption"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from home_assistant_platform.core.energy.models import (
    DeviceEnergyReading, DeviceEnergyProfile, EnergyAlert, EnergySummary,
    get_energy_db
)

logger = logging.getLogger(__name__)


class EnergyMonitor:
    """Monitors and analyzes energy consumption"""
    
    def __init__(self):
        self.db = get_energy_db()
        self.default_cost_per_kwh = 0.12  # Default $0.12 per kWh
    
    def record_reading(
        self,
        device_id: str,
        power_watts: float,
        device_name: Optional[str] = None,
        voltage: Optional[float] = None,
        current: Optional[float] = None,
        energy_kwh: Optional[float] = None,
        user_id: str = "default"
    ) -> DeviceEnergyReading:
        """Record an energy reading"""
        reading = DeviceEnergyReading(
            device_id=device_id,
            device_name=device_name or device_id,
            power_watts=power_watts,
            energy_kwh=energy_kwh,
            voltage=voltage,
            current=current,
            user_id=user_id
        )
        
        self.db.add(reading)
        self.db.commit()
        
        # Check for alerts
        self._check_alerts(device_id, power_watts, user_id)
        
        logger.debug(f"Recorded energy reading: {device_id} = {power_watts}W")
        return reading
    
    def get_device_readings(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: str = "default"
    ) -> List[DeviceEnergyReading]:
        """Get energy readings for a device"""
        query = self.db.query(DeviceEnergyReading).filter(
            DeviceEnergyReading.device_id == device_id,
            DeviceEnergyReading.user_id == user_id
        )
        
        if start_time:
            query = query.filter(DeviceEnergyReading.timestamp >= start_time)
        if end_time:
            query = query.filter(DeviceEnergyReading.timestamp <= end_time)
        
        return query.order_by(DeviceEnergyReading.timestamp).all()
    
    def get_current_power(self, device_id: str, user_id: str = "default") -> Optional[float]:
        """Get current power consumption for a device"""
        reading = self.db.query(DeviceEnergyReading).filter(
            DeviceEnergyReading.device_id == device_id,
            DeviceEnergyReading.user_id == user_id
        ).order_by(DeviceEnergyReading.timestamp.desc()).first()
        
        return reading.power_watts if reading else None
    
    def get_total_power(self, user_id: str = "default") -> float:
        """Get total current power consumption across all devices"""
        # Get latest reading for each device
        from sqlalchemy import func
        
        subquery = self.db.query(
            DeviceEnergyReading.device_id,
            func.max(DeviceEnergyReading.timestamp).label('max_timestamp')
        ).filter(
            DeviceEnergyReading.user_id == user_id
        ).group_by(DeviceEnergyReading.device_id).subquery()
        
        readings = self.db.query(DeviceEnergyReading).join(
            subquery,
            (DeviceEnergyReading.device_id == subquery.c.device_id) &
            (DeviceEnergyReading.timestamp == subquery.c.max_timestamp)
        ).all()
        
        return sum(r.power_watts for r in readings) if readings else 0.0
    
    def calculate_energy_consumption(
        self,
        device_id: str,
        start_time: datetime,
        end_time: datetime,
        user_id: str = "default"
    ) -> Dict[str, float]:
        """Calculate energy consumption for a time period"""
        readings = self.get_device_readings(device_id, start_time, end_time, user_id)
        
        if not readings:
            return {
                "total_kwh": 0.0,
                "average_power_watts": 0.0,
                "peak_power_watts": 0.0,
                "hours": 0.0
            }
        
        # Calculate total energy (integrate power over time)
        total_energy = 0.0
        peak_power = 0.0
        
        for i in range(len(readings) - 1):
            current = readings[i]
            next_reading = readings[i + 1]
            
            # Time difference in hours
            time_diff = (next_reading.timestamp - current.timestamp).total_seconds() / 3600
            
            # Average power during this interval
            avg_power = (current.power_watts + next_reading.power_watts) / 2
            
            # Energy = power * time
            total_energy += avg_power * time_diff
            
            peak_power = max(peak_power, current.power_watts, next_reading.power_watts)
        
        total_hours = (end_time - start_time).total_seconds() / 3600
        avg_power = sum(r.power_watts for r in readings) / len(readings) if readings else 0.0
        
        return {
            "total_kwh": total_energy / 1000,  # Convert to kWh
            "average_power_watts": avg_power,
            "peak_power_watts": peak_power,
            "hours": total_hours
        }
    
    def get_daily_summary(self, date: datetime, user_id: str = "default") -> Dict[str, Any]:
        """Get daily energy summary"""
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        # Get all device readings for the day
        readings = self.db.query(DeviceEnergyReading).filter(
            DeviceEnergyReading.user_id == user_id,
            DeviceEnergyReading.timestamp >= start_time,
            DeviceEnergyReading.timestamp < end_time
        ).all()
        
        if not readings:
            return {
                "date": date.date().isoformat(),
                "total_kwh": 0.0,
                "total_cost": 0.0,
                "device_breakdown": {},
                "peak_power_watts": 0.0
            }
        
        # Group by device
        device_energy = {}
        peak_power = 0.0
        
        devices = set(r.device_id for r in readings)
        for device_id in devices:
            device_readings = [r for r in readings if r.device_id == device_id]
            device_readings.sort(key=lambda x: x.timestamp)
            
            # Calculate energy for this device
            device_total = 0.0
            for i in range(len(device_readings) - 1):
                current = device_readings[i]
                next_reading = device_readings[i + 1]
                time_diff = (next_reading.timestamp - current.timestamp).total_seconds() / 3600
                avg_power = (current.power_watts + next_reading.power_watts) / 2
                device_total += avg_power * time_diff
            
            device_energy[device_id] = device_total / 1000  # Convert to kWh
            peak_power = max(peak_power, max(r.power_watts for r in device_readings))
        
        total_kwh = sum(device_energy.values())
        
        # Get cost per kWh from profile or use default
        profile = self.db.query(DeviceEnergyProfile).filter(
            DeviceEnergyProfile.user_id == user_id
        ).first()
        cost_per_kwh = profile.cost_per_kwh if profile else self.default_cost_per_kwh
        
        total_cost = total_kwh * cost_per_kwh
        
        return {
            "date": date.date().isoformat(),
            "total_kwh": total_kwh,
            "total_cost": total_cost,
            "device_breakdown": device_energy,
            "peak_power_watts": peak_power
        }
    
    def create_device_profile(
        self,
        device_id: str,
        device_name: str,
        rated_power_watts: Optional[float] = None,
        typical_power_watts: Optional[float] = None,
        standby_power_watts: Optional[float] = None,
        cost_per_kwh: Optional[float] = None,
        user_id: str = "default"
    ) -> DeviceEnergyProfile:
        """Create or update device energy profile"""
        profile = self.db.query(DeviceEnergyProfile).filter(
            DeviceEnergyProfile.device_id == device_id,
            DeviceEnergyProfile.user_id == user_id
        ).first()
        
        if profile:
            if rated_power_watts is not None:
                profile.rated_power_watts = rated_power_watts
            if typical_power_watts is not None:
                profile.typical_power_watts = typical_power_watts
            if standby_power_watts is not None:
                profile.standby_power_watts = standby_power_watts
            if cost_per_kwh is not None:
                profile.cost_per_kwh = cost_per_kwh
            profile.updated_at = datetime.utcnow()
        else:
            profile = DeviceEnergyProfile(
                device_id=device_id,
                device_name=device_name,
                rated_power_watts=rated_power_watts,
                typical_power_watts=typical_power_watts,
                standby_power_watts=standby_power_watts,
                cost_per_kwh=cost_per_kwh or self.default_cost_per_kwh,
                user_id=user_id
            )
            self.db.add(profile)
        
        self.db.commit()
        logger.info(f"Created/updated energy profile for device: {device_id}")
        return profile
    
    def create_alert(
        self,
        device_id: str,
        alert_type: str,
        threshold_value: float,
        user_id: str = "default"
    ) -> EnergyAlert:
        """Create an energy alert"""
        alert = EnergyAlert(
            device_id=device_id,
            alert_type=alert_type,
            threshold_value=threshold_value,
            user_id=user_id
        )
        
        self.db.add(alert)
        self.db.commit()
        
        logger.info(f"Created energy alert: {device_id} - {alert_type}")
        return alert
    
    def _check_alerts(self, device_id: str, power_watts: float, user_id: str):
        """Check if any alerts should be triggered"""
        alerts = self.db.query(EnergyAlert).filter(
            EnergyAlert.device_id == device_id,
            EnergyAlert.user_id == user_id,
            EnergyAlert.is_active == True
        ).all()
        
        for alert in alerts:
            if alert.alert_type == "high_consumption" and power_watts > alert.threshold_value:
                if not alert.triggered_at:
                    alert.triggered_at = datetime.utcnow()
                    self.db.commit()
                    logger.warning(f"Energy alert triggered: {device_id} = {power_watts}W (threshold: {alert.threshold_value}W)")
    
    def get_energy_insights(self, days: int = 7, user_id: str = "default") -> Dict[str, Any]:
        """Get energy consumption insights"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily summaries
        daily_summaries = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            summary = self.get_daily_summary(date, user_id)
            daily_summaries.append(summary)
        
        total_kwh = sum(s["total_kwh"] for s in daily_summaries)
        total_cost = sum(s["total_cost"] for s in daily_summaries)
        avg_daily_kwh = total_kwh / days if days > 0 else 0.0
        
        # Find peak day
        peak_day = max(daily_summaries, key=lambda x: x["total_kwh"]) if daily_summaries else None
        
        # Device breakdown
        device_totals = {}
        for summary in daily_summaries:
            for device_id, kwh in summary["device_breakdown"].items():
                device_totals[device_id] = device_totals.get(device_id, 0) + kwh
        
        # Top consuming devices
        top_devices = sorted(device_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_kwh": total_kwh,
            "total_cost": total_cost,
            "average_daily_kwh": avg_daily_kwh,
            "average_daily_cost": total_cost / days if days > 0 else 0.0,
            "peak_day": peak_day,
            "top_devices": [{"device_id": d[0], "total_kwh": d[1]} for d in top_devices],
            "daily_summaries": daily_summaries
        }

