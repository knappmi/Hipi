# Plugin API Reference

## Platform API

Plugins can call back to the platform API using the `PLATFORM_API_URL` environment variable.

### Available Endpoints

- `GET /api/v1/status` - Platform status
- `POST /api/v1/events` - Send events to platform
- `GET /api/v1/config` - Get platform configuration

## Plugin API Requirements

### Health Check

**Endpoint:** `GET /health`

**Response:**
- Status: 200 OK
- Body: JSON with status information

### Command Execution

**Endpoint:** `POST /command`

**Request Body:**
```json
{
  "command": "string",
  "params": {}
}
```

**Response:**
```json
{
  "success": boolean,
  "result": "string",
  "data": {}
}
```

### Status Reporting

**Endpoint:** `GET /status`

**Response:**
```json
{
  "plugin_id": "string",
  "status": "string",
  "data": {}
}
```

### Configuration

**Endpoint:** `POST /config`

**Request Body:**
```json
{
  "key": "value"
}
```

**Response:**
```json
{
  "success": boolean,
  "message": "string"
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses should include:
```json
{
  "success": false,
  "error": "Error message"
}
```



