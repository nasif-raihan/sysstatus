"""Custom exceptions for sysstatus package."""


class SysStatusError(Exception):
    """Base exception for sysstatus package."""

    pass


class NetworkError(SysStatusError):
    """Raised when network operations fail."""

    pass


class WeatherAPIError(SysStatusError):
    """Raised when weather API operations fail."""

    pass


class SystemInfoError(SysStatusError):
    """Raised when system information cannot be retrieved."""

    pass
