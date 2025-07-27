"""Integration tests for sysstatus package."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import requests

from sysstatus.cli import main
from sysstatus.config import Config
from sysstatus.core import SystemInfo
from tests.conftest import MockResponse


class TestIntegration:
    """Integration test cases."""

    def test_end_to_end_success(self):
        """Test complete end-to-end functionality."""
        mock_weather_data = {
            "cod": 200,
            "main": {"temp": 25.5},
            "weather": [{"description": "clear sky"}],
            "name": "TestCity",
        }

        with (
            patch("socket.socket") as mock_socket,
            patch("subprocess.run") as mock_subprocess,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.open") as mock_open,
            patch("requests.get") as mock_requests,
            patch("datetime.datetime") as mock_datetime,
        ):

            # Mock IP address
            mock_socket_instance = mock_socket.return_value.__enter__.return_value
            mock_socket_instance.getsockname.return_value = ("192.168.1.100", 12345)

            # Mock router IP
            mock_subprocess.return_value.stdout = "default via 192.168.1.1 dev eth0"

            # Mock uptime
            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.readline.return_value = "12345.67 98765.43\n"

            # Mock current time
            mock_now = mock_datetime.now.return_value
            mock_now.strftime.return_value = "2023-12-01 12:00:00"

            # Mock weather API
            mock_requests.return_value = MockResponse(mock_weather_data)

            # Create config with API key
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".env", delete=False
            ) as f:
                f.write("WEATHER_API_KEY=test_key\nDEFAULT_CITY=TestCity\n")
                f.flush()

                config = Config(f.name)
                sys_info = SystemInfo(config)

                info = sys_info.get_all_info()

                assert info["IP Address"] == "192.168.1.100"
                assert info["Router IP"] == "192.168.1.1"
                assert info["Date/Time"] == "2023-12-01 12:00:00"
                assert "3h 25m 45s" in info["Uptime"]
                assert "TestCity: 25.5°C, clear sky" in info["Weather"]

            # Cleanup
            Path(f.name).unlink()

    def test_cli_integration(self):
        """Test CLI integration with mocked system calls."""
        mock_weather_data = {
            "cod": 200,
            "main": {"temp": 20.0},
            "weather": [{"description": "cloudy"}],
            "name": "TestCity",
        }

        with (
            patch("socket.socket") as mock_socket,
            patch("subprocess.run") as mock_subprocess,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.open") as mock_open,
            patch("requests.get") as mock_requests,
            patch("datetime.datetime") as mock_datetime,
            patch("os.environ", {"WEATHER_API_KEY": "test_key"}),
        ):

            # Setup mocks
            mock_socket_instance = mock_socket.return_value.__enter__.return_value
            mock_socket_instance.getsockname.return_value = ("10.0.0.1", 12345)

            mock_subprocess.return_value.stdout = "default via 10.0.0.1 dev wlan0"

            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.readline.return_value = "86400.0 172800.0\n"

            mock_now = mock_datetime.now.return_value
            mock_now.strftime.return_value = "2023-12-01 15:30:00"

            mock_requests.return_value = MockResponse(mock_weather_data)

            # Test CLI execution
            result = main(["--no-colors"])
            assert result == 0

    def test_error_handling_integration(self):
        """Test error handling in integration scenario."""
        with (
            patch("socket.socket") as mock_socket,
            patch("subprocess.run") as mock_subprocess,
            patch("pathlib.Path.exists", return_value=False),
            patch("requests.get") as mock_requests,
            patch("os.environ", {"WEATHER_API_KEY": "test_key"}),
        ):

            # Mock IP address success
            mock_socket_instance = mock_socket.return_value.__enter__.return_value
            mock_socket_instance.getsockname.return_value = ("192.168.1.100", 12345)

            # Mock router IP failure
            mock_subprocess.side_effect = subprocess.SubprocessError("Command failed")

            # Mock weather API failure
            mock_requests.side_effect = requests.ConnectionError("Network error")

            config = Config()
            sys_info = SystemInfo(config)

            info = sys_info.get_all_info()

            # Should have IP address
            assert info["IP Address"] == "192.168.1.100"

            # Should handle router IP error gracefully
            assert info["Router IP"] == "Not available"

            # Should handle uptime error gracefully
            assert "Error:" in info["Uptime"]

            # Should handle weather error gracefully
            assert "Error:" in info["Weather"]

    def test_config_precedence_integration(self):
        """Test configuration precedence (env file vs environment variables)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("WEATHER_API_KEY=file_key\nDEFAULT_CITY=FileCity\n")
            f.flush()

            # Environment variable should override file
            with patch(
                "os.environ", {"WEATHER_API_KEY": "env_key", "DEFAULT_CITY": "EnvCity"}
            ):
                config = Config(f.name)

                # Environment variables take precedence
                assert config.weather_api_key == "env_key"
                assert config.default_city == "EnvCity"

        # Cleanup
        Path(f.name).unlink()
