"""Basic API integration tests"""

import pytest
from home_assistant_platform.tests.utils.test_client import TestClient


@pytest.fixture
def client():
    """API client"""
    return TestClient()


def test_api_status(client):
    """Test API status endpoint"""
    status = client.get('status')
    assert status['status'] == 'ok'


def test_list_devices(client):
    """Test listing devices"""
    devices = client.get('devices')
    assert isinstance(devices, list)


def test_list_scenes(client):
    """Test listing scenes"""
    scenes = client.get('scenes/scenes')
    assert isinstance(scenes, list)


def test_list_automations(client):
    """Test listing automations"""
    automations = client.get('automation/automations')
    assert isinstance(automations, list)

