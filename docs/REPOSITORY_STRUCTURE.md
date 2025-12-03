# Repository Structure

## Root Directory

The root directory contains only essential project files:

### Project Configuration Files
- `README.md` - Main project documentation
- `pyproject.toml` - Poetry configuration
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker Compose configuration
- `Makefile` - Build and development commands
- `.gitignore` - Git ignore rules

## Directory Structure

```
.
├── README.md                    # Main documentation
├── Makefile                     # Build commands
├── docker-compose.yml           # Docker configuration
├── pyproject.toml              # Poetry config
├── requirements.txt            # Dependencies
├── .gitignore                  # Git ignore
│
├── home_assistant_platform/    # Main application code
│   ├── core/                   # Core functionality
│   ├── config/                 # Configuration
│   ├── web/                    # Web UI
│   └── ...
│
├── docs/                       # Documentation
│   ├── README.md              # Documentation index
│   ├── guides/                # Setup and usage guides
│   └── *.md                   # Feature documentation
│
├── scripts/                    # Utility scripts
│   ├── start.sh               # Start script
│   └── *.sh                   # Other scripts
│
├── tests/                      # Test files
│   ├── __init__.py            # Test package
│   ├── test_*.py              # Unit tests
│   └── integration/           # Integration tests
│       └── test_*.py          # Integration test scripts
│
├── data/                       # Data files (gitignored)
│   ├── backups/               # Backup files
│   └── logs/                  # Log files
│
├── plugin_sdk/                 # Plugin SDK
├── plugins/                    # Installed plugins
└── docker/                     # Docker files
```

## File Organization Rules

### Root Directory
- **Keep**: Project configuration files (Makefile, docker-compose.yml, etc.)
- **Keep**: Main README.md
- **Move**: Everything else to appropriate subdirectories

### Documentation (`docs/`)
- Feature documentation: `docs/*.md`
- Setup guides: `docs/guides/*.md`
- Documentation index: `docs/README.md`

### Scripts (`scripts/`)
- All shell scripts (`.sh` files)
- Utility scripts
- Setup scripts

### Tests (`tests/`)
- Unit tests: `tests/test_*.py`
- Integration tests: `tests/integration/test_*.py`

### Data (`data/`)
- Backup files: `data/backups/`
- Log files: `data/logs/`
- Database files: `data/backups/`

## Adding New Files

### Documentation
- Add to `docs/` for feature docs
- Add to `docs/guides/` for setup/usage guides

### Scripts
- Add to `scripts/` for any shell scripts

### Tests
- Add to `tests/` for unit tests
- Add to `tests/integration/` for integration tests

### Data Files
- Add to `data/` (gitignored by default)
