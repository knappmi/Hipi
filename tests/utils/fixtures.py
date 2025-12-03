"""Test fixtures and helpers"""

import pytest
from home_assistant_platform.tests.utils.test_client import TestClient, MockDevice


@pytest.fixture
def api_client():
    """API client fixture"""
    return TestClient()


@pytest.fixture
def mock_device():
    """Mock device fixture"""
    return MockDevice("test_device_001", "Test Light", "light")


@pytest.fixture
def sample_scene():
    """Sample scene data"""
    return {
        "name": "Test Scene",
        "device_states": [
            {"device_id": "light_001", "state": "on", "brightness": 50},
            {"device_id": "light_002", "state": "off"}
        ],
        "description": "Test scene for testing"
    }


@pytest.fixture
def sample_automation():
    """Sample automation data"""
    return {
        "name": "Test Automation",
        "trigger": {
            "type": "time",
            "time": "12:00"
        },
        "actions": [
            {
                "type": "scene",
                "scene_id": 1
            }
        ],
        "enabled": True
    }

