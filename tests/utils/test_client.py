"""Test client for API testing"""

import requests
from typing import Optional, Dict, Any


class TestClient:
    """Test client for API testing"""
    
    def __init__(self, api_url: str = 'http://localhost:8000/api/v1'):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url, timeout=10)
        response.raise_for_status()
        if response.content:
            return response.json()
        return {}


class MockDevice:
    """Mock device for testing"""
    
    def __init__(self, device_id: str, name: str = None, device_type: str = "light"):
        self.id = device_id
        self.name = name or device_id
        self.device_type = device_type
        self.state = "off"
        self.brightness = 0
    
    def turn_on(self, brightness: int = None):
        """Turn on device"""
        self.state = "on"
        if brightness is not None:
            self.brightness = brightness
    
    def turn_off(self):
        """Turn off device"""
        self.state = "off"
        self.brightness = 0
    
    def set_brightness(self, brightness: int):
        """Set brightness"""
        self.brightness = brightness
        if brightness > 0:
            self.state = "on"
    
    @property
    def is_on(self) -> bool:
        """Check if device is on"""
        return self.state == "on"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "device_type": self.device_type,
            "state": self.state,
            "brightness": self.brightness
        }

