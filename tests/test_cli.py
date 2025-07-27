"""Tests for command-line interface."""

from io import StringIO
from unittest.mock import Mock, patch

import pytest

from sysstatus.cli import Colors, create_parser, format_table, main
from sysstatus.exceptions import WeatherAPIError


class TestColors:
    """Test cases for Colors class."""

    def test_colors_defined(self):
        """Test that color constants are defined."""
        assert hasattr(Colors, "CYAN")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "RESET")
        assert hasattr(Colors, "BOLD")

        # Test that they are strings
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.RESET, str)


class TestFormatTable:
    """Test cases for format_table function."""

    def test_format_table_with_colors(self):
        """Test table formatting with colors."""
        data = {"IP Address": "192.168.1.100", "Weather": "Clear sky"}

        result = format_table(data, use_colors=True)

        assert "IP Address" in result
        assert "192.168.1.100" in result
        assert Colors.GREEN in result
        assert Colors.YELLOW in result
        assert Colors.RESET in result

    def test_format_table_without_colors(self):
        """Test table formatting without colors."""
        data = {"IP Address": "192.168.1.100", "Weather": "Clear sky"}

        result = format_table(data, use_colors=False)

        assert "IP Address" in result
        assert "192.168.1.100" in result
        assert Colors.GREEN not in result
        assert Colors.YELLOW not in result

    def test_format_table_with_errors(self):
        """Test table formatting with error messages."""
        data = {
            "IP Address": "192.168.1.100",
            "Weather": "Error: API key not configured",
        }

        result = format_table(data, use_colors=True)

        assert "Error:" in result
        assert Colors.RED in result

    def test_format_table_empty_data(self):
        """Test table formatting with empty data."""
        result = format_table({})
        assert result == "No system information available"

    def test_format_table_column_width_calculation(self):
        """Test proper column width calculation."""
        data = {"Short": "Value", "Very Long Label Name": "Short"}

        result = format_table(data, use_colors=False)
        lines = result.split("\n")

        # All lines should have consistent spacing
        header_length = len(lines[0])
        separator_length = len(lines[1])

        assert header_length == separator_length

        # Data rows should align properly
        for line in lines[2:]:
            assert " | " in line


