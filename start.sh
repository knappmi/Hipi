#!/bin/bash
# Startup script for Home Assistant Platform

echo "Starting Home Assistant Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start services with docker compose (v2 syntax)
docker compose up -d

echo "Platform started!"
echo "Web UI: http://localhost:5000"
echo "API: http://localhost:8000"

