"""Tests for configuration module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from nodie_cli.config import (
    DEFAULT_CONFIG,
    get_config_dir,
    get_config_file,
    load_config,
    save_config,
    get_config_value,
    set_config_value,
)


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("NODIE_CONFIG_DIR", tmpdir)
        yield Path(tmpdir)


def test_get_config_dir(temp_config_dir):
    """Test that config dir is created."""
    config_dir = get_config_dir()
    assert config_dir.exists()
    assert config_dir == temp_config_dir


def test_load_default_config(temp_config_dir):
    """Test loading default config when no file exists."""
    config = load_config()
    assert config["api_url"] == DEFAULT_CONFIG["api_url"]
    assert config["heartbeat_interval"] == DEFAULT_CONFIG["heartbeat_interval"]


def test_save_and_load_config(temp_config_dir):
    """Test saving and loading config."""
    test_config = {"api_url": "https://test.example.com", "custom_key": "custom_value"}
    save_config(test_config)
    
    loaded = load_config()
    assert loaded["api_url"] == "https://test.example.com"
    assert loaded["custom_key"] == "custom_value"


def test_get_config_value(temp_config_dir):
    """Test getting a specific config value."""
    save_config({"test_key": "test_value"})
    
    value = get_config_value("test_key")
    assert value == "test_value"
    
    default = get_config_value("nonexistent", "default")
    assert default == "default"


def test_set_config_value(temp_config_dir):
    """Test setting a specific config value."""
    set_config_value("new_key", "new_value")
    
    value = get_config_value("new_key")
    assert value == "new_value"


def test_env_override(temp_config_dir, monkeypatch):
    """Test that environment variables override config."""
    monkeypatch.setenv("NODIE_API_URL", "https://env.example.com")
    
    config = load_config()
    assert config["api_url"] == "https://env.example.com"
