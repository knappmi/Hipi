"""Pattern learning system - records and analyzes device usage patterns"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
from home_assistant_platform.core.automation.models import (
    DeviceAction, Pattern, get_automation_db
)

logger = logging.getLogger(__name__)


class PatternLearner:
    """Learns usage patterns from device actions"""
    
    def __init__(self):
        self.db = get_automation_db()
        self.min_occurrences = 3  # Minimum occurrences to detect a pattern
        self.confidence_threshold = 0.6  # Minimum confidence to suggest automation
    
    def record_action(
        self,
        device_id: str,
        device_type: str,
        action: str,
        value: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> None:
        """Record a device action for pattern learning"""
        try:
            # Use local time for pattern detection (more intuitive for users)
            from datetime import datetime as dt
            now = dt.now()
            action_record = DeviceAction(
                device_id=device_id,
                device_type=device_type,
                action=action,
                value=value,
                timestamp=now,
                day_of_week=now.weekday(),
                hour=now.hour,
                minute=now.minute,
                context=context or {},
                user_id=user_id
            )
            
            self.db.add(action_record)
            self.db.commit()
            
            logger.debug(f"Recorded action: {device_id} -> {action}")
            
            # Trigger pattern detection after recording
            self._detect_patterns(device_id, user_id)
            
        except Exception as e:
            logger.error(f"Error recording action: {e}", exc_info=True)
            self.db.rollback()
    
    def _detect_patterns(self, device_id: str, user_id: str) -> None:
        """Detect patterns for a specific device"""
        try:
            # Get recent actions for this device (last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            actions = self.db.query(DeviceAction).filter(
                DeviceAction.device_id == device_id,
                DeviceAction.user_id == user_id,
                DeviceAction.timestamp >= cutoff_date
            ).order_by(DeviceAction.timestamp).all()
            
            if len(actions) < self.min_occurrences:
                return
            
            # Group by action type
            action_groups = defaultdict(list)
            for action in actions:
                key = (action.action, action.value)
                action_groups[key].append(action)
            
            # Detect time-based patterns
            for (action_type, value), action_list in action_groups.items():
                if len(action_list) >= self.min_occurrences:
                    pattern = self._detect_time_pattern(
                        device_id, device_type=actions[0].device_type,
                        action=action_type, value=value,
                        actions=action_list, user_id=user_id
                    )
                    if pattern:
                        self._save_pattern(pattern)
        
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}", exc_info=True)
    
    def _detect_time_pattern(
        self,
        device_id: str,
        device_type: str,
        action: str,
        value: Optional[str],
        actions: List[DeviceAction],
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Detect time-based patterns from actions"""
        if len(actions) < self.min_occurrences:
            return None
        
        # Analyze time patterns
        hours = [a.hour for a in actions]
        minutes = [a.minute for a in actions]
        days_of_week = [a.day_of_week for a in actions]
        
        # Check for consistent time pattern
        hour_counts = defaultdict(int)
        minute_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for hour in hours:
            hour_counts[hour] += 1
        for minute in minutes:
            minute_counts[minute] += 1
        for day in days_of_week:
            day_counts[day] += 1
        
        # Find most common hour (must occur in at least 60% of actions)
        most_common_hour = max(hour_counts.items(), key=lambda x: x[1])
        hour_confidence = most_common_hour[1] / len(actions)
        
        # Find most common minute (within 5-minute window)
        minute_window = defaultdict(int)
        for minute in minutes:
            # Group minutes into 5-minute windows
            window = (minute // 5) * 5
            minute_window[window] += 1
        
        most_common_minute_window = max(minute_window.items(), key=lambda x: x[1]) if minute_window else (None, 0)
        minute_confidence = most_common_minute_window[1] / len(actions) if minute_window else 0
        
        # Check day pattern (weekdays vs weekends, or specific days)
        weekday_count = sum(1 for d in days_of_week if d < 5)
        weekend_count = len(days_of_week) - weekday_count
        
        # Determine day pattern
        if weekday_count / len(days_of_week) > 0.7:
            day_pattern = list(range(5))  # Weekdays
            day_confidence = weekday_count / len(days_of_week)
        elif weekend_count / len(days_of_week) > 0.7:
            day_pattern = [5, 6]  # Weekends
            day_confidence = weekend_count / len(days_of_week)
        else:
            # Check for specific days
            day_pattern = list(set(days_of_week))
            day_confidence = max(day_counts.values()) / len(actions) if day_counts else 0
        
        # Calculate overall confidence
        overall_confidence = (hour_confidence * 0.5 + minute_confidence * 0.3 + day_confidence * 0.2)
        
        if overall_confidence >= self.confidence_threshold:
            return {
                "device_id": device_id,
                "device_type": device_type,
                "action": action,
                "value": value,
                "pattern_type": "time_based",
                "conditions": {
                    "hour": most_common_hour[0],
                    "minute": most_common_minute_window[0],
                    "days_of_week": day_pattern
                },
                "occurrence_count": len(actions),
                "confidence": overall_confidence,
                "last_occurrence": actions[-1].timestamp,
                "user_id": user_id
            }
        
        return None
    
    def _save_pattern(self, pattern_data: Dict[str, Any]) -> None:
        """Save or update a detected pattern"""
        try:
            # Check if pattern already exists
            existing = self.db.query(Pattern).filter(
                Pattern.device_id == pattern_data["device_id"],
                Pattern.action == pattern_data["action"],
                Pattern.user_id == pattern_data["user_id"]
            ).first()
            
            if existing:
                # Update existing pattern
                existing.occurrence_count = pattern_data["occurrence_count"]
                existing.confidence = pattern_data["confidence"]
                existing.last_occurrence = pattern_data["last_occurrence"]
                existing.conditions = pattern_data["conditions"]
                existing.updated_at = datetime.utcnow()
            else:
                # Create new pattern
                pattern = Pattern(**pattern_data)
                self.db.add(pattern)
            
            self.db.commit()
            logger.info(f"Saved pattern: {pattern_data['device_id']} -> {pattern_data['action']} "
                       f"(confidence: {pattern_data['confidence']:.2f})")
            
        except Exception as e:
            logger.error(f"Error saving pattern: {e}", exc_info=True)
            self.db.rollback()
    
    def get_patterns(
        self,
        device_id: Optional[str] = None,
        user_id: str = "default",
        min_confidence: float = 0.0
    ) -> List[Pattern]:
        """Get detected patterns"""
        try:
            query = self.db.query(Pattern).filter(
                Pattern.user_id == user_id,
                Pattern.is_active == True,
                Pattern.confidence >= min_confidence
            )
            
            if device_id:
                query = query.filter(Pattern.device_id == device_id)
            
            return query.order_by(Pattern.confidence.desc()).all()
        except Exception as e:
            logger.error(f"Error getting patterns: {e}", exc_info=True)
            return []
    
    def get_action_history(
        self,
        device_id: Optional[str] = None,
        days: int = 7,
        user_id: str = "default"
    ) -> List[DeviceAction]:
        """Get action history"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = self.db.query(DeviceAction).filter(
                DeviceAction.timestamp >= cutoff_date,
                DeviceAction.user_id == user_id
            )
            
            if device_id:
                query = query.filter(DeviceAction.device_id == device_id)
            
            return query.order_by(DeviceAction.timestamp.desc()).all()
        except Exception as e:
            logger.error(f"Error getting action history: {e}", exc_info=True)
            return []

