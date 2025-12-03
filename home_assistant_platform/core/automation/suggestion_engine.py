"""Automation suggestion engine - generates suggestions from patterns"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from home_assistant_platform.core.automation.models import (
    Pattern, AutomationSuggestion, get_automation_db
)

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """Generates automation suggestions from detected patterns"""
    
    def __init__(self):
        self.db = get_automation_db()
    
    def generate_suggestions(
        self,
        pattern: Pattern,
        user_id: str = "default"
    ) -> Optional[AutomationSuggestion]:
        """Generate an automation suggestion from a pattern"""
        try:
            # Check if suggestion already exists for this pattern
            existing = self.db.query(AutomationSuggestion).filter(
                AutomationSuggestion.pattern_id == pattern.id,
                AutomationSuggestion.user_id == user_id,
                AutomationSuggestion.status == "pending"
            ).first()
            
            if existing:
                return existing
            
            # Generate suggestion based on pattern type
            if pattern.pattern_type == "time_based":
                suggestion = self._generate_time_based_suggestion(pattern)
            else:
                return None
            
            if suggestion:
                suggestion_obj = AutomationSuggestion(
                    pattern_id=pattern.id,
                    suggestion_text=suggestion["text"],
                    automation_name=suggestion["name"],
                    automation_config=suggestion["config"],
                    user_id=user_id,
                    status="pending"
                )
                
                self.db.add(suggestion_obj)
                self.db.commit()
                
                logger.info(f"Generated suggestion for pattern {pattern.id}: {suggestion['name']}")
                return suggestion_obj
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}", exc_info=True)
            self.db.rollback()
            return None
    
    def _generate_time_based_suggestion(self, pattern: Pattern) -> Optional[Dict[str, Any]]:
        """Generate suggestion for time-based pattern"""
        conditions = pattern.conditions or {}
        hour = conditions.get("hour", 0)
        minute = conditions.get("minute", 0)
        days = conditions.get("days_of_week", [])
        
        # Format time
        time_str = f"{hour:02d}:{minute:02d}"
        
        # Format days
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if days == list(range(5)):
            day_str = "weekdays"
        elif days == [5, 6]:
            day_str = "weekends"
        elif len(days) == 7:
            day_str = "every day"
        else:
            day_str = ", ".join([day_names[d] for d in sorted(days)])
        
        # Generate action description
        action_desc = f"{pattern.action.replace('_', ' ')}"
        if pattern.value:
            action_desc += f" to {pattern.value}"
        
        # Create suggestion text
        suggestion_text = (
            f"I notice you {action_desc} the {pattern.device_id} at {time_str} on {day_str}. "
            f"Would you like me to automate this?"
        )
        
        # Create automation name
        automation_name = f"Auto {action_desc.title()} {pattern.device_id} at {time_str}"
        
        # Create automation config
        automation_config = {
            "trigger_type": "time",
            "trigger_config": {
                "time": time_str,
                "days_of_week": days
            },
            "actions": [{
                "device_id": pattern.device_id,
                "device_type": pattern.device_type,
                "action": pattern.action,
                "value": pattern.value
            }]
        }
        
        return {
            "text": suggestion_text,
            "name": automation_name,
            "config": automation_config
        }
    
    def get_pending_suggestions(self, user_id: str = "default") -> List[AutomationSuggestion]:
        """Get all pending suggestions"""
        try:
            return self.db.query(AutomationSuggestion).filter(
                AutomationSuggestion.user_id == user_id,
                AutomationSuggestion.status == "pending"
            ).order_by(AutomationSuggestion.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}", exc_info=True)
            return []
    
    def accept_suggestion(self, suggestion_id: int, user_id: str = "default") -> bool:
        """Accept an automation suggestion"""
        try:
            suggestion = self.db.query(AutomationSuggestion).filter(
                AutomationSuggestion.id == suggestion_id,
                AutomationSuggestion.user_id == user_id
            ).first()
            
            if not suggestion:
                return False
            
            suggestion.status = "accepted"
            suggestion.responded_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Suggestion {suggestion_id} accepted")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting suggestion: {e}", exc_info=True)
            self.db.rollback()
            return False
    
    def reject_suggestion(self, suggestion_id: int, user_id: str = "default") -> bool:
        """Reject an automation suggestion"""
        try:
            suggestion = self.db.query(AutomationSuggestion).filter(
                AutomationSuggestion.id == suggestion_id,
                AutomationSuggestion.user_id == user_id
            ).first()
            
            if not suggestion:
                return False
            
            suggestion.status = "rejected"
            suggestion.responded_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Suggestion {suggestion_id} rejected")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting suggestion: {e}", exc_info=True)
            self.db.rollback()
            return False

