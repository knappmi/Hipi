"""Unified device manager - combines all device sources"""

import logging
from typing import Dict, List, Optional, Any
from home_assistant_platform.core.automation.device_manager import DeviceManager
from home_assistant_platform.core.devices.device_registry import DeviceRegistry
from home_assistant_platform.core.devices.mqtt_manager import MQTTDeviceManager
from home_assistant_platform.core.automation.device_manager import MockDeviceManager

logger = logging.getLogger(__name__)


class UnifiedDeviceManager(DeviceManager):
    """Unified device manager that combines all device sources"""
    
    def __init__(self):
        self.registry = DeviceRegistry()
        
        # Register mock devices by default
        mock_manager = MockDeviceManager()
        self.registry.register_manager(mock_manager, "mock")
        
        # Try to register MQTT manager if configured
        try:
            mqtt_manager = MQTTDeviceManager()
            if mqtt_manager.connect():
                self.registry.register_manager(mqtt_manager, "mqtt")
                logger.info("MQTT device manager registered")
        except Exception as e:
            logger.warning(f"Could not initialize MQTT manager: {e}")
    
    async def turn_on_device(self, device_id: str) -> bool:
        """Turn on a device"""
        return await self.registry.turn_on_device(device_id)
    
    async def turn_off_device(self, device_id: str) -> bool:
        """Turn off a device"""
        return await self.registry.turn_off_device(device_id)
    
    async def set_temperature(self, device_id: str, temperature: float) -> bool:
        """Set device temperature"""
        return await self.registry.set_temperature(device_id, temperature)
    
    async def set_brightness(self, device_id: str, brightness: int) -> bool:
        """Set device brightness"""
        return await self.registry.set_brightness(device_id, brightness)
    
    async def set_color(self, device_id: str, color: str) -> bool:
        """Set device color"""
        return await self.registry.set_color(device_id, color)
    
    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device state"""
        return await self.registry.get_device_state(device_id)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List all devices"""
        return self.registry.list_devices()
    
    def register_wifi_manager(self, manager: DeviceManager, source_name: str):
        """Register a WiFi device manager"""
        self.registry.register_manager(manager, source_name)
    
    async def discover_wifi_devices(self):
        """Discover WiFi devices"""
        from home_assistant_platform.core.devices.wifi_discovery import (
            WiFiDeviceDiscovery, TPLinkDeviceManager, HueDeviceManager
        )
        
        discovery = WiFiDeviceDiscovery()
        devices = await discovery.discover_all()
        
        # Register TP-Link devices if found
        tplink_devices = [d for d in devices if d.get("source") == "tplink"]
        if tplink_devices:
            tplink_manager = TPLinkDeviceManager()
            await tplink_manager.discover_devices()
            self.registry.register_manager(tplink_manager, "tplink")
        
        # Register Hue devices if found
        hue_devices = [d for d in devices if d.get("source") == "hue"]
        if hue_devices:
            hue_manager = HueDeviceManager()
            await hue_manager.connect()
            self.registry.register_manager(hue_manager, "hue")
        
        return devices

