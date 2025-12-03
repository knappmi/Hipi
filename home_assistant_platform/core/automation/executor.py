"""Automation execution engine"""

import logging
import asyncio
from datetime import datetime, time
from typing import List, Dict, Optional, Any, Callable
from home_assistant_platform.core.automation.models import (
    Automation, AutomationExecution, AutomationSuggestion, get_automation_db
)

logger = logging.getLogger(__name__)


class AutomationExecutor:
    """Executes automation rules"""
    
    def __init__(self, device_manager: Optional[Any] = None):
        self.db = get_automation_db()
        self.device_manager = device_manager
        self.running_automations: Dict[int, asyncio.Task] = {}
    
    async def execute_automation(
        self,
        automation_id: int,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute an automation"""
        try:
            automation = self.db.query(Automation).filter(
                Automation.id == automation_id,
                Automation.is_enabled == True,
                Automation.is_active == True
            ).first()
            
            if not automation:
                logger.warning(f"Automation {automation_id} not found or disabled")
                return False
            
            # Check conditions if any
            if automation.conditions:
                if not self._check_conditions(automation.conditions, trigger_data):
                    logger.debug(f"Automation {automation_id} conditions not met")
                    return False
            
            # Execute actions
            success = True
            executed_actions = []
            
            for action in automation.actions:
                try:
                    action_result = await self._execute_action(action, trigger_data)
                    executed_actions.append({
                        "action": action,
                        "success": action_result
                    })
                    if not action_result:
                        success = False
                except Exception as e:
                    logger.error(f"Error executing action {action}: {e}", exc_info=True)
                    executed_actions.append({
                        "action": action,
                        "success": False,
                        "error": str(e)
                    })
                    success = False
            
            # Log execution
            execution_log = AutomationExecution(
                automation_id=automation_id,
                trigger_type=automation.trigger_type,
                trigger_data=trigger_data or {},
                actions_executed=executed_actions,
                success=success
            )
            self.db.add(execution_log)
            self.db.commit()
            
            logger.info(f"Executed automation {automation_id}: {automation.name} (success: {success})")
            return success
            
        except Exception as e:
            logger.error(f"Error executing automation {automation_id}: {e}", exc_info=True)
            self.db.rollback()
            return False
    
    async def _execute_action(
        self,
        action: Dict[str, Any],
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute a single action"""
        device_id = action.get("device_id")
        device_type = action.get("device_type")
        action_type = action.get("action")
        value = action.get("value")
        
        if not device_id or not action_type:
            logger.error(f"Invalid action: missing device_id or action")
            return False
        
        # Use device manager if available
        if self.device_manager:
            try:
                if action_type == "turn_on":
                    return await self.device_manager.turn_on_device(device_id)
                elif action_type == "turn_off":
                    return await self.device_manager.turn_off_device(device_id)
                elif action_type == "set_temperature":
                    return await self.device_manager.set_temperature(device_id, float(value))
                elif action_type == "set_brightness":
                    return await self.device_manager.set_brightness(device_id, int(value))
                elif action_type == "set_color":
                    return await self.device_manager.set_color(device_id, value)
                else:
                    logger.warning(f"Unknown action type: {action_type}")
                    return False
            except Exception as e:
                logger.error(f"Error executing device action: {e}", exc_info=True)
                return False
        else:
            # Fallback: just log the action
            logger.info(f"Would execute: {device_id} -> {action_type} ({value})")
            return True
    
    def _check_conditions(
        self,
        conditions: Dict[str, Any],
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if conditions are met"""
        # Simple condition checking
        # Can be extended for more complex logic
        
        # Time conditions
        if "time" in conditions:
            current_time = datetime.now().time()
            condition_time = time.fromisoformat(conditions["time"])
            if current_time < condition_time:
                return False
        
        # Day of week conditions
        if "days_of_week" in conditions:
            current_day = datetime.now().weekday()
            if current_day not in conditions["days_of_week"]:
                return False
        
        # Device state conditions
        if "device_states" in conditions:
            # Would need device manager to check states
            pass
        
        return True
    
    def create_automation_from_suggestion(
        self,
        suggestion_id: int,
        user_id: str = "default"
    ) -> Optional[Automation]:
        """Create automation from accepted suggestion"""
        try:
            from home_assistant_platform.core.automation.suggestion_engine import SuggestionEngine
            suggestion_engine = SuggestionEngine()
            
            suggestion = self.db.query(AutomationSuggestion).filter(
                AutomationSuggestion.id == suggestion_id,
                AutomationSuggestion.user_id == user_id,
                AutomationSuggestion.status == "accepted"
            ).first()
            
            if not suggestion:
                logger.error(f"Suggestion {suggestion_id} not found or not accepted")
                return None
            
            config = suggestion.automation_config
            
            automation = Automation(
                name=suggestion.automation_name,
                description=suggestion.suggestion_text,
                trigger_type=config["trigger_type"],
                trigger_config=config["trigger_config"],
                actions=config["actions"],
                conditions=config.get("conditions"),
                created_from_pattern=suggestion.pattern_id,
                user_id=user_id,
                is_enabled=True,
                is_active=True
            )
            
            self.db.add(automation)
            self.db.commit()
            
            logger.info(f"Created automation from suggestion {suggestion_id}: {automation.name}")
            return automation
            
        except Exception as e:
            logger.error(f"Error creating automation from suggestion: {e}", exc_info=True)
            self.db.rollback()
            return None

