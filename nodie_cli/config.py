"""
Configuration management for Nodie CLI.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import appdirs

APP_NAME = "nodie"
APP_AUTHOR = "nodie"

# Default configuration
DEFAULT_CONFIG = {
    "api_url": "https://nodie.host/api",
    "heartbeat_interval": 30,
    "speedtest_interval": 300,
    "auto_reconnect": True,
    "log_level": "INFO",
}


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    env_dir = os.environ.get("NODIE_CONFIG_DIR")
    if env_dir:
        config_dir = Path(env_dir)
    else:
        config_dir = Path(appdirs.user_config_dir(APP_NAME, APP_AUTHOR))
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.json"


def get_pid_file() -> Path:
    """Get the PID file path."""
    return get_config_dir() / "nodie.pid"


def get_log_file() -> Path:
    """Get the log file path."""
    log_dir = get_config_dir() / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir / "nodie.log"


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    config_file = get_config_file()
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    if os.environ.get("NODIE_API_URL"):
        config["api_url"] = os.environ["NODIE_API_URL"]
    if os.environ.get("NODIE_LOG_LEVEL"):
        config["log_level"] = os.environ["NODIE_LOG_LEVEL"]
    
    # Load from file
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, IOError):
            pass
    
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_file = get_config_file()
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)


def get_config_value(key: str, default: Optional[Any] = None) -> Any:
    """Get a specific configuration value."""
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set a specific configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)
