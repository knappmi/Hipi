"""Docker container management for plugins"""

import logging
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import docker
from docker.errors import DockerException, ImageNotFound, ContainerError

from home_assistant_platform.config.settings import settings
from home_assistant_platform.core.plugin_manager.plugin_manifest import PluginManifest

logger = logging.getLogger(__name__)


class DockerManager:
    """Manages Docker containers for plugins"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()  # Test connection
            logger.info("Docker client initialized")
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    def install_plugin(self, manifest: PluginManifest, plugin_dir: Path) -> bool:
        """Install a plugin by building/pulling its Docker image"""
        try:
            # Check if image exists
            try:
                self.client.images.get(manifest.image)
                logger.info(f"Image {manifest.image} already exists")
                return True
            except ImageNotFound:
                pass
            
            # Build from Dockerfile if provided
            if manifest.dockerfile:
                dockerfile_path = plugin_dir / manifest.dockerfile
                if dockerfile_path.exists():
                    logger.info(f"Building image from {dockerfile_path}")
                    self.client.images.build(
                        path=str(plugin_dir),
                        dockerfile=manifest.dockerfile,
                        tag=manifest.image,
                        rm=True
                    )
                    return True
            
            # Try to pull from registry
            try:
                logger.info(f"Pulling image {manifest.image}")
                self.client.images.pull(manifest.image)
                return True
            except Exception as e:
                logger.error(f"Failed to pull image {manifest.image}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install plugin {manifest.id}: {e}")
            return False
    
    def start_plugin(self, manifest: PluginManifest, plugin_dir: Path) -> bool:
        """Start a plugin container"""
        try:
            container_name = f"plugin-{manifest.id}"
            
            # Check if container already exists
            try:
                container = self.client.containers.get(container_name)
                if container.status == "running":
                    logger.info(f"Plugin {manifest.id} is already running")
                    return True
                elif container.status == "exited":
                    container.start()
                    logger.info(f"Started existing container for plugin {manifest.id}")
                    return True
            except docker.errors.NotFound:
                pass
            
            # Prepare container configuration
            container_config = self._prepare_container_config(manifest, plugin_dir)
            
            # Create and start container
            container = self.client.containers.run(
                manifest.image,
                name=container_name,
                detach=True,
                **container_config
            )
            
            logger.info(f"Started container for plugin {manifest.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start plugin {manifest.id}: {e}")
            return False
    
    def _prepare_container_config(self, manifest: PluginManifest, plugin_dir: Path) -> Dict:
        """Prepare Docker container configuration"""
        config = {
            "restart_policy": {"Name": "unless-stopped"},
            "network": settings.plugin_network,
            "environment": {
                "PLUGIN_ID": manifest.id,
                "PLUGIN_NAME": manifest.name,
                "PLATFORM_API_URL": f"http://platform:8000/api/v1",
                **manifest.env_vars
            },
            "ports": {f"{manifest.api_port}/tcp": None},  # Auto-assign port
        }
        
        # Resource limits
        if manifest.cpu_limit:
            config["cpu_period"] = 100000
            config["cpu_quota"] = int(manifest.cpu_limit * 100000)
        else:
            config["cpu_period"] = 100000
            config["cpu_quota"] = int(settings.plugin_max_cpu * 100000)
        
        if manifest.memory_limit:
            config["mem_limit"] = manifest.memory_limit
        else:
            config["mem_limit"] = settings.plugin_max_memory
        
        # Volume mounts
        volumes = {}
        for volume in manifest.volumes:
            host_path = plugin_dir / volume.lstrip("/")
            if host_path.exists():
                volumes[str(host_path)] = {"bind": volume, "mode": "rw"}
        
        if volumes:
            config["volumes"] = volumes
        
        # Device access (for GPIO, etc.)
        if manifest.device_access:
            config["devices"] = ["/dev/gpiomem:/dev/gpiomem"]
        
        # Network isolation
        if not manifest.network_access:
            config["network_mode"] = "none"
        
        return config
    
    def stop_plugin(self, plugin_id: str) -> bool:
        """Stop a plugin container"""
        try:
            container_name = f"plugin-{plugin_id}"
            container = self.client.containers.get(container_name)
            container.stop()
            logger.info(f"Stopped plugin {plugin_id}")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Container for plugin {plugin_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to stop plugin {plugin_id}: {e}")
            return False
    
    def remove_plugin(self, plugin_id: str) -> bool:
        """Remove a plugin container"""
        try:
            container_name = f"plugin-{plugin_id}"
            container = self.client.containers.get(container_name)
            container.remove(force=True)
            logger.info(f"Removed plugin {plugin_id}")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Container for plugin {plugin_id} not found")
            return True  # Already removed
        except Exception as e:
            logger.error(f"Failed to remove plugin {plugin_id}: {e}")
            return False
    
    def get_plugin_status(self, plugin_id: str) -> Optional[Dict]:
        """Get status of a plugin container"""
        try:
            container_name = f"plugin-{plugin_id}"
            container = self.client.containers.get(container_name)
            
            return {
                "id": plugin_id,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "",
                "created": container.attrs["Created"],
                "ports": container.attrs.get("NetworkSettings", {}).get("Ports", {}),
            }
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.error(f"Failed to get status for plugin {plugin_id}: {e}")
            return None
    
    def list_plugins(self) -> List[Dict]:
        """List all plugin containers"""
        plugins = []
        try:
            containers = self.client.containers.list(all=True, filters={"name": "plugin-"})
            for container in containers:
                plugin_id = container.name.replace("plugin-", "")
                status = self.get_plugin_status(plugin_id)
                if status:
                    plugins.append(status)
        except Exception as e:
            logger.error(f"Failed to list plugins: {e}")
        return plugins
    
    def get_container_logs(self, plugin_id: str, tail: int = 100) -> str:
        """Get container logs"""
        try:
            container_name = f"plugin-{plugin_id}"
            container = self.client.containers.get(container_name)
            return container.logs(tail=tail).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to get logs for plugin {plugin_id}: {e}")
            return ""
    
    async def cleanup(self):
        """Cleanup Docker resources"""
        # Cleanup is handled by Docker's restart policies
        logger.info("Docker manager cleanup completed")

