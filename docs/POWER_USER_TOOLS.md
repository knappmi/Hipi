# Power User Tools

Advanced features for power users and advanced automation.

## Webhooks

### Create Webhook

```bash
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IFTTT Integration",
    "url": "https://maker.ifttt.com/trigger/device_changed/with/key/YOUR_KEY",
    "method": "POST",
    "trigger_on_device_change": true,
    "enabled": true
  }'
```

### Webhook Triggers

- **Device Changes**: Trigger when any device state changes
- **Scene Activation**: Trigger when a scene is activated
- **Automation Run**: Trigger when an automation executes
- **Voice Commands**: Trigger on voice commands
- **Custom Events**: Trigger on custom event types

### Custom Payload Templates

Use Jinja2 templates for custom payloads:

```json
{
  "name": "Custom Webhook",
  "url": "https://api.example.com/webhook",
  "payload_template": "{\"device\": \"{{ event_data.device_id }}\", \"state\": \"{{ event_data.state }}\", \"time\": \"{{ timestamp }}\"}",
  "trigger_on_device_change": true
}
```

### Webhook Logs

View webhook execution logs:

```bash
curl http://localhost:8000/api/v1/webhooks/1/logs
```

## Advanced Automation Scripting

### Python Scripts

Execute Python scripts in automations:

```python
# Example: Complex device control logic
devices = context.get('devices', [])
for device in devices:
    if device['type'] == 'light' and device['state'] == 'on':
        # Turn off lights during day
        if context.get('time_of_day') == 'day':
            turn_off_device(device['id'])
```

### JavaScript Scripts

Execute JavaScript scripts:

```javascript
// Example: Conditional logic
const devices = context.devices || [];
devices.forEach(device => {
    if (device.type === 'light' && device.brightness > 80) {
        // Dim bright lights
        setBrightness(device.id, 50);
    }
});
```

### Execute Script via API

```bash
curl -X POST http://localhost:8000/api/v1/automation/scripts/execute \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "script": "print(\"Hello from automation!\")",
    "context": {"device_id": "light_001"}
  }'
```

## Custom Voice Commands

### Training Custom Intents

```bash
# Use the enhanced voice API
curl -X POST http://localhost:8000/api/v1/voice/enhanced/wake-words/train \
  -H "Content-Type: application/json" \
  -d '{
    "wake_word": "custom_command",
    "samples": ["path/to/sample1.wav", "path/to/sample2.wav"]
  }'
```

## Performance Monitoring

### System Metrics

```bash
# Get system performance (future feature)
curl http://localhost:8000/api/v1/telemetry/metrics
```

### Device Response Times

Track device response times in automation logs.

## Advanced Scheduling

### Cron-like Scheduling

```json
{
  "name": "Daily Backup",
  "trigger": {
    "type": "cron",
    "expression": "0 2 * * *"  // 2 AM daily
  },
  "actions": [{"type": "webhook", "webhook_id": 1}]
}
```

## Integration Examples

### IFTTT Integration

```bash
# Create IFTTT webhook
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IFTTT",
    "url": "https://maker.ifttt.com/trigger/home_event/with/key/YOUR_KEY",
    "trigger_on_device_change": true,
    "trigger_on_scene_activate": true
  }'
```

### Zapier Integration

```bash
# Create Zapier webhook
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zapier",
    "url": "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK_ID/",
    "trigger_on_automation_run": true
  }'
```

### Home Assistant Integration

```bash
# Send events to Home Assistant
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home Assistant",
    "url": "http://homeassistant.local:8123/api/webhook/YOUR_WEBHOOK_ID",
    "method": "POST",
    "trigger_on_device_change": true,
    "payload_template": "{\"entity_id\": \"{{ event_data.device_id }}\", \"state\": \"{{ event_data.state }}\"}"
  }'
```

## CLI Usage

### Webhook Management

```bash
# List webhooks (future CLI command)
hap webhooks list

# Create webhook
hap webhooks create --name "IFTTT" --url "https://..." --trigger device-change

# Trigger webhook
hap webhooks trigger 1 --event-type device_change --event-data '{"device_id": "light_001"}'
```

## Best Practices

1. **Webhook Security**: Always use secrets for webhooks
2. **Error Handling**: Monitor webhook logs for failures
3. **Rate Limiting**: Be mindful of webhook rate limits
4. **Script Safety**: Test scripts in development before production
5. **Template Testing**: Test payload templates before enabling

## Examples

See `examples/power_user/` for complete examples:
- Webhook integrations
- Advanced automation scripts
- Custom voice commands
- Performance monitoring

