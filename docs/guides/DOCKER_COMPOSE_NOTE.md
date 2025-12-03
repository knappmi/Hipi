# Docker Compose Command Note

## Docker Compose v2 vs v1

Modern Docker installations use **Docker Compose v2**, which uses:
```bash
docker compose  # (with a space)
```

The older standalone version used:
```bash
docker-compose  # (with a hyphen)
```

## Solution

You have two options:

### Option 1: Use the new syntax (Recommended)
Always use `docker compose` (with a space):
```bash
docker compose up -d
docker compose down
docker compose ps
docker compose logs
```

### Option 2: Create an alias (for compatibility)
An alias has been added to your `.bashrc` file. After restarting your shell or running `source ~/.bashrc`, you can use either:
- `docker compose` (new syntax)
- `docker-compose` (old syntax - via alias)

## Verify Your Setup

Check which version you have:
```bash
docker compose version
```

If you see a version number, you're using Docker Compose v2 (plugin version).

## Updated Commands

All commands in this project use `docker compose` (with space) for compatibility with Docker Compose v2.



