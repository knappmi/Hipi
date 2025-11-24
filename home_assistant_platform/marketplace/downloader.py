"""Plugin download and distribution"""

import logging
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
import requests
from home_assistant_platform.config.settings import settings
from home_assistant_platform.marketplace.registry import MarketplaceRegistry

logger = logging.getLogger(__name__)


class PluginDownloader:
    """Handles plugin downloads from marketplace"""
    
    def __init__(self, registry: MarketplaceRegistry):
        self.registry = registry
        self.download_dir = Path(settings.plugins_dir) / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_plugin(self, plugin_id: str, user_id: str, download_url: Optional[str] = None) -> Optional[Path]:
        """Download a plugin package"""
        try:
            # Get plugin info
            plugin = self.registry.get_plugin(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return None
            
            # Check if user has purchased (if not free)
            if not plugin["is_free"]:
                purchases = self.registry.get_user_purchases(user_id)
                if not any(p["plugin_id"] == plugin_id for p in purchases):
                    logger.error(f"User {user_id} has not purchased plugin {plugin_id}")
                    return None
            
            # Get download URL
            url = download_url or plugin.get("download_url")
            if not url:
                logger.error(f"No download URL for plugin {plugin_id}")
                return None
            
            # Download plugin package
            logger.info(f"Downloading plugin {plugin_id} from {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = self.download_dir / f"{plugin_id}.zip"
            with open(temp_file, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            logger.info(f"Downloaded plugin {plugin_id} to {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to download plugin {plugin_id}: {e}")
            return None
    
    def extract_plugin(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract plugin package"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info(f"Extracted plugin to {extract_to}")
            return True
        except Exception as e:
            logger.error(f"Failed to extract plugin: {e}")
            return False
    
    def validate_plugin_package(self, zip_path: Path) -> bool:
        """Validate plugin package structure"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                
                # Check for manifest.json
                if "manifest.json" not in files:
                    logger.error("Plugin package missing manifest.json")
                    return False
                
                # Check for Dockerfile or valid structure
                has_dockerfile = any(f.endswith("Dockerfile") for f in files)
                if not has_dockerfile:
                    logger.warning("Plugin package missing Dockerfile")
                
                return True
        except Exception as e:
            logger.error(f"Failed to validate plugin package: {e}")
            return False

