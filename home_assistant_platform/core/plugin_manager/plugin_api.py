"""Plugin API interface specification"""

import logging
import aiohttp
from typing import Dict, Optional, Any
from home_assistant_platform.core.plugin_manager.plugin_manifest import PluginManifest
from home_assistant_platform.core.plugin_manager.docker_manager import DockerManager

logger = logging.getLogger(__name__)


class PluginAPI:
    """Interface for communicating with plugins via REST API"""
    
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
    
    def _get_plugin_url(self, manifest: PluginManifest) -> Optional[str]:
        """Get plugin API URL"""
        status = self.docker_manager.get_plugin_status(manifest.id)
        if not status or status["status"] != "running":
            return None
        
        # Get port mapping
        ports = status.get("ports", {})
        if not ports:
            return None
        
        # Find the mapped port
        for container_port, host_ports in ports.items():
            if container_port.startswith(f"{manifest.api_port}/"):
                if host_ports:
                    host_port = host_ports[0]["HostPort"]
                    return f"http://localhost:{host_port}"
        
        return None
    
    async def health_check(self, manifest: PluginManifest) -> bool:
        """Check if plugin is healthy"""
        url = self._get_plugin_url(manifest)
        if not url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}{manifest.health_check_path}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed for plugin {manifest.id}: {e}")
            return False
    
    async def execute_command(self, manifest: PluginManifest, command: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Execute a command on the plugin"""
        url = self._get_plugin_url(manifest)
        if not url:
            logger.error(f"Plugin {manifest.id} is not running")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{url}{manifest.command_endpoint}",
                    json={"command": command, "params": params or {}},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Command execution failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to execute command on plugin {manifest.id}: {e}")
            return None
    
    async def get_status(self, manifest: PluginManifest) -> Optional[Dict]:
        """Get plugin status"""
        url = self._get_plugin_url(manifest)
        if not url:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}{manifest.status_endpoint}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"Failed to get status from plugin {manifest.id}: {e}")
            return None
    
    async def update_config(self, manifest: PluginManifest, config: Dict[str, Any]) -> bool:
        """Update plugin configuration"""
        url = self._get_plugin_url(manifest)
        if not url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{url}{manifest.config_endpoint}",
                    json=config,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to update config for plugin {manifest.id}: {e}")
            return False

