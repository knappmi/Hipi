"""Scene manager - manages predefined device scenes"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from home_assistant_platform.core.automation.models import get_automation_db, Base

logger = logging.getLogger(__name__)


class Scene(Base):
    """Scene - predefined device states"""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    icon = Column(String)  # Icon name for UI
    
    # Scene actions - list of device states
    device_states = Column(JSON, nullable=False)  # [{"device_id": "...", "state": "on", "brightness": 50}, ...]
    
    # Metadata
    is_active = Column(Boolean, default=True)
    user_id = Column(String, default="default")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SceneManager:
    """Manages scenes"""
    
    def __init__(self, device_manager=None):
        self.device_manager = device_manager
        self.db = get_automation_db()
        # Initialize scenes table
        try:
            Base.metadata.create_all(self.db.bind)
        except Exception as e:
            logger.warning(f"Could not create scenes table: {e}")
    
    def create_scene(
        self,
        name: str,
        device_states: List[Dict[str, Any]],
        description: Optional[str] = None,
        icon: Optional[str] = None,
        user_id: str = "default"
    ) -> Scene:
        """Create a new scene"""
        # Check if scene already exists
        existing = self.get_scene_by_name(name, user_id)
        if existing:
            logger.warning(f"Scene '{name}' already exists, updating instead")
            self.update_scene(existing.id, name=name, device_states=device_states, description=description, user_id=user_id)
            return existing
        
        scene = Scene(
            name=name,
            description=description,
            icon=icon,
            device_states=device_states,
            user_id=user_id
        )
        
        try:
            self.db.add(scene)
            self.db.commit()
            logger.info(f"Created scene: {name} with {len(device_states)} device states")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scene: {e}")
            raise
        
        return scene
    
    def get_scene(self, scene_id: int, user_id: str = "default") -> Optional[Scene]:
        """Get a scene by ID"""
        return self.db.query(Scene).filter(
            Scene.id == scene_id,
            Scene.user_id == user_id
        ).first()
    
    def get_scene_by_name(self, name: str, user_id: str = "default") -> Optional[Scene]:
        """Get a scene by name"""
        return self.db.query(Scene).filter(
            Scene.name == name,
            Scene.user_id == user_id,
            Scene.is_active == True
        ).first()
    
    def list_scenes(self, user_id: str = "default") -> List[Scene]:
        """List all scenes"""
        return self.db.query(Scene).filter(
            Scene.user_id == user_id,
            Scene.is_active == True
        ).order_by(Scene.name).all()
    
    async def activate_scene(self, scene_id: int, user_id: str = "default") -> bool:
        """Activate a scene"""
        scene = self.get_scene(scene_id, user_id)
        if not scene:
            logger.warning(f"Scene {scene_id} not found")
            return False
        
        if not self.device_manager:
            logger.error("Device manager not available")
            return False
        
        success = True
        for device_state in scene.device_states:
            device_id = device_state.get("device_id")
            state = device_state.get("state")
            brightness = device_state.get("brightness")
            color = device_state.get("color")
            temperature = device_state.get("temperature")
            
            try:
                if state == "on":
                    result = await self.device_manager.turn_on_device(device_id)
                    if not result:
                        success = False
                elif state == "off":
                    result = await self.device_manager.turn_off_device(device_id)
                    if not result:
                        success = False
                
                if brightness is not None:
                    await self.device_manager.set_brightness(device_id, brightness)
                
                if color:
                    await self.device_manager.set_color(device_id, color)
                
                if temperature is not None:
                    await self.device_manager.set_temperature(device_id, temperature)
                
            except Exception as e:
                logger.error(f"Error setting device {device_id} state: {e}")
                success = False
        
        logger.info(f"Activated scene: {scene.name} (success: {success})")
        return success
    
    async def activate_scene_by_name(self, scene_name: str, user_id: str = "default") -> bool:
        """Activate a scene by name"""
        scene = self.get_scene_by_name(scene_name, user_id)
        if not scene:
            logger.warning(f"Scene '{scene_name}' not found")
            return False
        
        return await self.activate_scene(scene.id, user_id)
    
    def delete_scene(self, scene_id: int, user_id: str = "default") -> bool:
        """Delete a scene"""
        scene = self.get_scene(scene_id, user_id)
        if scene:
            self.db.delete(scene)
            self.db.commit()
            logger.info(f"Deleted scene: {scene_id}")
            return True
        return False
    
    def update_scene(
        self,
        scene_id: int,
        name: Optional[str] = None,
        device_states: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        user_id: str = "default"
    ) -> bool:
        """Update a scene"""
        scene = self.get_scene(scene_id, user_id)
        if not scene:
            return False
        
        if name:
            scene.name = name
        if device_states:
            scene.device_states = device_states
        if description:
            scene.description = description
        
        scene.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Updated scene: {scene_id}")
        return True

