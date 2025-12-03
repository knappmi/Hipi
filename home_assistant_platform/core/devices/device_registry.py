"""Device registry - unified device management"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from home_assistant_platform.core.automation.device_manager import DeviceManager

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """Unified device registry that combines multiple device sources"""
    
    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.device_managers: List[DeviceManager] = []
        self.device_sources: Dict[str, str] = {}  # device_id -> source name
    
    def register_manager(self, manager: DeviceManager, source_name: str):
        """Register a device manager"""
        self.device_managers.append(manager)
        logger.info(f"Registered device manager: {source_name}")
        
        # Load devices from this manager
        try:
            devices = manager.list_devices()
            for device in devices:
                device_id = device.get("id")
                if device_id:
                    self.devices[device_id] = device
                    self.device_sources[device_id] = source_name
                    logger.debug(f"Registered device from {source_name}: {device_id}")
        except Exception as e:
            logger.error(f"Error loading devices from {source_name}: {e}")
    
    def get_device_manager(self, device_id: str) -> Optional[DeviceManager]:
        """Get the device manager for a specific device"""
        source = self.device_sources.get(device_id)
        if source:
            # Find manager by source name (simplified - in production use a mapping)
            for manager in self.device_managers:
                if hasattr(manager, 'source_name') and manager.source_name == source:
                    return manager
            # Fallback: return first manager
            return self.device_managers[0] if self.device_managers else None
        return None
    
    async def turn_on_device(self, device_id: str) -> bool:
        """Turn on a device"""
        manager = self.get_device_manager(device_id)
        if manager:
            result = await manager.turn_on_device(device_id)
            if result:
                # Update local state
                if device_id in self.devices:
                    self.devices[device_id]["state"] = "on"
                    if "brightness" in self.devices[device_id]:
                        self.devices[device_id]["brightness"] = 100
            return result
        logger.warning(f"No manager found for device: {device_id}")
        return False
    
    async def turn_off_device(self, device_id: str) -> bool:
        """Turn off a device"""
        manager = self.get_device_manager(device_id)
        if manager:
            result = await manager.turn_off_device(device_id)
            if result:
                # Update local state
                if device_id in self.devices:
                    self.devices[device_id]["state"] = "off"
                    if "brightness" in self.devices[device_id]:
                        self.devices[device_id]["brightness"] = 0
            return result
        logger.warning(f"No manager found for device: {device_id}")
        return False
    
    async def set_temperature(self, device_id: str, temperature: float) -> bool:
        """Set device temperature"""
        manager = self.get_device_manager(device_id)
        if manager and hasattr(manager, 'set_temperature'):
            result = await manager.set_temperature(device_id, temperature)
            if result and device_id in self.devices:
                self.devices[device_id]["temperature"] = temperature
            return result
        return False
    
    async def set_brightness(self, device_id: str, brightness: int) -> bool:
        """Set device brightness"""
        manager = self.get_device_manager(device_id)
        if manager and hasattr(manager, 'set_brightness'):
            result = await manager.set_brightness(device_id, brightness)
            if result and device_id in self.devices:
                self.devices[device_id]["brightness"] = brightness
            return result
        return False
    
    async def set_color(self, device_id: str, color: str) -> bool:
        """Set device color"""
        manager = self.get_device_manager(device_id)
        if manager and hasattr(manager, 'set_color'):
            result = await manager.set_color(device_id, color)
            if result and device_id in self.devices:
                self.devices[device_id]["color"] = color
            return result
        return False
    
    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device state"""
        # Try to get fresh state from manager
        manager = self.get_device_manager(device_id)
        if manager:
            state = await manager.get_device_state(device_id)
            if state:
                # Update local cache
                self.devices[device_id] = state
                return state
        
        # Fallback to cached state
        return self.devices.get(device_id)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List all registered devices"""
        return list(self.devices.values())
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device info"""
        return self.devices.get(device_id)
    
    def add_device(self, device: Dict[str, Any], source: str = "manual"):
        """Manually add a device"""
        device_id = device.get("id")
        if device_id:
            self.devices[device_id] = device
            self.device_sources[device_id] = source
            logger.info(f"Added device: {device_id} from {source}")
    
    def remove_device(self, device_id: str):
        """Remove a device"""
        if device_id in self.devices:
            del self.devices[device_id]
            if device_id in self.device_sources:
                del self.device_sources[device_id]
            logger.info(f"Removed device: {device_id}")

