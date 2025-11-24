# Installation Guide

## Prerequisites

- Raspberry Pi 4 (8GB RAM, 128GB storage recommended)
- Docker and Docker Compose installed
- Python 3.11+ (if running without Docker)
- Microphone and speaker (for voice features)

## Docker Installation (Recommended)

1. **Clone or copy the platform files to your Raspberry Pi**

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the platform:**
   ```bash
   ./start.sh
   # Or manually:
   docker-compose up -d
   ```

4. **Access the web UI:**
   - Open browser to `http://localhost:5000`
   - API available at `http://localhost:8000`

## Manual Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL for marketplace:**
   ```bash
   # Install PostgreSQL or use Docker
   docker run -d --name marketplace-db \
     -e POSTGRES_DB=marketplace \
     -e POSTGRES_USER=marketplace_user \
     -e POSTGRES_PASSWORD=your_password \
     postgres:15-alpine
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the platform:**
   ```bash
   python -m platform.core.main
   ```

5. **Run the web UI (in another terminal):**
   ```bash
   python -m platform.web.app
   ```

## Post-Installation

1. **Set up license:**
   - Access Settings page in web UI
   - Enter your license key

2. **Configure voice (optional):**
   - Go to Voice Settings
   - Configure STT/TTS engines
   - Set wake word

3. **Install plugins:**
   - Browse Marketplace
   - Install desired plugins

## Troubleshooting

- **Docker issues:** Ensure Docker daemon is running
- **Port conflicts:** Change ports in .env file
- **Voice not working:** Check microphone permissions and audio setup
- **Plugin errors:** Check Docker logs: `docker logs plugin-<id>`

## Support

For issues and questions, contact support.



