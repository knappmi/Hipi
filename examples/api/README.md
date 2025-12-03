# API Examples

Code examples for using the Home Assistant Platform API.

## Python Examples

### Device Control
```bash
python examples/api/python/device_control.py
```

### Automation Creation
```bash
python examples/api/python/automation_creation.py
```

### Scene Management
```bash
python examples/api/python/scene_management.py
```

## JavaScript/Node.js Examples

```bash
npm install axios
node examples/api/javascript/nodejs_examples.js
```

## cURL Examples

```bash
chmod +x examples/api/curl/api_examples.sh
./examples/api/curl/api_examples.sh
```

## API Base URL

Default: `http://localhost:8000/api/v1`

Override by setting environment variable:
```bash
export API_BASE_URL=http://your-server:8000/api/v1
```

## Authentication

Currently, the API doesn't require authentication for local access. For production, API keys will be required.

## More Examples

See the [API Documentation](http://localhost:8000/docs) for interactive API explorer and more examples.

