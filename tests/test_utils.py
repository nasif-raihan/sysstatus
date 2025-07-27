"""Tests for utility functions."""

import logging
import sys

import pytest

from sysstatus.utils import format_uptime, safe_get_nested, setup_logging


class TestFormatUptime:
    """Test cases for format_uptime function."""

    def test_format_uptime_seconds_only(self):
        """Test formatting uptime with seconds only."""
        assert format_uptime(45.7) == "45s"

    def test_format_uptime_minutes_and_seconds(self):
        """Test formatting uptime with minutes and seconds."""
        assert format_uptime(125.3) == "2m 5s"

    def test_format_uptime_hours_minutes_seconds(self):
        """Test formatting uptime with hours, minutes, and seconds."""
        assert format_uptime(3725.8) == "1h 2m 5s"

    def test_format_uptime_days_hours_minutes_seconds(self):
        """Test formatting uptime with days, hours, minutes, and seconds."""
        assert format_uptime(90125.2) == "1d 1h 2m 5s"

    def test_format_uptime_zero(self):
        """Test formatting zero uptime."""
        assert format_uptime(0) == "0s"

    def test_format_uptime_exact_minute(self):
        """Test formatting exact minute."""
        assert format_uptime(60) == "1m"

    def test_format_uptime_exact_hour(self):
        """Test formatting exact hour."""
        assert format_uptime(3600) == "1h"

    def test_format_uptime_exact_day(self):
        """Test formatting exact day."""
        assert format_uptime(86400) == "1d"

    def test_format_uptime_large_value(self):
        """Test formatting very large uptime value."""
        # 10 days, 5 hours, 30 minutes, 45 seconds
        uptime = 10 * 86400 + 5 * 3600 + 30 * 60 + 45
        assert format_uptime(uptime) == "10d 5h 30m 45s"


class TestSafeGetNested:
    """Test cases for safe_get_nested function."""

    def test_safe_get_nested_success(self):
        """Test successful nested dictionary access."""
        data = {"level1": {"level2": {"level3": "value"}}}

        result = safe_get_nested(data, "level1", "level2", "level3")
        assert result == "value"

    def test_safe_get_nested_missing_key(self):
        """Test nested dictionary access with missing key."""
        data = {"level1": {"level2": {}}}

        result = safe_get_nested(data, "level1", "level2", "missing")
        assert result is None

    def test_safe_get_nested_with_default(self):
        """Test nested dictionary access with custom default."""
        data = {"level1": {}}

        result = safe_get_nested(data, "level1", "missing", default="default_value")
        assert result == "default_value"

    def test_safe_get_nested_non_dict_intermediate(self):
        """Test nested dictionary access with non-dict intermediate value."""
        data = {"level1": "not_a_dict"}

        result = safe_get_nested(data, "level1", "level2")
        assert result is None

    def test_safe_get_nested_empty_keys(self):
        """Test nested dictionary access with no keys."""
        data = {"key": "value"}

        result = safe_get_nested(data)
        assert result == data

    def test_safe_get_nested_none_data(self):
        """Test nested dictionary access with None data."""
        result = safe_get_nested(None, "key")
        assert result is None


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_setup_logging_default_level(self):
        """Test logging setup with default level."""
        logger = setup_logging()

        assert logger.name == "sysstatus"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        logger = setup_logging("DEBUG")

        assert logger.level == logging.DEBUG

    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level."""
        with pytest.raises(AttributeError):
            setup_logging("INVALID_LEVEL")

    def test_setup_logging_idempotent(self):
        """Test that setup_logging doesn't add duplicate handlers."""
        logger1 = setup_logging()
        initial_handler_count = len(logger1.handlers)

        logger2 = setup_logging()
        assert len(logger2.handlers) == initial_handler_count
        assert logger1 is logger2

    def test_setup_logging_formatter(self):
        """Test logging formatter configuration."""
        logger = setup_logging()
        handler = logger.handlers[0]
        formatter = handler.formatter

        # Test formatter format string
        expected_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert formatter._fmt == expected_format

    def test_setup_logging_handler_stream(self):
        """Test logging handler uses stderr."""
        logger = setup_logging()
        handler = logger.handlers[0]

        assert handler.stream is sys.stderr
