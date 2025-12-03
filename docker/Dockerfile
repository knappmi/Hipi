FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    alsa-utils \
    pulseaudio \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY home_assistant_platform/ ./home_assistant_platform/

# Create necessary directories
RUN mkdir -p /app/plugins /app/data /app/data/vosk_models

# Download and extract Vosk model to a persistent location
RUN cd /tmp && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
    unzip -q vosk-model-small-en-us-0.15.zip && \
    mv vosk-model-small-en-us-0.15 /app/vosk-model && \
    rm vosk-model-small-en-us-0.15.zip && \
    chmod -R 755 /app/vosk-model

# Expose ports
EXPOSE 8000 5000

# Copy startup scripts
COPY docker/start_services.sh /app/start_services.sh
COPY docker/setup_terminal_user.sh /app/docker/setup_terminal_user.sh
RUN chmod +x /app/start_services.sh /app/docker/setup_terminal_user.sh

# Run both services
CMD ["/app/start_services.sh"]

