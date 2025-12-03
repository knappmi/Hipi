"""Enhanced automation system with scenes and advanced triggers"""

import logging
from datetime import datetime, time
from typing import List, Dict, Optional, Any
from home_assistant_platform.core.automation.models import Automation, get_automation_db
from home_assistant_platform.core.automation.executor import AutomationExecutor

logger = logging.getLogger(__name__)


class EnhancedAutomationManager:
    """Enhanced automation manager with scene support"""
    
    def __init__(self, automation_executor: AutomationExecutor, scene_manager=None):
        self.executor = automation_executor
        self.scene_manager = scene_manager
        self.db = get_automation_db()
    
    def create_scene_automation(
        self,
        name: str,
        scene_name: str,
        trigger_type: str = "time",
        trigger_config: Optional[Dict[str, Any]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> Optional[Automation]:
        """Create automation that activates a scene"""
        if not self.scene_manager:
            logger.error("Scene manager not available")
            return None
        
        scene = self.scene_manager.get_scene_by_name(scene_name, user_id)
        if not scene:
            logger.error(f"Scene '{scene_name}' not found")
            return None
        
        # Convert scene device states to automation actions
        actions = []
        for device_state in scene.device_states:
            action = {
                "device_id": device_state.get("device_id"),
                "device_type": device_state.get("device_type", "unknown"),
                "action": "turn_on" if device_state.get("state") == "on" else "turn_off"
            }
            
            if device_state.get("brightness"):
                actions.append({
                    "device_id": device_state.get("device_id"),
                    "device_type": device_state.get("device_type", "unknown"),
                    "action": "set_brightness",
                    "value": str(device_state.get("brightness"))
                })
            
            if device_state.get("color"):
                actions.append({
                    "device_id": device_state.get("device_id"),
                    "device_type": device_state.get("device_type", "unknown"),
                    "action": "set_color",
                    "value": device_state.get("color")
                })
            
            if device_state.get("temperature"):
                actions.append({
                    "device_id": device_state.get("device_id"),
                    "device_type": device_state.get("device_type", "unknown"),
                    "action": "set_temperature",
                    "value": str(device_state.get("temperature"))
                })
            
            actions.append(action)
        
        automation = Automation(
            name=name,
            description=f"Activate scene: {scene_name}",
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
            actions=actions,
            conditions=conditions,
            user_id=user_id,
            is_enabled=True,
            is_active=True
        )
        
        self.db.add(automation)
        self.db.commit()
        
        logger.info(f"Created scene automation: {name}")
        return automation
    
    def create_event_based_automation(
        self,
        name: str,
        event_type: str,  # device_state_change, calendar_event, etc.
        event_config: Dict[str, Any],
        actions: List[Dict[str, Any]],
        conditions: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> Automation:
        """Create event-based automation"""
        automation = Automation(
            name=name,
            description=f"Event-based: {event_type}",
            trigger_type="event",
            trigger_config={
                "event_type": event_type,
                **event_config
            },
            actions=actions,
            conditions=conditions,
            user_id=user_id,
            is_enabled=True,
            is_active=True
        )
        
        self.db.add(automation)
        self.db.commit()
        
        logger.info(f"Created event-based automation: {name}")
        return automation
    
    def create_conditional_automation(
        self,
        name: str,
        trigger_type: str,
        trigger_config: Dict[str, Any],
        conditions: Dict[str, Any],  # Complex conditions
        actions: List[Dict[str, Any]],
        user_id: str = "default"
    ) -> Automation:
        """Create automation with complex conditions"""
        automation = Automation(
            name=name,
            description=f"Conditional automation: {name}",
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            actions=actions,
            conditions=conditions,
            user_id=user_id,
            is_enabled=True,
            is_active=True
        )
        
        self.db.add(automation)
        self.db.commit()
        
        logger.info(f"Created conditional automation: {name}")
        return automation
    
    def get_automations_by_trigger(self, trigger_type: str, user_id: str = "default") -> List[Automation]:
        """Get automations by trigger type"""
        return self.db.query(Automation).filter(
            Automation.trigger_type == trigger_type,
            Automation.user_id == user_id,
            Automation.is_enabled == True,
            Automation.is_active == True
        ).all()
    
    def enable_automation(self, automation_id: int, user_id: str = "default") -> bool:
        """Enable an automation"""
        automation = self.db.query(Automation).filter(
            Automation.id == automation_id,
            Automation.user_id == user_id
        ).first()
        
        if automation:
            automation.is_enabled = True
            self.db.commit()
            return True
        return False
    
    def disable_automation(self, automation_id: int, user_id: str = "default") -> bool:
        """Disable an automation"""
        automation = self.db.query(Automation).filter(
            Automation.id == automation_id,
            Automation.user_id == user_id
        ).first()
        
        if automation:
            automation.is_enabled = False
            self.db.commit()
            return True
        return False