class TestCreateParser:
    """Test cases for create_parser function."""

    def test_create_parser_basic(self):
        """Test basic parser creation."""
        parser = create_parser()

        assert parser.prog == "sysstatus"
        assert "Display system information" in parser.description

    def test_parser_no_weather_argument(self):
        """Test --no-weather argument."""
        parser = create_parser()
        args = parser.parse_args(["--no-weather"])

        assert args.no_weather is True

    def test_parser_no_colors_argument(self):
        """Test --no-colors argument."""
        parser = create_parser()
        args = parser.parse_args(["--no-colors"])

        assert args.no_colors is True

    def test_parser_city_argument(self):
        """Test --city argument."""
        parser = create_parser()
        args = parser.parse_args(["--city", "New York"])

        assert args.city == "New York"

    def test_parser_config_argument(self):
        """Test --config argument."""
        parser = create_parser()
        args = parser.parse_args(["--config", "/path/to/.env"])

        assert args.config == "/path/to/.env"

    def test_parser_log_level_argument(self):
        """Test --log-level argument."""
        parser = create_parser()
        args = parser.parse_args(["--log-level", "DEBUG"])

        assert args.log_level == "DEBUG"

    def test_parser_invalid_log_level(self):
        """Test invalid log level argument."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--log-level", "INVALID"])

    def test_parser_version_argument(self):
        """Test --version argument."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        assert exc_info.value.code == 0

    def test_parser_help_argument(self):
        """Test --help argument."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])

        assert exc_info.value.code == 0

    def test_parser_default_values(self):
        """Test parser default values."""
        parser = create_parser()
        args = parser.parse_args([])

        assert args.no_weather is False
        assert args.no_colors is False
        assert args.city is None
        assert args.config is None
        assert args.log_level == "WARNING"


class TestMain:
    """Test cases for main function."""

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_success(self, mock_setup_logging, mock_config, mock_system_info):
        """Test successful main execution."""
        # Setup mocks
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.return_value = {
            "IP Address": "192.168.1.100",
            "Weather": "Clear sky",
        }
        mock_system_info.return_value = mock_sys_info

        # Capture stdout
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main([])

            assert result == 0
            output = mock_stdout.getvalue()
            assert "IP Address" in output
            assert "192.168.1.100" in output

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_no_weather(self, mock_setup_logging, mock_config, mock_system_info):
        """Test main execution without weather."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.return_value = {"IP Address": "192.168.1.100"}
        mock_system_info.return_value = mock_sys_info

        result = main(["--no-weather"])

        assert result == 0
        mock_sys_info.get_all_info.assert_called_once_with(include_weather=False)

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_custom_city(self, mock_setup_logging, mock_config, mock_system_info):
        """Test main execution with custom city."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.return_value = {"IP Address": "192.168.1.100"}
        mock_sys_info.get_weather.return_value = "New York: 20°C, cloudy"
        mock_system_info.return_value = mock_sys_info

        result = main(["--city", "New York"])

        assert result == 0
        mock_sys_info.get_weather.assert_called_once_with("New York")

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_custom_city_weather_error(
        self, mock_setup_logging, mock_config, mock_system_info
    ):
        """Test main execution with custom city and weather error."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.return_value = {"IP Address": "192.168.1.100"}
        mock_sys_info.get_weather.side_effect = WeatherAPIError("API error")
        mock_system_info.return_value = mock_sys_info

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main(["--city", "InvalidCity"])

            assert result == 0
            output = mock_stdout.getvalue()
            assert "Error: API error" in output

    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_config_error(self, mock_setup_logging, mock_config):
        """Test main execution with configuration error."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config.side_effect = Exception("Config error")

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main([])

            assert result == 1
            error_output = mock_stderr.getvalue()
            assert "Error: Config error" in error_output

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_keyboard_interrupt(
        self, mock_setup_logging, mock_config, mock_system_info
    ):
        """Test main execution with keyboard interrupt."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.side_effect = KeyboardInterrupt()
        mock_system_info.return_value = mock_sys_info

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main([])

            assert result == 1
            error_output = mock_stderr.getvalue()
            assert "Operation cancelled by user" in error_output

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    @patch("sys.stdout.isatty")
    def test_main_no_colors_when_not_tty(
        self, mock_isatty, mock_setup_logging, mock_config, mock_system_info
    ):
        """Test that colors are disabled when output is not a TTY."""
        mock_isatty.return_value = False

        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.return_value = {"IP Address": "192.168.1.100"}
        mock_system_info.return_value = mock_sys_info

        with patch("sysstatus.cli.format_table") as mock_format_table:
            main([])

            # format_table should be called with use_colors=False
            mock_format_table.assert_called_once()
            args, kwargs = mock_format_table.call_args
            assert kwargs.get("use_colors") is False

    @patch("sysstatus.cli.SystemInfo")
    @patch("sysstatus.cli.Config")
    @patch("sysstatus.cli.setup_logging")
    def test_main_custom_config_file(
        self, mock_setup_logging, mock_config, mock_system_info
    ):
        """Test main execution with custom config file."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sys_info = Mock()
        mock_sys_info.get_all_info.return_value = {"IP Address": "192.168.1.100"}
        mock_system_info.return_value = mock_sys_info

        result = main(["--config", "/custom/.env"])

        assert result == 0
        mock_config.assert_called_once_with("/custom/.env")

    @patch("sysstatus.cli.setup_logging")
    def test_main_custom_log_level(self, mock_setup_logging):
        """Test main execution with custom log level."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger

        with (
            patch("sysstatus.cli.Config"),
            patch("sysstatus.cli.SystemInfo") as mock_system_info,
        ):

            mock_sys_info = Mock()
            mock_sys_info.get_all_info.return_value = {"IP Address": "192.168.1.100"}
            mock_system_info.return_value = mock_sys_info

            main(["--log-level", "DEBUG"])

            mock_setup_logging.assert_called_once_with("DEBUG")
