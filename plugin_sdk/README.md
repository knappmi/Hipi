# Plugin SDK

Welcome to the Home Assistant Platform Plugin SDK! This SDK provides everything you need to create plugins for the platform.

## Overview

Plugins are Docker containers that communicate with the platform via a REST API. Each plugin runs in isolation with resource limits and can be distributed through the marketplace.

## Quick Start

1. Use the plugin template to create a new plugin
2. Implement the required API endpoints
3. Create a Dockerfile
4. Build and test your plugin
5. Submit to the marketplace

## Plugin Structure

```
my-plugin/
├── manifest.json          # Plugin metadata
├── Dockerfile             # Docker build instructions
├── app.py                 # Plugin application
├── requirements.txt       # Python dependencies
└── README.md             # Plugin documentation
```

## Required API Endpoints

Your plugin must implement these endpoints:

- `GET /health` - Health check
- `POST /command` - Execute commands
- `GET /status` - Get plugin status
- `POST /config` - Update configuration

## Example Plugin

See `examples/` directory for example plugins.

## Documentation

Full documentation is available in `docs/`.



