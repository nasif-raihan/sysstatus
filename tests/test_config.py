"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest

from sysstatus.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_default_config(self, clean_env):
        """Test configuration with default values."""
        config = Config()

        assert config.weather_api_key is not None
        assert config.default_city == "Dhaka"
        assert config.timeout == 10
        assert "openweathermap.org" in config.weather_url_template

    def test_config_from_env_file(self, mock_env_file, clean_env):
        """Test configuration loading from .env file."""
        config = Config(mock_env_file)

        assert config.weather_api_key == "test_api_key_12345"
        assert config.default_city == "TestCity"
        assert config.timeout == 5
        assert "test.api.com" in config.weather_url_template

    def test_config_from_environment_variables(self, clean_env):
        """Test configuration from environment variables."""
        os.environ["WEATHER_API_KEY"] = "env_api_key"
        os.environ["DEFAULT_CITY"] = "EnvCity"
        os.environ["REQUEST_TIMEOUT"] = "15"

        config = Config()

        assert config.weather_api_key == "env_api_key"
        assert config.default_city == "EnvCity"
        assert config.timeout == 15

    def test_find_env_file_in_current_directory(self, clean_env):
        """Test automatic .env file discovery in current directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("WEATHER_API_KEY=auto_discovered")

            # Change to temp directory
            original_cwd = Path.cwd()
            os.chdir(temp_dir)

            try:
                config = Config()
                assert config.weather_api_key == "auto_discovered"
            finally:
                os.chdir(original_cwd)

    def test_find_env_file_in_parent_directory(self, clean_env):
        """Test automatic .env file discovery in parent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            parent_dir = Path(temp_dir)
            child_dir = parent_dir / "subdir"
            child_dir.mkdir()

            env_file = parent_dir / ".env"
            env_file.write_text("WEATHER_API_KEY=parent_discovered")

            # Change to child directory
            original_cwd = Path.cwd()
            os.chdir(child_dir)

            try:
                config = Config()
                assert config.weather_api_key == "parent_discovered"
            finally:
                os.chdir(original_cwd)

    def test_no_env_file_found(self, clean_env):
        """Test behavior when no .env file is found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            os.chdir(temp_dir)

            try:
                config = Config()
                # Should use defaults
                assert config.weather_api_key is None
                assert config.default_city == "Dhaka"
            finally:
                os.chdir(original_cwd)

    def test_invalid_timeout_value(self, clean_env):
        """Test handling of invalid timeout value."""
        os.environ["REQUEST_TIMEOUT"] = "invalid"

        with pytest.raises(ValueError):
            Config().timeout
