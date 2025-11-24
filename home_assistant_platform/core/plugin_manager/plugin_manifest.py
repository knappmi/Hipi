"""Plugin manifest schema and validation"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PluginManifest(BaseModel):
    """Plugin manifest schema"""
    
    id: str = Field(..., description="Unique plugin identifier")
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    
    # Docker configuration
    image: str = Field(..., description="Docker image name")
    dockerfile: Optional[str] = Field(None, description="Path to Dockerfile if building from source")
    
    # Resource limits
    cpu_limit: Optional[float] = Field(None, description="CPU limit (0.0-1.0)")
    memory_limit: Optional[str] = Field(None, description="Memory limit (e.g., '512m')")
    
    # API endpoints
    api_port: int = Field(8000, description="Plugin API port")
    health_check_path: str = Field("/health", description="Health check endpoint path")
    command_endpoint: str = Field("/command", description="Command execution endpoint")
    status_endpoint: str = Field("/status", description="Status reporting endpoint")
    config_endpoint: str = Field("/config", description="Configuration endpoint")
    
    # Environment variables
    env_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    # Volume mounts
    volumes: List[str] = Field(default_factory=list, description="Volume mount paths")
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Plugin dependencies")
    
    # Permissions
    network_access: bool = Field(True, description="Allow network access")
    device_access: bool = Field(False, description="Allow device access (GPIO, etc.)")
    
    # Marketplace metadata
    price: Optional[float] = Field(None, description="Plugin price")
    category: Optional[str] = Field(None, description="Plugin category")
    tags: List[str] = Field(default_factory=list, description="Plugin tags")
    
    @classmethod
    def from_file(cls, manifest_path: Path) -> 'PluginManifest':
        """Load manifest from JSON file"""
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to load manifest from {manifest_path}: {e}")
            raise
    
    def to_file(self, manifest_path: Path):
        """Save manifest to JSON file"""
        try:
            with open(manifest_path, 'w') as f:
                json.dump(self.dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save manifest to {manifest_path}: {e}")
            raise
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return self.dict()

