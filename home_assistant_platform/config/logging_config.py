"""Logging configuration for the platform"""

import logging
import sys
from pathlib import Path
from home_assistant_platform.config.settings import settings


def setup_logging():
    """Configure logging for the platform"""
    
    # Create logs directory
    log_dir = settings.data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Set log level
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_dir / "platform.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("docker").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

