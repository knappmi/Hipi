# Logging Guide

## View Logs

### Watch All Services (Real-time)
```bash
sudo docker compose logs -f
```

### Watch Platform Service Only
```bash
sudo docker compose logs -f platform
```

### Watch Last N Lines
```bash
# Last 50 lines
sudo docker compose logs --tail 50 platform

# Last 100 lines
sudo docker compose logs --tail 100 platform
```

### Watch Specific Service
```bash
# Platform
sudo docker compose logs -f platform

# Database
sudo docker compose logs -f marketplace-db
```

## Filter Logs

### Filter by Keyword
```bash
# Voice-related logs
sudo docker compose logs -f platform | grep -i "voice\|wake\|tts\|stt"

# Error logs only
sudo docker compose logs -f platform | grep -i "error\|exception\|failed"

# Plugin logs
sudo docker compose logs -f platform | grep -i "plugin"

# Wake word detection
sudo docker compose logs -f platform | grep -i "wake word"
```

### Filter by Time
```bash
# Logs since last 10 minutes
sudo docker compose logs --since 10m platform

# Logs since last hour
sudo docker compose logs --since 1h platform
```

## Log Files

Logs are also saved to files inside the container:
- Location: `/app/data/logs/platform.log`
- View in container:
  ```bash
  sudo docker compose exec platform tail -f /app/data/logs/platform.log
  ```

## Useful Commands

### Follow logs with timestamps
```bash
sudo docker compose logs -f --timestamps platform
```

### Follow logs and filter
```bash
sudo docker compose logs -f platform 2>&1 | grep -i "voice"
```

### Export logs to file
```bash
sudo docker compose logs platform > platform_logs.txt
```

### Clear logs (restart container)
```bash
sudo docker compose restart platform
```

## Common Log Patterns

### Watch for voice activity
```bash
sudo docker compose logs -f platform | grep -E "voice|wake|intent|speak"
```

### Watch for errors
```bash
sudo docker compose logs -f platform | grep -E "ERROR|Exception|Failed"
```

### Watch for plugin activity
```bash
sudo docker compose logs -f platform | grep -E "plugin|container|docker"
```

### Watch for API requests
```bash
sudo docker compose logs -f platform | grep -E "GET|POST|PUT|DELETE"
```

## Quick Reference

```bash
# Most common: Watch platform logs in real-time
sudo docker compose logs -f platform

# Watch with timestamps
sudo docker compose logs -f --timestamps platform

# Watch and filter for voice
sudo docker compose logs -f platform | grep -i voice

# Last 100 lines
sudo docker compose logs --tail 100 platform
```



