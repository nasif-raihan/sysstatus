"""Configuration management for sysstatus."""

import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """Configuration class for sysstatus."""

    def __init__(self, env_file: str | None = None):
        """Initialize configuration.

        Args:
            env_file: Path to .env file. If None, searches for .env in current directory.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            # Search for .env file in current directory and parent directories
            env_path = self._find_env_file()
            if env_path:
                load_dotenv(env_path)

    @staticmethod
    def _find_env_file() -> Path | None:
        """Find .env file in current or parent directories."""
        current_dir = Path.cwd()
        for directory in [current_dir] + list(current_dir.parents):
            env_file = directory / ".env"
            if env_file.exists():
                return env_file
        return None

    @property
    def weather_api_key(self) -> str | None:
        """Get weather API key from environment."""
        return os.getenv("WEATHER_API_KEY")

    @property
    def default_city(self) -> str | None:
        """Get default city for weather information."""
        return os.getenv("DEFAULT_CITY", "Dhaka")

    @property
    def timeout(self) -> int:
        """Get request timeout in seconds."""
        return int(os.getenv("REQUEST_TIMEOUT", "10"))

    @property
    def weather_url_template(self) -> str:
        """Get weather API URL template."""
        return os.getenv(
            "WEATHER_API_URL",
            "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric",
        )
