"""Tests for core system information functionality."""

import subprocess
from unittest.mock import Mock, mock_open, patch

import pytest
import requests

from sysstatus.core import SystemInfo
from sysstatus.exceptions import SystemInfoError, WeatherAPIError
from tests.conftest import MockResponse


class TestSystemInfo:
    """Test cases for SystemInfo class."""

    def test_init_with_config(self, mock_config):
        """Test SystemInfo initialization with config."""
        sys_info = SystemInfo(mock_config)
        assert sys_info.config == mock_config
        assert sys_info.logger is not None

    def test_init_without_config(self):
        """Test SystemInfo initialization without config."""
        with patch("sysstatus.core.Config") as mock_config_class:
            mock_config_instance = Mock()
            mock_config_class.return_value = mock_config_instance

            sys_info = SystemInfo()
            assert sys_info.config == mock_config_instance
            mock_config_class.assert_called_once_with()


class TestGetIPAddress:
    """Test cases for get_ip_address method."""

    def test_get_ip_address_success(self, system_info):
        """Test successful IP address retrieval."""
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = Mock()
            mock_socket.return_value.__enter__.return_value = mock_socket_instance
            mock_socket_instance.getsockname.return_value = ("192.168.1.100", 12345)

            ip = system_info.get_ip_address()
            assert ip == "192.168.1.100"

    def test_get_ip_address_fallback_to_hostname(self, system_info):
        """Test fallback to hostname resolution."""
        with (
            patch("socket.socket") as mock_socket,
            patch("socket.gethostbyname") as mock_gethostbyname,
            patch("socket.gethostname") as mock_gethostname,
        ):

            # First method fails
            mock_socket.return_value.__enter__.return_value.connect.side_effect = (
                Exception("Network error")
            )

            # Fallback succeeds
            mock_gethostname.return_value = "test-host"
            mock_gethostbyname.return_value = "127.0.0.1"

            ip = system_info.get_ip_address()
            assert ip == "127.0.0.1"

    def test_get_ip_address_failure(self, system_info):
        """Test IP address retrieval failure."""
        with (
            patch("socket.socket") as mock_socket,
            patch("socket.gethostbyname") as mock_gethostbyname,
        ):

            mock_socket.return_value.__enter__.return_value.connect.side_effect = (
                Exception("Network error")
            )
            mock_gethostbyname.side_effect = Exception("Hostname resolution failed")

            with pytest.raises(SystemInfoError, match="Cannot determine IP address"):
                system_info.get_ip_address()


class TestGetRouterIP:
    """Test cases for get_router_ip method."""

    def test_get_router_ip_success(self, system_info, mock_ip_route_output):
        """Test successful router IP retrieval."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_ip_route_output

            router_ip = system_info.get_router_ip()
            assert router_ip == "192.168.1.1"

    def test_get_router_ip_no_default_route(self, system_info):
        """Test router IP retrieval with no default route."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = (
                "192.168.1.0/24 dev eth0 proto kernel scope link"
            )

            router_ip = system_info.get_router_ip()
            assert router_ip is None

    def test_get_router_ip_subprocess_error(self, system_info):
        """Test router IP retrieval with subprocess error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("Command failed")

            router_ip = system_info.get_router_ip()
            assert router_ip is None

    def test_get_router_ip_timeout(self, system_info):
        """Test router IP retrieval with timeout."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("ip", 5)

            router_ip = system_info.get_router_ip()
            assert router_ip is None


