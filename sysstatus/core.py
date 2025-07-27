"""Core system information functionality."""

import datetime
import socket
import subprocess
from pathlib import Path
from typing import Any

import requests

from .config import Config
from .exceptions import SystemInfoError, WeatherAPIError
from .utils import format_uptime, safe_get_nested, setup_logging


class SystemInfo:
    """System information collector."""

    def __init__(self, config: Config | None = None):
        """Initialize SystemInfo.

        Args:
            config: Configuration instance. If None, creates default config.
        """
        self.config = config or Config()
        self.logger = setup_logging()

    def get_ip_address(self) -> str | Any:
        """Get local IP address.

        Returns:
            Local IP address as string

        Raises:
            SystemInfoError: If IP address cannot be determined
        """
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            self.logger.warning(f"Failed to get IP via socket: {e}")
            try:
                # Fallback to hostname resolution
                return socket.gethostbyname(socket.gethostname())
            except Exception as e:
                raise SystemInfoError(f"Cannot determine IP address: {e}")

    def get_router_ip(self) -> str | None:
        """Get default gateway (router) IP address.

        Returns:
            Router IP address or None if not found
        """
        try:
            result = subprocess.run(
                ["ip", "route"], capture_output=True, text=True, timeout=5, check=True
            )

            for line in result.stdout.splitlines():
                if line.strip().startswith("default"):
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.logger.warning(f"Failed to get router IP: {e}")

        return None

    @staticmethod
    def get_current_time() -> str:
        """Get current date and time.

        Returns:
            Formatted current datetime string
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_uptime() -> str:
        """Get system uptime.

        Returns:
            Formatted uptime string

        Raises:
            SystemInfoError: If uptime cannot be read
        """
        uptime_file = Path("/proc/uptime")

        if not uptime_file.exists():
            raise SystemInfoError("Cannot read system uptime: /proc/uptime not found")

        try:
            with uptime_file.open() as f:
                uptime_seconds = float(f.readline().split()[0])
            return format_uptime(uptime_seconds)
        except (IOError, ValueError, IndexError) as e:
            raise SystemInfoError(f"Cannot parse uptime: {e}")

    def get_weather(self, city: str | None = None) -> str:
        """Get weather information for specified city.

        Args:
            city: City name. If None, uses default from config.

        Returns:
            Formatted weather string

        Raises:
            WeatherAPIError: If weather data cannot be retrieved
        """
        city = city or self.config.default_city
        api_key = self.config.weather_api_key

        if not api_key:
            raise WeatherAPIError("Weather API key not configured")

        url = self.config.weather_url_template.format(city=city, api_key=api_key)
        self.logger.debug(f"{url=}")

        try:
            response = requests.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"{data=}")

            # Handle API error responses
            if data.get("cod") != 200:
                error_msg = data.get("message", "Unknown API error")
                raise WeatherAPIError(f"Weather API error: {error_msg}")

            temp = safe_get_nested(data, "main", "temp")
            weather_list = data.get("weather", [])
            description = None
            if weather_list and len(weather_list) > 0:
                description = weather_list[0].get("description")

            if temp is None or description is None:
                raise WeatherAPIError("Invalid weather data format")

            return f"{city}: {temp}°C, {description}"

        except requests.RequestException as e:
            raise WeatherAPIError(f"Failed to fetch weather data: {e}")
        except (KeyError, IndexError, ValueError) as e:
            raise WeatherAPIError(f"Failed to parse weather data: {e}")

    def get_all_info(self, include_weather: bool = True) -> dict[str, str]:
        """Get all system information.

        Args:
            include_weather: Whether to include weather information

        Returns:
            Dictionary containing all system information
        """
        info = {"Date/Time": self.get_current_time()}

        if include_weather:
            try:
                info["Weather"] = self.get_weather()
            except WeatherAPIError as e:
                info["Weather"] = f"Error: {e}"
                self.logger.error(f"Failed to get weather: {e}")

        try:
            info["IP Address"] = self.get_ip_address()
        except SystemInfoError as e:
            info["IP Address"] = f"Error: {e}"
            self.logger.error(f"Failed to get IP address: {e}")

        try:
            router_ip = self.get_router_ip()
            info["Router IP"] = router_ip if router_ip else "Not available"
        except Exception as e:
            info["Router IP"] = f"Error: {e}"
            self.logger.error(f"Failed to get router IP: {e}")

        try:
            info["Uptime"] = self.get_uptime()
        except SystemInfoError as e:
            info["Uptime"] = f"Error: {e}"
            self.logger.error(f"Failed to get uptime: {e}")

        return info
