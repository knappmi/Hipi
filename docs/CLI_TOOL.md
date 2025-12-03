# CLI Tool (hap)

Command-line interface for managing the Home Assistant Platform.

## Installation

The CLI is installed automatically with the platform:

```bash
# After installing the platform
poetry install

# Or with pip
pip install -e .
```

## Usage

```bash
# General help
hap --help

# Command-specific help
hap devices --help
hap automations --help
```

## Commands

### Device Management

```bash
# List all devices
hap devices list

# List devices as JSON
hap devices list --format json

# Get device details
hap devices get <device_id>

# Turn on device
hap devices turn-on <device_id>

# Turn on with brightness
hap devices turn-on <device_id> --brightness 50

# Turn off device
hap devices turn-off <device_id>

# Set brightness
hap devices set-brightness <device_id> 75

# Discover new devices
hap devices discover
```

### Automation Management

```bash
# List automations
hap automations list

# Create automation from file
hap automations create --file automation.json

# Create automation inline
hap automations create --name "Morning Routine" --trigger "time:07:00" --action "scene:morning"

# Enable automation
hap automations enable <automation_id>

# Disable automation
hap automations disable <automation_id>

# List detected patterns
hap automations patterns

# List suggestions
hap automations suggestions
```

### Scene Management

```bash
# List scenes
hap scenes list

# Create scene from file
hap scenes create --file scene.json

# Create scene inline
hap scenes create --name "Movie Night" --devices '[{"device_id": "light_001", "state": "on", "brightness": 20}]'

# Activate scene
hap scenes activate <scene_id>

# Get scene details
hap scenes get <scene_id>
```

### Configuration

```bash
# Get all configuration
hap config get

# Get specific config key
hap config get <key>

# Set configuration
hap config set <key> <value>

# Show platform status
hap config status
```

### Plugin Management

```bash
# List plugins
hap plugins list

# Install plugin
hap plugins install <plugin_id>

# Uninstall plugin
hap plugins uninstall <plugin_id>

# Start plugin
hap plugins start <plugin_id>

# Stop plugin
hap plugins stop <plugin_id>
```

### Logs

```bash
# Tail logs
hap logs tail

# Tail with follow
hap logs tail --follow

# Show errors
hap logs errors
```

## Configuration

### API URL

By default, the CLI connects to `http://localhost:8000/api/v1`. You can override this:

```bash
# Set via environment variable
export HAP_API_URL=http://192.168.1.100:8000/api/v1
hap devices list

# Or set in config file (future feature)
```

## Examples

### Quick Device Control

```bash
# Turn on living room lights
hap devices turn-on light_living_room

# Set bedroom light to 30%
hap devices set-brightness light_bedroom 30

# Turn off all lights (requires automation)
hap automations create --name "Turn Off All" --trigger "voice:turn off all lights" --action "devices:turn_off:all"
```

### Scene Management

```bash
# Create movie night scene
cat > movie_night.json << EOF
{
  "name": "Movie Night",
  "device_states": [
    {"device_id": "light_living_room", "state": "on", "brightness": 20},
    {"device_id": "light_kitchen", "state": "off"}
  ]
}
EOF

hap scenes create --file movie_night.json

# Activate scene
hap scenes activate 1
```

### Automation Creation

```bash
# Create automation from file
cat > morning_routine.json << EOF
{
  "name": "Morning Routine",
  "trigger": {
    "type": "time",
    "time": "07:00"
  },
  "actions": [
    {
      "type": "scene",
      "scene_id": 1
    }
  ]
}
EOF

hap automations create --file morning_routine.json
```

## Error Handling

The CLI provides clear error messages:

```bash
# Connection error
$ hap devices list
Error: Could not connect to API at http://localhost:8000/api/v1. Is the platform running?

# API error
$ hap devices turn-on invalid_id
Error: API error: 404 - Device not found
```

## Integration with Scripts

The CLI can be used in shell scripts:

```bash
#!/bin/bash
# Morning automation script

# Activate morning scene
hap scenes activate 1

# Turn on coffee maker
hap devices turn-on coffee_maker

# Set thermostat
hap devices set-brightness thermostat 72
```

## Future Enhancements

- Interactive mode (`hap interactive`)
- Configuration file support
- API authentication
- Output formatting (CSV, YAML)
- Batch operations
- Command aliases
- Auto-completion

