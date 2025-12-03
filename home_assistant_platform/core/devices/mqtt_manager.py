"""MQTT device manager"""

import logging
import json
import asyncio
from typing import Dict, Optional, List, Any, Callable
import paho.mqtt.client as mqtt
from home_assistant_platform.core.automation.device_manager import DeviceManager
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class MQTTDeviceManager(DeviceManager):
    """MQTT-based device manager"""
    
    def __init__(self, broker_host: Optional[str] = None, broker_port: int = 1883,
                 username: Optional[str] = None, password: Optional[str] = None):
        self.broker_host = broker_host or settings.mqtt_broker_host
        self.broker_port = broker_port or settings.mqtt_broker_port
        self.username = username or settings.mqtt_username
        self.password = password or settings.mqtt_password
        self.source_name = "mqtt"
        
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.device_states: Dict[str, Dict[str, Any]] = {}
        self.state_callbacks: Dict[str, Callable] = {}
        
        # MQTT topic patterns
        self.command_topic_pattern = "homeassistant/{device_id}/set"
        self.state_topic_pattern = "homeassistant/{device_id}/state"
        self.discovery_topic = "homeassistant/+/config"
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=f"home_assistant_platform_{id(self)}")
            
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Connect
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            logger.info(f"MQTT client connecting to {self.broker_host}:{self.broker_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("MQTT client connected")
            
            # Subscribe to device states and discovery
            self.client.subscribe(self.state_topic_pattern.format(device_id="+"))
            self.client.subscribe(self.discovery_topic)
            logger.info("Subscribed to MQTT topics")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Parse device ID from topic
            parts = topic.split('/')
            if len(parts) >= 2:
                device_id = parts[1]
                
                if '/state' in topic:
                    # State update
                    state_data = json.loads(payload)
                    self.device_states[device_id] = state_data
                    
                    # Update device info
                    if device_id in self.devices:
                        self.devices[device_id].update(state_data)
                    
                    # Call callback if registered
                    if device_id in self.state_callbacks:
                        self.state_callbacks[device_id](state_data)
                    
                    logger.debug(f"State update for {device_id}: {state_data}")
                
                elif '/config' in topic:
                    # Device discovery
                    config_data = json.loads(payload)
                    self._handle_device_discovery(device_id, config_data)
        
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.warning("MQTT client disconnected")
    
    def _handle_device_discovery(self, device_id: str, config: Dict[str, Any]):
        """Handle device discovery message"""
        device_info = {
            "id": device_id,
            "name": config.get("name", device_id),
            "type": config.get("device_class", "switch"),
            "state": "unknown",
            "source": "mqtt",
            "config": config
        }
        
        self.devices[device_id] = device_info
        logger.info(f"Discovered MQTT device: {device_id} ({device_info['name']})")
    
    async def turn_on_device(self, device_id: str) -> bool:
        """Turn on device via MQTT"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            topic = self.command_topic_pattern.format(device_id=device_id)
            payload = json.dumps({"state": "ON"})
            
            result = self.client.publish(topic, payload, qos=1)
            result.wait_for_publish()
            
            logger.info(f"Published turn_on command to {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error turning on device {device_id}: {e}")
            return False
    
    async def turn_off_device(self, device_id: str) -> bool:
        """Turn off device via MQTT"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            topic = self.command_topic_pattern.format(device_id=device_id)
            payload = json.dumps({"state": "OFF"})
            
            result = self.client.publish(topic, payload, qos=1)
            result.wait_for_publish()
            
            logger.info(f"Published turn_off command to {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error turning off device {device_id}: {e}")
            return False
    
    async def set_brightness(self, device_id: str, brightness: int) -> bool:
        """Set device brightness via MQTT"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            topic = self.command_topic_pattern.format(device_id=device_id)
            payload = json.dumps({"brightness": brightness})
            
            result = self.client.publish(topic, payload, qos=1)
            result.wait_for_publish()
            
            logger.info(f"Published brightness command to {topic}: {brightness}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting brightness for {device_id}: {e}")
            return False
    
    async def set_color(self, device_id: str, color: str) -> bool:
        """Set device color via MQTT"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            topic = self.command_topic_pattern.format(device_id=device_id)
            # Convert color name to RGB if needed
            payload = json.dumps({"color": color})
            
            result = self.client.publish(topic, payload, qos=1)
            result.wait_for_publish()
            
            logger.info(f"Published color command to {topic}: {color}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting color for {device_id}: {e}")
            return False
    
    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device state"""
        # Return cached state
        if device_id in self.device_states:
            return self.device_states[device_id]
        
        # Return device info if available
        return self.devices.get(device_id)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List all discovered MQTT devices"""
        return list(self.devices.values())
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("MQTT client disconnected")

