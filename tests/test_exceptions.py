import pytest

from sysstatus.exceptions import (
    NetworkError,
    SysStatusError,
    SystemInfoError,
    WeatherAPIError,
)


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_sysstatus_error_inheritance(self):
        """Test that SysStatusError inherits from Exception."""
        assert issubclass(SysStatusError, Exception)

    def test_network_error_inheritance(self):
        """Test that NetworkError inherits from SysStatusError."""
        assert issubclass(NetworkError, SysStatusError)
        assert issubclass(NetworkError, Exception)

    def test_weather_api_error_inheritance(self):
        """Test that WeatherAPIError inherits from SysStatusError."""
        assert issubclass(WeatherAPIError, SysStatusError)
        assert issubclass(WeatherAPIError, Exception)

    def test_system_info_error_inheritance(self):
        """Test that SystemInfoError inherits from SysStatusError."""
        assert issubclass(SystemInfoError, SysStatusError)
        assert issubclass(SystemInfoError, Exception)

    def test_sysstatus_error_message(self):
        """Test SysStatusError with message."""
        error = SysStatusError("Test error message")
        assert str(error) == "Test error message"

    def test_network_error_message(self):
        """Test NetworkError with message."""
        error = NetworkError("Network connection failed")
        assert str(error) == "Network connection failed"

    def test_weather_api_error_message(self):
        """Test WeatherAPIError with message."""
        error = WeatherAPIError("API key invalid")
        assert str(error) == "API key invalid"

    def test_system_info_error_message(self):
        """Test SystemInfoError with message."""
        error = SystemInfoError("Cannot read system file")
        assert str(error) == "Cannot read system file"

    def test_exception_raising_and_catching(self):
        """Test raising and catching custom exceptions."""
        # Test raising SysStatusError
        with pytest.raises(SysStatusError):
            raise SysStatusError("Base error")

        # Test raising NetworkError
        with pytest.raises(NetworkError):
            raise NetworkError("Network error")

        # Test catching NetworkError as SysStatusError
        try:
            raise NetworkError("Network error")
        except SysStatusError as e:
            assert isinstance(e, NetworkError)
            assert str(e) == "Network error"

        # Test raising WeatherAPIError
        with pytest.raises(WeatherAPIError):
            raise WeatherAPIError("Weather API error")

        # Test catching WeatherAPIError as SysStatusError
        try:
            raise WeatherAPIError("Weather API error")
        except SysStatusError as e:
            assert isinstance(e, WeatherAPIError)
            assert str(e) == "Weather API error"

        # Test raising SystemInfoError
        with pytest.raises(SystemInfoError):
            raise SystemInfoError("System info error")

        # Test catching SystemInfoError as SysStatusError
        try:
            raise SystemInfoError("System info error")
        except SysStatusError as e:
            assert isinstance(e, SystemInfoError)
            assert str(e) == "System info error"
