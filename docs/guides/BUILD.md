# Build Guide

This document explains how to build and develop the Hipi project using Poetry and Make.

## Prerequisites

### 1. Install Poetry

Poetry is a modern dependency management tool for Python. Install it using:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Or on macOS with Homebrew:
```bash
brew install poetry
```

Verify installation:
```bash
poetry --version
```

### 2. Install Docker and Docker Compose

Docker is required for running the platform in containers. Follow the installation guide in `DOCKER_INSTALLATION.md`.

## Quick Start

### Option 1: Using Make (Easiest)

1. Check all dependencies are installed:
   ```bash
   make check-deps
   ```

2. Quick start with Docker:
   ```bash
   make quick-start
   ```

3. View logs:
   ```bash
   make docker-logs
   ```

### Option 2: Using Poetry + Docker

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Build Docker image:
   ```bash
   docker compose build
   ```

3. Start services:
   ```bash
   docker compose up -d
   ```

### Option 3: Local Development (No Docker)

1. Install system dependencies (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
       portaudio19-dev \
       espeak \
       espeak-data \
       libespeak1 \
       alsa-utils
   ```

2. Install Python dependencies:
   ```bash
   poetry install
   ```

3. Setup environment:
   ```bash
   make setup-env
   # Edit config/.env
   ```

4. Run services:
   ```bash
   # Terminal 1: API Server
   make run-api

   # Terminal 2: Web UI
   make run-web

   # Terminal 3: Streamlit Dashboard (optional)
   make run-streamlit
   ```

## Common Commands

### Development Workflow

```bash
# Format code
make format

# Lint code
make lint

# Run tests
make test

# Run tests with coverage
make test-coverage
```

### Docker Workflow

```bash
# Build image
make docker-build

# Start containers
make docker-up

# Stop containers
make docker-down

# View logs
make docker-logs

# Open shell in container
make docker-shell

# Restart containers
make docker-restart
```

### Poetry Commands

```bash
# Install all dependencies
poetry install

# Install production dependencies only
poetry install --no-dev

# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Export to requirements.txt (for Docker)
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Maintenance

```bash
# Clean temporary files
make clean

# Clean everything including Docker volumes
make clean-all

# Update Poetry lock file
poetry lock
```

## Project Structure

```
Hipi/
├── Makefile              # Common build commands
├── pyproject.toml        # Poetry configuration and dependencies
├── requirements.txt      # Exported from Poetry (for Docker)
├── docker-compose.yml    # Docker Compose configuration
├── docker/
│   ├── Dockerfile        # Docker image definition
│   └── start_services.sh # Container startup script
├── home_assistant_platform/
│   └── ...               # Main application code
├── plugin_sdk/           # Plugin development SDK
├── config/               # Configuration files
└── tests/                # Test files
```

## Troubleshooting

### Poetry Installation Issues

If Poetry is not found after installation, add it to your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Docker Permission Issues

If you get permission errors with Docker:

```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Port Already in Use

If ports 5000, 8000, or 8501 are already in use, modify `docker-compose.yml` to use different ports.

### Audio Issues

See `AUDIO_SETUP.md` and `AUDIO_TROUBLESHOOTING.md` for audio configuration help.

## Environment Variables

Copy `config/.env.example` to `config/.env` and configure:

- `OPENAI_API_KEY` - Optional, for OpenAI TTS/STT
- `MARKETPLACE_API_KEY` - For marketplace integration
- `SECRET_KEY` - Change in production
- Database credentials

## Building for Production

1. Update version in `pyproject.toml`

2. Build Docker image:
   ```bash
   make docker-build
   ```

3. Tag and push to registry (if needed):
   ```bash
   docker tag home-assistant-platform:latest your-registry/hipi:1.0.0
   docker push your-registry/hipi:1.0.0
   ```

## Continuous Integration

Example GitHub Actions workflow:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: snok/install-poetry@v1
      - run: poetry install
      - run: poetry run make lint
      - run: poetry run make test
```


