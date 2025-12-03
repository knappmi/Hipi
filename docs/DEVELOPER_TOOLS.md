# Developer Tools

Complete guide to developer tools for the Home Assistant Platform.

## CLI Tool (hap)

See [CLI_TOOL.md](CLI_TOOL.md) for complete CLI documentation.

### Quick Start

```bash
# After installation
hap devices list
hap scenes activate 1
hap config status
```

## API Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# List devices
devices = requests.get(f"{API_URL}/devices").json()

# Turn on device
requests.post(
    f"{API_URL}/devices/light_001/control",
    json={"action": "turn_on", "brightness": 50}
)
```

See `examples/api/python/` for complete examples.

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000/api/v1';

// List devices
const devices = await axios.get(`${API_URL}/devices`);

// Turn on device
await axios.post(`${API_URL}/devices/light_001/control`, {
    action: 'turn_on',
    brightness: 50
});
```

See `examples/api/javascript/` for complete examples.

### cURL

```bash
# List devices
curl http://localhost:8000/api/v1/devices

# Turn on device
curl -X POST http://localhost:8000/api/v1/devices/light_001/control \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on", "brightness": 50}'
```

See `examples/api/curl/` for complete examples.

## Plugin Development

### Create New Plugin

```bash
# Use plugin creation script
./scripts/plugin_create.sh my-plugin

# Or manually copy from template
cp -r plugin_sdk/template plugins/my-plugin
```

### Plugin Structure

```
my-plugin/
├── manifest.json      # Plugin metadata
├── Dockerfile         # Docker build file
├── app.py            # Plugin application
├── requirements.txt   # Dependencies
└── README.md         # Documentation
```

### Build and Test

```bash
# Build plugin
docker build -t my-plugin:latest plugins/my-plugin

# Test locally
docker run -p 8000:8000 my-plugin:latest

# Test endpoints
curl http://localhost:8000/health
```

See `plugin_sdk/` for complete plugin SDK documentation.

## Testing Framework

### Test Client

```python
from home_assistant_platform.tests.utils.test_client import TestClient

client = TestClient()

# Test API calls
devices = client.get('devices')
client.post('devices/light_001/control', {'action': 'turn_on'})
```

### Mock Devices

```python
from home_assistant_platform.tests.utils.test_client import MockDevice

device = MockDevice("light_001", "Test Light")
device.turn_on(brightness=50)
assert device.is_on
assert device.brightness == 50
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/integration/test_api_basic.py

# Run with coverage
pytest --cov=home_assistant_platform
```

## Development Mode

### Hot Reload

```bash
# Run with hot reload (development)
poetry run uvicorn home_assistant_platform.core.main:app --reload
```

### Debug Mode

Set environment variable:
```bash
export DEBUG=true
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Code Examples

All code examples are in `examples/`:
- `examples/api/python/` - Python examples
- `examples/api/javascript/` - Node.js examples
- `examples/api/curl/` - cURL examples

## Best Practices

1. **Use the CLI** for common operations
2. **Use API examples** as starting points
3. **Test plugins** before publishing
4. **Follow plugin SDK** guidelines
5. **Write tests** for your code

## Getting Help

- **API Docs**: http://localhost:8000/docs
- **CLI Help**: `hap --help`
- **Plugin SDK**: See `plugin_sdk/docs/`
- **Examples**: See `examples/`

