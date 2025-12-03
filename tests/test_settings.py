"""Tests for settings configuration"""

import pytest
from home_assistant_platform.config.settings import settings


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings.platform_name == "Home Assistant Platform"
    assert settings.platform_version == "1.0.0"
    assert isinstance(settings.api_port, int)
    assert settings.api_port == 8000


def test_settings_paths():
    """Test that paths are configured correctly"""
    assert settings.base_dir.exists()
    assert settings.data_dir.exists()
    assert settings.plugins_dir_path.exists()

