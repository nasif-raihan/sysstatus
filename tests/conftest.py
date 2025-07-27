"""Pytest configuration and fixtures."""

import os
import tempfile
from unittest.mock import Mock, patch
from typing import Dict, Any

import pytest
import requests

from sysstatus.config import Config
from sysstatus.core import SystemInfo


@pytest.fixture
def mock_env_file():
    """Create a temporary .env file for testing."""
    content = """
WEATHER_API_KEY=test_api_key_12345
DEFAULT_CITY=TestCity
REQUEST_TIMEOUT=5
WEATHER_API_URL=http://test.api.com/weather?q={city}&appid={api_key}&units=metric
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(content.strip())
        f.flush()
        yield f.name

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def clean_env():
    """Clean environment variables before and after tests."""
    # Store original values
    original_env = {}
    env_vars = ["WEATHER_API_KEY", "DEFAULT_CITY", "REQUEST_TIMEOUT", "WEATHER_API_URL"]

    for var in env_vars:
        original_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_env.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock(spec=Config)
    config.weather_api_key = "test_api_key"
    config.default_city = "TestCity"
    config.timeout = 10
    config.weather_url_template = (
        "http://api.test.com/weather?q={city}&appid={api_key}&units=metric"
    )
    return config


@pytest.fixture
def system_info(mock_config):
    """Create SystemInfo instance with mock config."""
    return SystemInfo(mock_config)


@pytest.fixture
def mock_weather_response():
    """Mock weather API response data."""
    return {
        "coord": {"lon": 90.4074, "lat": 23.7104},
        "weather": [
            {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
        ],
        "base": "stations",
        "main": {
            "temp": 25.5,
            "feels_like": 27.2,
            "temp_min": 24.0,
            "temp_max": 27.0,
            "pressure": 1013,
            "humidity": 60,
        },
        "visibility": 10000,
        "wind": {"speed": 3.5, "deg": 180},
        "clouds": {"all": 0},
        "dt": 1640995200,
        "sys": {
            "type": 1,
            "id": 1234,
            "country": "BD",
            "sunrise": 1640995200,
            "sunset": 1641038400,
        },
        "timezone": 21600,
        "id": 1185241,
        "name": "TestCity",
        "cod": 200,
    }


@pytest.fixture
def mock_uptime_file():
    """Mock /proc/uptime file content."""
    return "12345.67 98765.43\n"


@pytest.fixture
def mock_ip_route_output():
    """Mock ip route command output."""
    return """default via 192.168.1.1 dev eth0 proto dhcp metric 100
10.0.0.0/8 dev docker0 proto kernel scope link src 172.17.0.1 linkdown
192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100 metric 100"""


class MockResponse:
    """Mock requests.Response object."""

    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError(f"HTTP {self.status_code}")


@pytest.fixture
def mock_requests_get():
    """Mock requests.get function."""
    with patch("requests.get") as mock:
        yield mock
