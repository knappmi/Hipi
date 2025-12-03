#!/bin/bash
# Start both FastAPI and Flask services

# Ensure data directories exist and Vosk model is available
mkdir -p /app/data/vosk_models
# Copy model from build location to runtime location if needed
if [ ! -d "/app/data/vosk_models/vosk-model-small-en-us-0.15" ] && [ -d "/app/vosk-model" ]; then
    echo "Setting up Vosk model..."
    cp -r /app/vosk-model /app/data/vosk_models/vosk-model-small-en-us-0.15
    chmod -R 755 /app/data/vosk_models
fi

# Setup restricted terminal user
if [ -f "/app/docker/setup_terminal_user.sh" ]; then
    echo "Setting up terminal user..."
    bash /app/docker/setup_terminal_user.sh
fi

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $FASTAPI_PID $FLASK_PID 2>/dev/null
    wait $FASTAPI_PID $FLASK_PID 2>/dev/null
    exit 0
}

trap cleanup SIGTERM SIGINT

# Start FastAPI with uvicorn in background
cd /app
uvicorn home_assistant_platform.core.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 2

# Start Flask web UI in background
python -m home_assistant_platform.web.app &
FLASK_PID=$!

# Wait for both processes
wait $FASTAPI_PID $FLASK_PID

