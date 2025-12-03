.PHONY: help install install-dev build up down restart logs shell test clean format lint docker-build docker-up docker-down docker-logs poetry-install poetry-update poetry-lock

# Default target
help:
	@echo "Hipi - Home Assistant Platform"
	@echo ""
	@echo "Available targets:"
	@echo "  make help              - Show this help message"
	@echo ""
	@echo "Development:"
	@echo "  make install           - Install production dependencies with Poetry"
	@echo "  make install-dev       - Install development dependencies"
	@echo "  make poetry-install    - Install dependencies using Poetry"
	@echo "  make poetry-update     - Update Poetry dependencies"
	@echo "  make poetry-lock       - Update Poetry lock file"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format            - Format code with black"
	@echo "  make lint              - Lint code with ruff and mypy"
	@echo "  make test              - Run tests with pytest"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker image"
	@echo "  make docker-up         - Start Docker containers"
	@echo "  make docker-down       - Stop Docker containers"
	@echo "  make docker-restart    - Restart Docker containers"
	@echo "  make docker-logs       - View Docker logs"
	@echo "  make docker-shell      - Open shell in Docker container"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             - Clean temporary files and caches"
	@echo "  make clean-all         - Clean everything including Docker volumes"

# Poetry installation
install:
	poetry install --no-dev

install-dev:
	poetry install

poetry-install:
	poetry install

poetry-update:
	poetry update

poetry-lock:
	poetry lock --no-update

# Code formatting and linting
format:
	poetry run black home_assistant_platform plugin_sdk tests
	poetry run ruff check --fix home_assistant_platform plugin_sdk tests

lint:
	poetry run ruff check home_assistant_platform plugin_sdk tests
	poetry run mypy home_assistant_platform --ignore-missing-imports

# Testing
test:
	poetry run pytest -v tests/

test-integration:
	poetry run python -m pytest tests/integration/ -v

test-coverage:
	poetry run pytest --cov=home_assistant_platform --cov-report=html --cov-report=term

# Docker commands
docker-build:
	docker compose build --no-cache

docker-build-platform:
	docker compose build --no-cache platform

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-restart:
	docker compose restart

docker-logs:
	docker compose logs -f platform

docker-shell:
	docker compose exec platform /bin/bash

docker-clean:
	docker compose down -v
	docker system prune -f

# Local development (without Docker)
run-api:
	poetry run uvicorn home_assistant_platform.core.main:app --host 0.0.0.0 --port 8000 --reload

run-web:
	poetry run python -m home_assistant_platform.web.app

run-streamlit:
	poetry run streamlit run home_assistant_platform/web/streamlit_app.py --server.port 8501

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf dist/
	rm -rf build/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "Cleaned temporary files and caches"

clean-all: clean docker-clean
	rm -rf .venv/
	rm -rf poetry.lock
	@echo "Cleaned everything including Docker volumes"

# Export requirements.txt from Poetry
export-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# Setup development environment
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make run-api' to start the API server"
	@echo "Run 'make run-web' to start the Flask web UI"
	@echo "Run 'make run-streamlit' to start the Streamlit dashboard"

# Quick start with Docker
quick-start: docker-build docker-up
	@echo "Platform is starting..."
	@sleep 5
	@echo "Web UI: http://localhost:5000"
	@echo "API: http://localhost:8000"
	@echo "Streamlit: http://localhost:8501 (if enabled)"
	@echo "View logs with: make docker-logs"

# Git helpers
git-status:
	git status

git-commit:
	git add .
	git commit -m "$(MSG)"

git-push:
	git push origin main

# Environment setup
setup-env:
	@if [ ! -f config/.env ]; then \
		echo "Creating config/.env from template..."; \
		cp config/.env.example config/.env 2>/dev/null || echo "# Add your environment variables here" > config/.env; \
		echo "Please edit config/.env with your settings"; \
	fi

# Check system requirements
check-deps:
	@echo "Checking system dependencies..."
	@command -v docker >/dev/null 2>&1 || { echo "Docker is not installed"; exit 1; }
	@command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose is not installed"; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo "Poetry is not installed. Install from: https://python-poetry.org/docs/#installation"; exit 1; }
	@echo "All dependencies are installed!"

# Database operations
db-migrate:
	docker compose exec platform alembic upgrade head

db-reset:
	docker compose down -v
	docker compose up -d marketplace-db
	@echo "Database reset complete"


