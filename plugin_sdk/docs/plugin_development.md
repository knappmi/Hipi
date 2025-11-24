# Plugin Development Guide

## Introduction

This guide will help you develop plugins for the Home Assistant Platform. Plugins extend the platform's functionality by running in isolated Docker containers.

## Plugin Architecture

### Container-Based

Each plugin runs in its own Docker container with:
- Resource limits (CPU, memory)
- Network isolation (optional)
- Volume mounts for persistent data
- Environment variables for configuration

### API Communication

Plugins communicate with the platform via REST API:
- Platform → Plugin: Commands and configuration
- Plugin → Platform: Status and events (via webhooks)

## Required Endpoints

### GET /health

Health check endpoint. Must return 200 OK when plugin is healthy.

**Response:**
```json
{
  "status": "healthy",
  "plugin_id": "my-plugin"
}
```

### POST /command

Execute a command on the plugin.

**Request:**
```json
{
  "command": "turn_on",
  "params": {
    "device": "light1"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": "Device turned on"
}
```

### GET /status

Get current plugin status.

**Response:**
```json
{
  "plugin_id": "my-plugin",
  "status": "running",
  "data": {}
}
```

### POST /config

Update plugin configuration.

**Request:**
```json
{
  "setting1": "value1",
  "setting2": "value2"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated"
}
```

## Manifest File

The `manifest.json` file defines your plugin:

```json
{
  "id": "unique-plugin-id",
  "name": "Plugin Name",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Your Name",
  "image": "plugin-image:tag",
  "api_port": 8000,
  "cpu_limit": 0.5,
  "memory_limit": "512m",
  "network_access": true,
  "device_access": false
}
```

## Building and Testing

1. Build Docker image:
```bash
docker build -t my-plugin:latest .
```

2. Test locally:
```bash
docker run -p 8000:8000 my-plugin:latest
```

3. Test endpoints:
```bash
curl http://localhost:8000/health
```

## Best Practices

1. **Error Handling**: Always return proper error responses
2. **Logging**: Use structured logging
3. **Resource Usage**: Be mindful of CPU and memory limits
4. **Configuration**: Use environment variables for configuration
5. **Security**: Don't expose sensitive data in logs

## Marketplace Submission

1. Create plugin package (zip file)
2. Include manifest.json
3. Include Dockerfile
4. Include documentation
5. Submit to marketplace

## Support

For questions and support, contact the platform team.



