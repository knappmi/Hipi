"""Base CLI utilities"""

import requests
import json
import click
from typing import Optional, Dict, Any
from click import Context


class APIClient:
    """Simple API client for CLI"""
    
    def __init__(self, api_url: str = 'http://localhost:8000/api/v1'):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise click.ClickException(f"Could not connect to API at {self.api_url}. Is the platform running?")
        except requests.exceptions.HTTPError as e:
            raise click.ClickException(f"API error: {e.response.status_code} - {e.response.text}")
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, json=json_data or data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise click.ClickException(f"Could not connect to API at {self.api_url}. Is the platform running?")
        except requests.exceptions.HTTPError as e:
            raise click.ClickException(f"API error: {e.response.status_code} - {e.response.text}")
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.put(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise click.ClickException(f"Could not connect to API at {self.api_url}. Is the platform running?")
        except requests.exceptions.HTTPError as e:
            raise click.ClickException(f"API error: {e.response.status_code} - {e.response.text}")
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.ConnectionError:
            raise click.ClickException(f"Could not connect to API at {self.api_url}. Is the platform running?")
        except requests.exceptions.HTTPError as e:
            raise click.ClickException(f"API error: {e.response.status_code} - {e.response.text}")


def get_client(ctx: Context) -> APIClient:
    """Get API client from context"""
    api_url = ctx.obj.get('api_url', 'http://localhost:8000/api/v1')
    return APIClient(api_url)


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON"""
    return json.dumps(data, indent=indent, default=str)

