"""Energy monitoring tool - handles energy voice commands"""

import logging
from datetime import datetime
from typing import List, Optional
from home_assistant_platform.core.voice.agent import Tool

logger = logging.getLogger(__name__)


class EnergyTool(Tool):
    """Tool for energy monitoring"""
    
    def __init__(self, energy_monitor=None):
        self.energy_monitor = energy_monitor
    
    @property
    def name(self) -> str:
        return "energy"
    
    @property
    def description(self) -> str:
        return "Monitor energy consumption and costs"
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "energy_usage", "power_consumption", "energy_cost",
            "energy_report", "power_usage"
        ]
    
    def can_handle(self, intent: str, text: str, entities: List[str]) -> bool:
        """Check if this tool can handle the request"""
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        if intent_lower in ["energy_usage", "energy_cost", "power_consumption"]:
            return True
        
        energy_keywords = [
            "energy", "power", "electricity", "consumption", "usage",
            "cost", "bill", "watt", "kwh", "kilowatt"
        ]
        
        return any(kw in text_lower for kw in energy_keywords)
    
    def execute(self, intent: str, text: str, entities: List[str]) -> Optional[str]:
        """Execute energy operation"""
        if not self.energy_monitor:
            return "Energy monitoring system is not available"
        
        text_lower = text.lower()
        intent_lower = intent.lower()
        
        # Get current total power
        if "current" in text_lower or "now" in text_lower or "right now" in text_lower:
            total_power = self.energy_monitor.get_total_power()
            return f"Current total power consumption is {total_power:.1f} watts ({total_power/1000:.2f} kilowatts)."
        
        # Get daily energy
        if "today" in text_lower or "daily" in text_lower:
            summary = self.energy_monitor.get_daily_summary(datetime.now())
            return f"Today's energy consumption: {summary['total_kwh']:.2f} kWh, cost: ${summary['total_cost']:.2f}"
        
        # Get weekly/monthly insights
        if "week" in text_lower or "weekly" in text_lower:
            insights = self.energy_monitor.get_energy_insights(days=7)
            return f"This week's energy: {insights['total_kwh']:.2f} kWh, total cost: ${insights['total_cost']:.2f}, average daily: {insights['average_daily_kwh']:.2f} kWh"
        
        if "month" in text_lower or "monthly" in text_lower:
            insights = self.energy_monitor.get_energy_insights(days=30)
            return f"This month's energy: {insights['total_kwh']:.2f} kWh, total cost: ${insights['total_cost']:.2f}, average daily: {insights['average_daily_kwh']:.2f} kWh"
        
        # Get device-specific energy
        if "device" in text_lower:
            # Try to extract device name
            device_name = self._extract_device_name(text_lower)
            if device_name:
                # This would need device_id lookup
                return f"I can check energy for {device_name}, but I need the device ID. Try asking about total energy usage instead."
        
        # Default: daily summary
        summary = self.energy_monitor.get_daily_summary(datetime.now())
        return f"Today's energy consumption: {summary['total_kwh']:.2f} kWh, cost: ${summary['total_cost']:.2f}. Current power: {self.energy_monitor.get_total_power():.1f}W"
    
    def _extract_device_name(self, text: str) -> Optional[str]:
        """Extract device name from text"""
        import re
        
        patterns = [
            r"device (.+)",
            r"(.+) energy",
            r"(.+) power",
            r"(.+) consumption"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        return None

