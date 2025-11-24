"""Plugin manager - orchestrates plugin lifecycle"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

from home_assistant_platform.config.settings import settings
from home_assistant_platform.core.plugin_manager.plugin_manifest import PluginManifest
from home_assistant_platform.core.plugin_manager.docker_manager import DockerManager
from home_assistant_platform.core.plugin_manager.plugin_api import PluginAPI

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin lifecycle and operations"""
    
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.plugin_api = PluginAPI(docker_manager)
        self.plugins_dir = Path(settings.plugins_dir)
        self.installed_plugins: Dict[str, PluginManifest] = {}
        self._load_installed_plugins()
    
    def _load_installed_plugins(self):
        """Load all installed plugins"""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = PluginManifest.from_file(manifest_path)
                        self.installed_plugins[manifest.id] = manifest
                        logger.info(f"Loaded plugin: {manifest.name} v{manifest.version}")
                    except Exception as e:
                        logger.error(f"Failed to load plugin from {plugin_dir}: {e}")
    
    def install_plugin(self, plugin_dir: Path, manifest: Optional[PluginManifest] = None) -> bool:
        """Install a plugin"""
        try:
            # Load manifest if not provided
            if not manifest:
                manifest_path = plugin_dir / "manifest.json"
                if not manifest_path.exists():
                    logger.error(f"Manifest not found in {plugin_dir}")
                    return False
                manifest = PluginManifest.from_file(manifest_path)
            
            # Check if already installed
            if manifest.id in self.installed_plugins:
                logger.warning(f"Plugin {manifest.id} is already installed")
                return False
            
            # Copy plugin to plugins directory
            target_dir = self.plugins_dir / manifest.id
            if target_dir.exists():
                logger.warning(f"Plugin directory {target_dir} already exists")
            else:
                import shutil
                shutil.copytree(plugin_dir, target_dir)
            
            # Install Docker image
            if not self.docker_manager.install_plugin(manifest, target_dir):
                logger.error(f"Failed to install Docker image for {manifest.id}")
                return False
            
            # Save manifest
            manifest.to_file(target_dir / "manifest.json")
            
            # Register plugin
            self.installed_plugins[manifest.id] = manifest
            
            logger.info(f"Installed plugin: {manifest.name} v{manifest.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install plugin: {e}", exc_info=True)
            return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        try:
            if plugin_id not in self.installed_plugins:
                logger.warning(f"Plugin {plugin_id} is not installed")
                return False
            
            # Stop and remove container
            self.docker_manager.stop_plugin(plugin_id)
            self.docker_manager.remove_plugin(plugin_id)
            
            # Remove plugin directory
            plugin_dir = self.plugins_dir / plugin_id
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)
            
            # Unregister plugin
            del self.installed_plugins[plugin_id]
            
            logger.info(f"Uninstalled plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_id}: {e}")
            return False
    
    def start_plugin(self, plugin_id: str) -> bool:
        """Start a plugin"""
        if plugin_id not in self.installed_plugins:
            logger.error(f"Plugin {plugin_id} is not installed")
            return False
        
        manifest = self.installed_plugins[plugin_id]
        plugin_dir = self.plugins_dir / plugin_id
        
        return self.docker_manager.start_plugin(manifest, plugin_dir)
    
    def stop_plugin(self, plugin_id: str) -> bool:
        """Stop a plugin"""
        return self.docker_manager.stop_plugin(plugin_id)
    
    def restart_plugin(self, plugin_id: str) -> bool:
        """Restart a plugin"""
        if not self.stop_plugin(plugin_id):
            return False
        return self.start_plugin(plugin_id)
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin manifest"""
        return self.installed_plugins.get(plugin_id)
    
    def list_plugins(self) -> List[Dict]:
        """List all installed plugins"""
        plugins = []
        for plugin_id, manifest in self.installed_plugins.items():
            status = self.docker_manager.get_plugin_status(plugin_id)
            plugins.append({
                "id": manifest.id,
                "name": manifest.name,
                "version": manifest.version,
                "description": manifest.description,
                "status": status["status"] if status else "not_running",
                "author": manifest.author,
            })
        return plugins
    
    async def execute_plugin_command(self, plugin_id: str, command: str, params: Dict = None) -> Optional[Dict]:
        """Execute a command on a plugin"""
        if plugin_id not in self.installed_plugins:
            return None
        
        manifest = self.installed_plugins[plugin_id]
        return await self.plugin_api.execute_command(manifest, command, params)
    
    async def get_plugin_status(self, plugin_id: str) -> Optional[Dict]:
        """Get detailed plugin status"""
        if plugin_id not in self.installed_plugins:
            return None
        
        manifest = self.installed_plugins[plugin_id]
        container_status = self.docker_manager.get_plugin_status(plugin_id)
        plugin_status = await self.plugin_api.get_status(manifest)
        
        return {
            "container": container_status,
            "plugin": plugin_status,
            "manifest": manifest.to_dict(),
        }

