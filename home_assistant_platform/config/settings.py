"""Configuration management for the platform"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Platform settings loaded from environment variables"""
    
    # Platform Configuration
    platform_name: str = Field(default="Home Assistant Platform", env="PLATFORM_NAME")
    platform_version: str = Field(default="1.0.0", env="PLATFORM_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    web_ui_port: int = Field(default=5000, env="WEB_UI_PORT")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./platform/data/platform.db", env="DATABASE_URL")
    marketplace_db_host: str = Field(default="marketplace-db", env="MARKETPLACE_DB_HOST")
    marketplace_db_port: int = Field(default=5432, env="MARKETPLACE_DB_PORT")
    marketplace_db_name: str = Field(default="marketplace", env="MARKETPLACE_DB_NAME")
    marketplace_db_user: str = Field(default="marketplace_user", env="MARKETPLACE_DB_USER")
    marketplace_db_password: str = Field(default="changeme", env="MARKETPLACE_DB_PASSWORD")
    
    # Licensing
    license_server_url: str = Field(default="https://license.example.com", env="LICENSE_SERVER_URL")
    license_offline_mode: bool = Field(default=True, env="LICENSE_OFFLINE_MODE")
    
    # Voice Processing
    voice_enabled: bool = Field(default=True, env="VOICE_ENABLED")
    wake_word: str = Field(default="hey_assistant", env="WAKE_WORD")
    stt_engine: str = Field(default="vosk", env="STT_ENGINE")
    tts_engine: str = Field(default="pyttsx3", env="TTS_ENGINE")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_enabled: bool = Field(default=False, env="OPENAI_ENABLED")
    openai_tts_voice: str = Field(default="nova", env="OPENAI_TTS_VOICE")  # Options: alloy, echo, fable, onyx, nova, shimmer
    conversation_mode: bool = Field(default=False, env="CONVERSATION_MODE")  # Enable fluid conversation mode
    
    # Plugin System
    plugins_dir: str = Field(default="/app/plugins", env="PLUGINS_DIR")
    plugin_max_cpu: float = Field(default=0.5, env="PLUGIN_MAX_CPU")
    plugin_max_memory: str = Field(default="512m", env="PLUGIN_MAX_MEMORY")
    plugin_network: str = Field(default="platform-network", env="PLUGIN_NETWORK")
    
    # Marketplace
    marketplace_url: str = Field(default="https://marketplace.example.com", env="MARKETPLACE_URL")
    marketplace_api_key: Optional[str] = Field(default=None, env="MARKETPLACE_API_KEY")
    revenue_share_percentage: int = Field(default=30, env="REVENUE_SHARE_PERCENTAGE")
    
    # Security
    secret_key: str = Field(default="changeme-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret_key: str = Field(default="changeme-jwt-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # MQTT
    mqtt_broker_host: str = Field(default="localhost", env="MQTT_BROKER_HOST")
    mqtt_broker_port: int = Field(default=1883, env="MQTT_BROKER_PORT")
    mqtt_username: Optional[str] = Field(default=None, env="MQTT_USERNAME")
    mqtt_password: Optional[str] = Field(default=None, env="MQTT_PASSWORD")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        """Get data directory path"""
        return self.base_dir / "data"
    
    @property
    def plugins_dir_path(self) -> Path:
        """Get plugins directory path"""
        if self.plugins_dir.startswith("/"):
            return Path(self.plugins_dir)
        return self.base_dir / self.plugins_dir
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure data directory exists
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.plugins_dir_path.mkdir(parents=True, exist_ok=True)

