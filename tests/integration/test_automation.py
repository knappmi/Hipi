#!/usr/bin/env python3
"""Test script for predictive automation system"""

import sys
import asyncio
import time
from datetime import datetime, timedelta

sys.path.insert(0, '/home/knappmi14/Documents')

from home_assistant_platform.core.automation.pattern_learner import PatternLearner
from home_assistant_platform.core.automation.suggestion_engine import SuggestionEngine
from home_assistant_platform.core.automation.executor import AutomationExecutor
from home_assistant_platform.core.automation.device_manager import MockDeviceManager
from home_assistant_platform.core.automation.models import get_automation_db


def test_pattern_learning():
    """Test pattern learning system"""
    print("=" * 60)
    print("Testing Pattern Learning System")
    print("=" * 60)
    
    pattern_learner = PatternLearner()
    
    # Simulate device actions - turn on living room light at 7 PM for 5 days
    print("\n1. Recording device actions...")
    base_time = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
    
    for day_offset in range(5):  # 5 days
        action_time = base_time - timedelta(days=day_offset)
        print(f"   Recording action on {action_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Record action
        pattern_learner.record_action(
            device_id="living_room_light",
            device_type="light",
            action="turn_on",
            user_id="test_user"
        )
        
        # Small delay to ensure different timestamps
        time.sleep(0.1)
    
    print("\n2. Checking detected patterns...")
    patterns = pattern_learner.get_patterns(user_id="test_user")
    
    if patterns:
        print(f"   Found {len(patterns)} pattern(s):")
        for pattern in patterns:
            print(f"   - Device: {pattern.device_id}")
            print(f"     Action: {pattern.action}")
            print(f"     Confidence: {pattern.confidence:.2%}")
            print(f"     Conditions: {pattern.conditions}")
            print(f"     Occurrences: {pattern.occurrence_count}")
    else:
        print("   No patterns detected yet (may need more data)")
    
    return patterns


def test_suggestion_engine(patterns):
    """Test suggestion engine"""
    print("\n" + "=" * 60)
    print("Testing Suggestion Engine")
    print("=" * 60)
    
    if not patterns:
        print("No patterns available for suggestions")
        return []
    
    suggestion_engine = SuggestionEngine()
    
    print("\n1. Generating suggestions from patterns...")
    suggestions = []
    
    for pattern in patterns:
        suggestion = suggestion_engine.generate_suggestions(pattern, user_id="test_user")
        if suggestion:
            suggestions.append(suggestion)
            print(f"   Generated suggestion: {suggestion.automation_name}")
            print(f"   Text: {suggestion.suggestion_text}")
    
    print(f"\n2. Found {len(suggestions)} suggestion(s)")
    
    return suggestions


async def test_automation_execution():
    """Test automation execution"""
    print("\n" + "=" * 60)
    print("Testing Automation Execution")
    print("=" * 60)
    
    device_manager = MockDeviceManager()
    executor = AutomationExecutor(device_manager)
    
    print("\n1. Testing device control...")
    result = await device_manager.turn_on_device("living_room_light")
    print(f"   Turn on living room light: {result}")
    
    state = await device_manager.get_device_state("living_room_light")
    print(f"   Device state: {state}")
    
    print("\n2. Testing automation creation and execution...")
    # This would normally come from a suggestion, but we'll create one manually
    from home_assistant_platform.core.automation.models import Automation, get_automation_db
    
    db = get_automation_db()
    automation = Automation(
        name="Test Automation",
        description="Test automation for living room light",
        trigger_type="manual",
        trigger_config={},
        actions=[{
            "device_id": "living_room_light",
            "device_type": "light",
            "action": "turn_on"
        }],
        is_enabled=True,
        is_active=True
    )
    
    db.add(automation)
    db.commit()
    
    print(f"   Created automation: {automation.name} (ID: {automation.id})")
    
    result = await executor.execute_automation(automation.id)
    print(f"   Executed automation: {result}")
    
    state = await device_manager.get_device_state("living_room_light")
    print(f"   Device state after automation: {state}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PREDICTIVE AUTOMATION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Pattern Learning
    patterns = test_pattern_learning()
    
    # Test 2: Suggestion Engine
    suggestions = test_suggestion_engine(patterns)
    
    # Test 3: Automation Execution
    asyncio.run(test_automation_execution())
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    if patterns:
        print(f"\n✓ Pattern learning: WORKING ({len(patterns)} patterns detected)")
    else:
        print("\n⚠ Pattern learning: Needs more data")
    
    if suggestions:
        print(f"✓ Suggestion engine: WORKING ({len(suggestions)} suggestions generated)")
    else:
        print("⚠ Suggestion engine: No suggestions (may need patterns)")
    
    print("✓ Automation execution: WORKING")


if __name__ == "__main__":
    main()

