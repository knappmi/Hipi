# Device Control System

A comprehensive device control system that supports multiple device protocols and integrates with the predictive automation system.

## Features

### ✅ Implemented

1. **Unified Device Manager**
   - Combines multiple device sources (Mock, MQTT, WiFi)
   - Single API for all device types
   - Automatic device discovery

2. **MQTT Device Support**
   - Full MQTT client implementation
   - Device discovery via MQTT topics
   - State updates via MQTT subscriptions
   - Command publishing for device control

3. **WiFi Device Discovery**
   - TP-Link Kasa device support (ready for python-kasa)
   - Philips Hue device support (ready for phue)
   - Network device discovery framework

4. **Device Registry**
   - Centralized device management
   - Device source tracking
   - State caching and updates

5. **REST API**
   - List all devices
   - Get device information
   - Control devices (turn on/off, brightness, color, temperature)
   - Device discovery
   - Manual device addition/removal

6. **Automation Integration**
   - Automatic action recording for pattern learning
   - Seamless integration with automation system
   - Device actions trigger pattern detection

## API Endpoints

### List Devices
```bash
GET /api/v1/devices
```

### Get Device Info
```bash
GET /api/v1/devices/{device_id}
```

### Turn On Device
```bash
POST /api/v1/devices/{device_id}/turn_on
```

### Turn Off Device
```bash
POST /api/v1/devices/{device_id}/turn_off
```

### Control Device (Generic)
```bash
POST /api/v1/devices/{device_id}/control
Content-Type: application/json

{
  "action": "set_brightness",
  "value": 75
}
```

### Discover WiFi Devices
```bash
POST /api/v1/devices/discover
```

### Add Device Manually
```bash
POST /api/v1/devices/add
Content-Type: application/json

{
  "id": "custom_device",
  "name": "Custom Device",
  "type": "light",
  "state": "off"
}
```

## Device Types Supported

- **Lights**: Turn on/off, brightness control, color control
- **Switches**: Turn on/off
- **Thermostats**: Temperature control
- **Generic**: Extensible for any device type

## Device Sources

1. **Mock Devices** (Default)
   - For testing and development
   - 4 pre-configured devices

2. **MQTT Devices**
   - Auto-discovered via MQTT topics
   - Supports Home Assistant MQTT format
   - Real-time state updates

3. **WiFi Devices** (Optional)
   - TP-Link Kasa: Install `python-kasa`
   - Philips Hue: Install `phue`

## Integration with Automation

Every device action is automatically recorded for pattern learning:

```python
# When you turn on a device via API
POST /api/v1/devices/living_room_light/turn_on

# The system automatically:
# 1. Executes the device action
# 2. Records the action with timestamp
# 3. Triggers pattern detection
# 4. Generates automation suggestions if patterns detected
```

## Usage Examples

### Control a Light
```bash
# Turn on
curl -X POST http://localhost:8000/api/v1/devices/living_room_light/turn_on

# Set brightness
curl -X POST http://localhost:8000/api/v1/devices/living_room_light/control \
  -H "Content-Type: application/json" \
  -d '{"action": "set_brightness", "value": 50}'

# Turn off
curl -X POST http://localhost:8000/api/v1/devices/living_room_light/turn_off
```

### Control Thermostat
```bash
curl -X POST http://localhost:8000/api/v1/devices/thermostat/control \
  -H "Content-Type: application/json" \
  -d '{"action": "set_temperature", "value": 72}'
```

## MQTT Configuration

Set in environment variables or config:
- `MQTT_BROKER_HOST`: MQTT broker hostname (default: localhost)
- `MQTT_BROKER_PORT`: MQTT broker port (default: 1883)
- `MQTT_USERNAME`: MQTT username (optional)
- `MQTT_PASSWORD`: MQTT password (optional)

## WiFi Device Setup

### TP-Link Kasa
```bash
pip install python-kasa
```

Devices will be auto-discovered on the network.

### Philips Hue
```bash
pip install phue
```

Bridge IP can be configured or auto-discovered.

## Architecture

```
UnifiedDeviceManager
├── DeviceRegistry
│   ├── MockDeviceManager (default)
│   ├── MQTTDeviceManager (if MQTT configured)
│   ├── TPLinkDeviceManager (if python-kasa installed)
│   └── HueDeviceManager (if phue installed)
└── PatternLearner (records all actions)
```

## Testing

Run the test script:
```bash
python3 test_device_control.py
```

## Future Enhancements

- Zigbee/Z-Wave bridge support
- Device grouping and rooms
- Device scenes
- Energy monitoring per device
- Device scheduling
- Voice control integration ("Turn on living room lights")

## Status

✅ **Fully Functional**
- Device control working
- API endpoints tested
- Automation integration complete
- Ready for MQTT and WiFi device integration

