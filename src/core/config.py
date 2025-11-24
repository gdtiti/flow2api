"""Configuration management for Flow2API"""
import tomli
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Application configuration"""

    def __init__(self):
        self._config = self._load_config()
        self._admin_username: Optional[str] = None
        self._admin_password: Optional[str] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from setting.toml and environment variables"""
        # Load base configuration from TOML file
        config_path = Path(__file__).parent.parent.parent / "config" / "setting.toml"
        with open(config_path, "rb") as f:
            config = tomli.load(f)

        # Override with environment variables
        config = self._override_with_env_vars(config)

        return config

    def _override_with_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration values with environment variables"""

        # Define environment variable mappings
        # Format: ENV_VAR_NAME -> ("section", "key", type_converter)
        env_mappings = {
            # Global settings
            "FLOW2API_API_KEY": ("global", "api_key", str),
            "FLOW2API_ADMIN_USERNAME": ("global", "admin_username", str),
            "FLOW2API_ADMIN_PASSWORD": ("global", "admin_password", str),

            # Flow settings
            "FLOW2API_LABS_BASE_URL": ("flow", "labs_base_url", str),
            "FLOW2API_API_BASE_URL": ("flow", "api_base_url", str),
            "FLOW2API_TIMEOUT": ("flow", "timeout", int),
            "FLOW2API_MAX_RETRIES": ("flow", "max_retries", int),
            "FLOW2API_POLL_INTERVAL": ("flow", "poll_interval", float),
            "FLOW2API_MAX_POLL_ATTEMPTS": ("flow", "max_poll_attempts", int),

            # Server settings
            "FLOW2API_HOST": ("server", "host", str),
            "FLOW2API_PORT": ("server", "port", int),

            # Debug settings
            "FLOW2API_DEBUG_ENABLED": ("debug", "enabled", self._str_to_bool),
            "FLOW2API_DEBUG_LOG_REQUESTS": ("debug", "log_requests", self._str_to_bool),
            "FLOW2API_DEBUG_LOG_RESPONSES": ("debug", "log_responses", self._str_to_bool),
            "FLOW2API_DEBUG_MASK_TOKEN": ("debug", "mask_token", self._str_to_bool),

            # Proxy settings
            "FLOW2API_PROXY_ENABLED": ("proxy", "proxy_enabled", self._str_to_bool),
            "FLOW2API_PROXY_URL": ("proxy", "proxy_url", str),

            # Generation settings
            "FLOW2API_IMAGE_TIMEOUT": ("generation", "image_timeout", int),
            "FLOW2API_VIDEO_TIMEOUT": ("generation", "video_timeout", int),

            # Cache settings
            "FLOW2API_CACHE_ENABLED": ("cache", "enabled", self._str_to_bool),
            "FLOW2API_CACHE_TIMEOUT": ("cache", "timeout", int),
            "FLOW2API_CACHE_BASE_URL": ("cache", "base_url", str),
        }

        # Apply environment variable overrides
        for env_var, (section, key, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Ensure section exists
                if section not in config:
                    config[section] = {}

                try:
                    # Convert the value and apply it
                    converted_value = converter(env_value)
                    config[section][key] = converted_value
                except (ValueError, TypeError) as e:
                    # Log warning but continue with default value
                    print(f"Warning: Invalid value for {env_var}: {env_value}, error: {e}")

        return config

    def _str_to_bool(self, value: str) -> bool:
        """Convert string to boolean value"""
        if isinstance(value, bool):
            return value
        return value.lower() in ("true", "1", "yes", "on", "enabled")

    def reload_config(self):
        """Reload configuration from file"""
        self._config = self._load_config()

    def get_env_overrides_info(self) -> Dict[str, Any]:
        """Get information about which environment variables are set and overriding config"""
        overrides = {}

        env_mappings = {
            "FLOW2API_API_KEY": ("global", "api_key"),
            "FLOW2API_ADMIN_USERNAME": ("global", "admin_username"),
            "FLOW2API_ADMIN_PASSWORD": ("global", "admin_password"),
            "FLOW2API_LABS_BASE_URL": ("flow", "labs_base_url"),
            "FLOW2API_API_BASE_URL": ("flow", "api_base_url"),
            "FLOW2API_TIMEOUT": ("flow", "timeout"),
            "FLOW2API_MAX_RETRIES": ("flow", "max_retries"),
            "FLOW2API_POLL_INTERVAL": ("flow", "poll_interval"),
            "FLOW2API_MAX_POLL_ATTEMPTS": ("flow", "max_poll_attempts"),
            "FLOW2API_HOST": ("server", "host"),
            "FLOW2API_PORT": ("server", "port"),
            "FLOW2API_DEBUG_ENABLED": ("debug", "enabled"),
            "FLOW2API_DEBUG_LOG_REQUESTS": ("debug", "log_requests"),
            "FLOW2API_DEBUG_LOG_RESPONSES": ("debug", "log_responses"),
            "FLOW2API_DEBUG_MASK_TOKEN": ("debug", "mask_token"),
            "FLOW2API_PROXY_ENABLED": ("proxy", "proxy_enabled"),
            "FLOW2API_PROXY_URL": ("proxy", "proxy_url"),
            "FLOW2API_IMAGE_TIMEOUT": ("generation", "image_timeout"),
            "FLOW2API_VIDEO_TIMEOUT": ("generation", "video_timeout"),
            "FLOW2API_CACHE_ENABLED": ("cache", "enabled"),
            "FLOW2API_CACHE_TIMEOUT": ("cache", "timeout"),
            "FLOW2API_CACHE_BASE_URL": ("cache", "base_url"),
        }

        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                overrides[env_var] = {
                    "section": section,
                    "key": key,
                    "env_value": env_value,
                    "config_value": self._config.get(section, {}).get(key)
                }

        return overrides

    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw configuration dictionary"""
        return self._config

    @property
    def admin_username(self) -> str:
        # If admin_username is set from database, use it; otherwise fall back to config file
        if self._admin_username is not None:
            return self._admin_username
        return self._config["global"]["admin_username"]

    @admin_username.setter
    def admin_username(self, value: str):
        self._admin_username = value
        self._config["global"]["admin_username"] = value

    def set_admin_username_from_db(self, username: str):
        """Set admin username from database"""
        self._admin_username = username

    # Flow2API specific properties
    @property
    def flow_labs_base_url(self) -> str:
        """Google Labs base URL for project management"""
        return self._config["flow"]["labs_base_url"]

    @property
    def flow_api_base_url(self) -> str:
        """Google AI Sandbox API base URL for generation"""
        return self._config["flow"]["api_base_url"]

    @property
    def flow_timeout(self) -> int:
        return self._config["flow"]["timeout"]

    @property
    def flow_max_retries(self) -> int:
        return self._config["flow"]["max_retries"]

    @property
    def poll_interval(self) -> float:
        return self._config["flow"]["poll_interval"]

    @property
    def max_poll_attempts(self) -> int:
        return self._config["flow"]["max_poll_attempts"]

    @property
    def server_host(self) -> str:
        return self._config["server"]["host"]

    @property
    def server_port(self) -> int:
        return self._config["server"]["port"]

    @property
    def debug_enabled(self) -> bool:
        return self._config.get("debug", {}).get("enabled", False)

    @property
    def debug_log_requests(self) -> bool:
        return self._config.get("debug", {}).get("log_requests", True)

    @property
    def debug_log_responses(self) -> bool:
        return self._config.get("debug", {}).get("log_responses", True)

    @property
    def debug_mask_token(self) -> bool:
        return self._config.get("debug", {}).get("mask_token", True)

    # Mutable properties for runtime updates
    @property
    def api_key(self) -> str:
        return self._config["global"]["api_key"]

    @api_key.setter
    def api_key(self, value: str):
        self._config["global"]["api_key"] = value

    @property
    def admin_password(self) -> str:
        # If admin_password is set from database, use it; otherwise fall back to config file
        if self._admin_password is not None:
            return self._admin_password
        return self._config["global"]["admin_password"]

    @admin_password.setter
    def admin_password(self, value: str):
        self._admin_password = value
        self._config["global"]["admin_password"] = value

    def set_admin_password_from_db(self, password: str):
        """Set admin password from database"""
        self._admin_password = password

    def set_debug_enabled(self, enabled: bool):
        """Set debug mode enabled/disabled"""
        if "debug" not in self._config:
            self._config["debug"] = {}
        self._config["debug"]["enabled"] = enabled

    @property
    def image_timeout(self) -> int:
        """Get image generation timeout in seconds"""
        return self._config.get("generation", {}).get("image_timeout", 300)

    def set_image_timeout(self, timeout: int):
        """Set image generation timeout in seconds"""
        if "generation" not in self._config:
            self._config["generation"] = {}
        self._config["generation"]["image_timeout"] = timeout

    @property
    def video_timeout(self) -> int:
        """Get video generation timeout in seconds"""
        return self._config.get("generation", {}).get("video_timeout", 1500)

    def set_video_timeout(self, timeout: int):
        """Set video generation timeout in seconds"""
        if "generation" not in self._config:
            self._config["generation"] = {}
        self._config["generation"]["video_timeout"] = timeout

    # Cache configuration
    @property
    def cache_enabled(self) -> bool:
        """Get cache enabled status"""
        return self._config.get("cache", {}).get("enabled", False)

    def set_cache_enabled(self, enabled: bool):
        """Set cache enabled status"""
        if "cache" not in self._config:
            self._config["cache"] = {}
        self._config["cache"]["enabled"] = enabled

    @property
    def cache_timeout(self) -> int:
        """Get cache timeout in seconds"""
        return self._config.get("cache", {}).get("timeout", 7200)

    def set_cache_timeout(self, timeout: int):
        """Set cache timeout in seconds"""
        if "cache" not in self._config:
            self._config["cache"] = {}
        self._config["cache"]["timeout"] = timeout

    @property
    def cache_base_url(self) -> str:
        """Get cache base URL"""
        return self._config.get("cache", {}).get("base_url", "")

    def set_cache_base_url(self, base_url: str):
        """Set cache base URL"""
        if "cache" not in self._config:
            self._config["cache"] = {}
        self._config["cache"]["base_url"] = base_url

# Global config instance
config = Config()