class TestGetCurrentTime:
    """Test cases for get_current_time method."""

    def test_get_current_time(self, system_info):
        """Test current time retrieval."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "2023-12-01 12:00:00"
            mock_datetime.now.return_value = mock_now

            current_time = system_info.get_current_time()
            assert current_time == "2023-12-01 12:00:00"
            mock_now.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")


class TestGetUptime:
    """Test cases for get_uptime method."""

    def test_get_uptime_success(self, system_info, mock_uptime_file):
        """Test successful uptime retrieval."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.open", mock_open(read_data=mock_uptime_file)),
        ):

            uptime = system_info.get_uptime()
            # 12345.67 seconds = 3h 25m 45s
            assert uptime == "3h 25m 45s"

    def test_get_uptime_file_not_found(self, system_info):
        """Test uptime retrieval when /proc/uptime doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(SystemInfoError, match="Cannot read system uptime"):
                system_info.get_uptime()

    def test_get_uptime_io_error(self, system_info):
        """Test uptime retrieval with IO error."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.open", side_effect=IOError("Permission denied")),
        ):

            with pytest.raises(SystemInfoError, match="Cannot parse uptime"):
                system_info.get_uptime()

    def test_get_uptime_invalid_format(self, system_info):
        """Test uptime retrieval with invalid file format."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.open", mock_open(read_data="invalid_format")),
        ):

            with pytest.raises(SystemInfoError, match="Cannot parse uptime"):
                system_info.get_uptime()


class TestGetWeather:
    """Test cases for get_weather method."""

    def test_get_weather_success(self, system_info, mock_weather_response):
        """Test successful weather retrieval."""
        with patch("requests.get") as mock_get:
            mock_get.return_value = MockResponse(mock_weather_response)

            weather = system_info.get_weather("TestCity")
            assert weather == "TestCity: 25.5°C, clear sky"

    def test_get_weather_default_city(self, system_info, mock_weather_response):
        """Test weather retrieval with default city."""
        with patch("requests.get") as mock_get:
            mock_get.return_value = MockResponse(mock_weather_response)

            weather = system_info.get_weather()
            assert "TestCity" in weather  # Default city from mock config

    def test_get_weather_no_api_key(self, system_info):
        """Test weather retrieval without API key."""
        system_info.config.weather_api_key = None

        with pytest.raises(WeatherAPIError, match="Weather API key not configured"):
            system_info.get_weather()

    def test_get_weather_api_error_response(self, system_info):
        """Test weather retrieval with API error response."""
        error_response = {"cod": 404, "message": "city not found"}

        with patch("requests.get") as mock_get:
            mock_get.return_value = MockResponse(error_response)

            with pytest.raises(
                WeatherAPIError, match="Weather API error: city not found"
            ):
                system_info.get_weather("NonExistentCity")

    def test_get_weather_http_error(self, system_info):
        """Test weather retrieval with HTTP error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.HTTPError("HTTP 500 Error")

            with pytest.raises(WeatherAPIError, match="Failed to fetch weather data"):
                system_info.get_weather()

    def test_get_weather_timeout(self, system_info):
        """Test weather retrieval with timeout."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")

            with pytest.raises(WeatherAPIError, match="Failed to fetch weather data"):
                system_info.get_weather()

    def test_get_weather_invalid_json(self, system_info):
        """Test weather retrieval with invalid JSON response."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            with pytest.raises(WeatherAPIError, match="Failed to parse weather data"):
                system_info.get_weather()

    def test_get_weather_missing_temperature(self, system_info):
        """Test weather retrieval with missing temperature data."""
        invalid_response = {
            "cod": 200,
            "weather": [{"description": "clear sky"}],
            # Missing 'main' section with temperature
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value = MockResponse(invalid_response)

            with pytest.raises(WeatherAPIError, match="Invalid weather data format"):
                system_info.get_weather()

    def test_get_weather_missing_description(self, system_info):
        """Test weather retrieval with missing weather description."""
        invalid_response = {
            "cod": 200,
            "main": {"temp": 25.5},
            "weather": [],  # Empty weather array
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value = MockResponse(invalid_response)

            with pytest.raises(WeatherAPIError, match="Invalid weather data format"):
                system_info.get_weather()


class TestGetAllInfo:
    """Test cases for get_all_info method."""

    def test_get_all_info_success(self, system_info, mock_weather_response):
        """Test successful retrieval of all system information."""
        with (
            patch.object(system_info, "get_ip_address", return_value="192.168.1.100"),
            patch.object(system_info, "get_router_ip", return_value="192.168.1.1"),
            patch.object(
                system_info, "get_current_time", return_value="2023-12-01 12:00:00"
            ),
            patch.object(system_info, "get_uptime", return_value="1d 2h 30m"),
            patch.object(
                system_info, "get_weather", return_value="TestCity: 25°C, clear"
            ),
        ):

            info = system_info.get_all_info()

            assert info["IP Address"] == "192.168.1.100"
            assert info["Router IP"] == "192.168.1.1"
            assert info["Date/Time"] == "2023-12-01 12:00:00"
            assert info["Uptime"] == "1d 2h 30m"
            assert info["Weather"] == "TestCity: 25°C, clear"

    def test_get_all_info_without_weather(self, system_info):
        """Test retrieval of system information without weather."""
        with (
            patch.object(system_info, "get_ip_address", return_value="192.168.1.100"),
            patch.object(system_info, "get_router_ip", return_value="192.168.1.1"),
            patch.object(
                system_info, "get_current_time", return_value="2023-12-01 12:00:00"
            ),
            patch.object(system_info, "get_uptime", return_value="1d 2h 30m"),
        ):

            info = system_info.get_all_info(include_weather=False)

            assert "Weather" not in info
            assert len(info) == 4

    def test_get_all_info_with_errors(self, system_info):
        """Test retrieval of system information with some errors."""
        with (
            patch.object(
                system_info, "get_ip_address", side_effect=SystemInfoError("IP error")
            ),
            patch.object(system_info, "get_router_ip", return_value=None),
            patch.object(
                system_info, "get_current_time", return_value="2023-12-01 12:00:00"
            ),
            patch.object(
                system_info, "get_uptime", side_effect=SystemInfoError("Uptime error")
            ),
            patch.object(
                system_info, "get_weather", side_effect=WeatherAPIError("Weather error")
            ),
        ):

            info = system_info.get_all_info()

            assert "Error: IP error" in info["IP Address"]
            assert info["Router IP"] == "Not available"
            assert info["Date/Time"] == "2023-12-01 12:00:00"
            assert "Error: Uptime error" in info["Uptime"]
            assert "Error: Weather error" in info["Weather"]
