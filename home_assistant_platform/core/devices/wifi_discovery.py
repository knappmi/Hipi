"""WiFi device discovery - TP-Link Kasa, Philips Hue, etc."""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from home_assistant_platform.core.automation.device_manager import DeviceManager

logger = logging.getLogger(__name__)


class WiFiDeviceDiscovery:
    """Discovers WiFi smart devices on the network"""
    
    def __init__(self):
        self.discovered_devices: Dict[str, Dict[str, Any]] = {}
    
    async def discover_tplink_devices(self) -> List[Dict[str, Any]]:
        """Discover TP-Link Kasa devices"""
        devices = []
        
        try:
            # Try to import python-kasa if available
            try:
                from kasa import Discover
                
                found_devices = await Discover.discover()
                for device in found_devices.values():
                    device_info = {
                        "id": f"tplink_{device.device_id}",
                        "name": device.alias or device.host,
                        "type": "light" if device.is_light else "switch",
                        "state": "on" if device.is_on else "off",
                        "source": "tplink",
                        "host": device.host,
                        "device_id": device.device_id,
                        "model": device.model,
                        "brightness": device.brightness if hasattr(device, 'brightness') else None,
                        "color_temp": device.color_temp if hasattr(device, 'color_temp') else None,
                    }
                    devices.append(device_info)
                    self.discovered_devices[device_info["id"]] = device_info
                
                logger.info(f"Discovered {len(devices)} TP-Link devices")
                
            except ImportError:
                logger.info("python-kasa not installed. Install with: pip install python-kasa")
            except Exception as e:
                logger.error(f"Error discovering TP-Link devices: {e}")
        
        except Exception as e:
            logger.error(f"Error in TP-Link discovery: {e}")
        
        return devices
    
    async def discover_hue_devices(self, bridge_ip: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover Philips Hue devices"""
        devices = []
        
        try:
            # Try to import phue if available
            try:
                from phue import Bridge
                
                # Auto-discover bridge if IP not provided
                if not bridge_ip:
                    # Try common IPs or use UPnP discovery
                    bridge_ip = "192.168.1.1"  # Default, should be discovered
                
                bridge = Bridge(bridge_ip)
                bridge.connect()
                
                lights = bridge.lights
                for light in lights:
                    device_info = {
                        "id": f"hue_{light.light_id}",
                        "name": light.name,
                        "type": "light",
                        "state": "on" if light.on else "off",
                        "source": "hue",
                        "brightness": light.brightness,
                        "hue": light.hue,
                        "saturation": light.saturation,
                        "color_mode": light.colormode,
                    }
                    devices.append(device_info)
                    self.discovered_devices[device_info["id"]] = device_info
                
                logger.info(f"Discovered {len(devices)} Hue devices")
                
            except ImportError:
                logger.info("phue not installed. Install with: pip install phue")
            except Exception as e:
                logger.error(f"Error discovering Hue devices: {e}")
        
        except Exception as e:
            logger.error(f"Error in Hue discovery: {e}")
        
        return devices
    
    async def discover_all(self) -> List[Dict[str, Any]]:
        """Discover all WiFi devices"""
        all_devices = []
        
        # Discover TP-Link devices
        tplink_devices = await self.discover_tplink_devices()
        all_devices.extend(tplink_devices)
        
        # Discover Hue devices
        hue_devices = await self.discover_hue_devices()
        all_devices.extend(hue_devices)
        
        logger.info(f"Total discovered WiFi devices: {len(all_devices)}")
        return all_devices


class TPLinkDeviceManager(DeviceManager):
    """TP-Link Kasa device manager"""
    
    def __init__(self):
        self.source_name = "tplink"
        self.devices: Dict[str, Any] = {}
        self.kasa_devices: Dict[str, Any] = {}
    
    async def discover_devices(self):
        """Discover TP-Link devices"""
        try:
            from kasa import Discover
            
            found_devices = await Discover.discover()
            for device in found_devices.values():
                device_id = f"tplink_{device.device_id}"
                self.kasa_devices[device_id] = device
                self.devices[device_id] = {
                    "id": device_id,
                    "name": device.alias or device.host,
                    "type": "light" if device.is_light else "switch",
                    "state": "on" if device.is_on else "off",
                    "source": "tplink",
                    "host": device.host,
                }
            
            logger.info(f"Discovered {len(self.devices)} TP-Link devices")
            
        except ImportError:
            logger.warning("python-kasa not installed. Install with: pip install python-kasa")
        except Exception as e:
            logger.error(f"Error discovering TP-Link devices: {e}")
    
    async def turn_on_device(self, device_id: str) -> bool:
        """Turn on TP-Link device"""
        if device_id in self.kasa_devices:
            try:
                device = self.kasa_devices[device_id]
                await device.turn_on()
                await device.update()
                self.devices[device_id]["state"] = "on"
                return True
            except Exception as e:
                logger.error(f"Error turning on {device_id}: {e}")
        return False
    
    async def turn_off_device(self, device_id: str) -> bool:
        """Turn off TP-Link device"""
        if device_id in self.kasa_devices:
            try:
                device = self.kasa_devices[device_id]
                await device.turn_off()
                await device.update()
                self.devices[device_id]["state"] = "off"
                return True
            except Exception as e:
                logger.error(f"Error turning off {device_id}: {e}")
        return False
    
    async def set_brightness(self, device_id: str, brightness: int) -> bool:
        """Set TP-Link device brightness"""
        if device_id in self.kasa_devices:
            try:
                device = self.kasa_devices[device_id]
                if hasattr(device, 'set_brightness'):
                    await device.set_brightness(brightness)
                    await device.update()
                    self.devices[device_id]["brightness"] = brightness
                    return True
            except Exception as e:
                logger.error(f"Error setting brightness for {device_id}: {e}")
        return False
    
    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get TP-Link device state"""
        if device_id in self.kasa_devices:
            try:
                device = self.kasa_devices[device_id]
                await device.update()
                return {
                    "id": device_id,
                    "name": device.alias or device.host,
                    "state": "on" if device.is_on else "off",
                    "brightness": device.brightness if hasattr(device, 'brightness') else None,
                }
            except Exception as e:
                logger.error(f"Error getting state for {device_id}: {e}")
        return self.devices.get(device_id)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List TP-Link devices"""
        return list(self.devices.values())


class HueDeviceManager(DeviceManager):
    """Philips Hue device manager"""
    
    def __init__(self, bridge_ip: Optional[str] = None):
        self.source_name = "hue"
        self.bridge_ip = bridge_ip
        self.bridge: Optional[Any] = None
        self.devices: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self) -> bool:
        """Connect to Hue bridge"""
        try:
            from phue import Bridge
            
            if not self.bridge_ip:
                self.bridge_ip = "192.168.1.1"  # Should be discovered
            
            self.bridge = Bridge(self.bridge_ip)
            self.bridge.connect()
            
            # Load lights
            for light in self.bridge.lights:
                device_id = f"hue_{light.light_id}"
                self.devices[device_id] = {
                    "id": device_id,
                    "name": light.name,
                    "type": "light",
                    "state": "on" if light.on else "off",
                    "source": "hue",
                }
            
            logger.info(f"Connected to Hue bridge, found {len(self.devices)} lights")
            return True
            
        except ImportError:
            logger.warning("phue not installed. Install with: pip install phue")
            return False
        except Exception as e:
            logger.error(f"Error connecting to Hue bridge: {e}")
            return False
    
    async def turn_on_device(self, device_id: str) -> bool:
        """Turn on Hue device"""
        if not self.bridge:
            await self.connect()
        
        if self.bridge and device_id in self.devices:
            try:
                light_id = int(device_id.split('_')[1])
                light = self.bridge.lights[light_id]
                light.on = True
                self.devices[device_id]["state"] = "on"
                return True
            except Exception as e:
                logger.error(f"Error turning on {device_id}: {e}")
        return False
    
    async def turn_off_device(self, device_id: str) -> bool:
        """Turn off Hue device"""
        if not self.bridge:
            await self.connect()
        
        if self.bridge and device_id in self.devices:
            try:
                light_id = int(device_id.split('_')[1])
                light = self.bridge.lights[light_id]
                light.on = False
                self.devices[device_id]["state"] = "off"
                return True
            except Exception as e:
                logger.error(f"Error turning off {device_id}: {e}")
        return False
    
    async def set_brightness(self, device_id: str, brightness: int) -> bool:
        """Set Hue device brightness"""
        if not self.bridge:
            await self.connect()
        
        if self.bridge and device_id in self.devices:
            try:
                light_id = int(device_id.split('_')[1])
                light = self.bridge.lights[light_id]
                light.brightness = brightness
                self.devices[device_id]["brightness"] = brightness
                return True
            except Exception as e:
                logger.error(f"Error setting brightness for {device_id}: {e}")
        return False
    
    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get Hue device state"""
        if not self.bridge:
            await self.connect()
        
        if self.bridge and device_id in self.devices:
            try:
                light_id = int(device_id.split('_')[1])
                light = self.bridge.lights[light_id]
                return {
                    "id": device_id,
                    "name": light.name,
                    "state": "on" if light.on else "off",
                    "brightness": light.brightness,
                    "hue": light.hue,
                    "saturation": light.saturation,
                }
            except Exception as e:
                logger.error(f"Error getting state for {device_id}: {e}")
        return self.devices.get(device_id)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List Hue devices"""
        return list(self.devices.values())

