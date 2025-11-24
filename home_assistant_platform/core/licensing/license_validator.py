"""License validation system"""

import logging
import requests
from typing import Optional, Dict, List
from pathlib import Path
from home_assistant_platform.config.settings import settings
from home_assistant_platform.core.licensing.hardware_id import get_or_create_hardware_id

logger = logging.getLogger(__name__)


class LicenseValidator:
    """Validates platform licenses"""
    
    def __init__(self):
        self.hardware_id = get_or_create_hardware_id()
        self.license_file = settings.data_dir / "license.key"
        self.license_data: Optional[Dict] = None
        self._load_license()
    
    def _load_license(self):
        """Load license from file"""
        if self.license_file.exists():
            try:
                with open(self.license_file, 'r') as f:
                    license_key = f.read().strip()
                    self.license_data = self._parse_license(license_key)
            except Exception as e:
                logger.error(f"Failed to load license: {e}")
    
    def _parse_license(self, license_key: str) -> Optional[Dict]:
        """Parse license key (simplified - implement proper validation)"""
        # In production, this would decrypt and validate the license
        # For now, basic structure
        try:
            parts = license_key.split('-')
            if len(parts) >= 3:
                return {
                    "key": license_key,
                    "tier": parts[0] if len(parts) > 0 else "basic",
                    "hardware_id": parts[1] if len(parts) > 1 else None,
                    "signature": parts[2] if len(parts) > 2 else None
                }
        except Exception as e:
            logger.error(f"Failed to parse license: {e}")
        return None
    
    def validate_license(self, license_key: Optional[str] = None) -> bool:
        """Validate license key"""
        if license_key:
            self.license_data = self._parse_license(license_key)
            if self.license_data:
                try:
                    with open(self.license_file, 'w') as f:
                        f.write(license_key)
                except Exception as e:
                    logger.error(f"Failed to save license: {e}")
        
        if not self.license_data:
            logger.warning("No license found - using trial mode")
            return False
        
        # Validate hardware ID matches
        if self.license_data.get("hardware_id") != self.hardware_id:
            logger.warning("License hardware ID mismatch")
            return False
        
        # Online validation (if enabled)
        if not settings.license_offline_mode:
            return self._validate_online()
        
        # Offline validation (basic check)
        return True
    
    def _validate_online(self) -> bool:
        """Validate license with license server"""
        try:
            response = requests.post(
                f"{settings.license_server_url}/validate",
                json={
                    "hardware_id": self.hardware_id,
                    "license_key": self.license_data.get("key")
                },
                timeout=5
            )
            return response.status_code == 200 and response.json().get("valid", False)
        except Exception as e:
            logger.error(f"Online license validation failed: {e}")
            return False
    
    def has_feature(self, feature: str) -> bool:
        """Check if license includes a specific feature"""
        if not self.license_data:
            return False
        
        tier = self.license_data.get("tier", "basic")
        
        # Feature gating based on tier
        features = {
            "basic": ["voice_commands", "basic_plugins"],
            "premium": ["voice_commands", "basic_plugins", "marketplace", "unlimited_plugins"],
            "enterprise": ["voice_commands", "basic_plugins", "marketplace", "unlimited_plugins", "custom_integrations", "priority_support"]
        }
        
        return feature in features.get(tier, [])
    
    def get_license_tier(self) -> str:
        """Get current license tier"""
        if not self.license_data:
            return "trial"
        return self.license_data.get("tier", "basic")
    
    def set_license(self, license_key: str) -> bool:
        """Set and validate a new license"""
        return self.validate_license(license_key)

