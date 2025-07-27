"""Command-line interface for sysstatus."""

import argparse
import sys

from .config import Config
from .core import SystemInfo
from .utils import setup_logging


class Colors:
    """ANSI color codes for terminal output."""

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def format_table(data: dict, use_colors: bool = True) -> str:
    """Format system information as a table.

    Args:
        data: Dictionary of system information
        use_colors: Whether to use ANSI colors

    Returns:
        Formatted table string
    """
    if not data:
        return "No system information available"

    # Calculate column widths
    label_width = max(len(str(key)) for key in data.keys())
    value_width = max(len(str(value)) for value in data.values())

    lines = []

    if use_colors:
        # Header with colors
        header = (
            f"{Colors.BOLD}{Colors.CYAN}"
            f"{'Item'.ljust(label_width)} | {'Value'.ljust(value_width)}"
            f"{Colors.RESET}"
        )
        separator = (
            f"{Colors.BOLD}{'-' * (label_width + value_width + 3)}{Colors.RESET}"
        )
    else:
        # Plain header
        header = f"{'Item'.ljust(label_width)} | {'Value'.ljust(value_width)}"
        separator = "-" * (label_width + value_width + 3)

    lines.append(header)
    lines.append(separator)

    # Data rows
    for label, value in data.items():
        if use_colors:
            if "Error:" in str(value):
                color_label = f"{Colors.RED}{label.ljust(label_width)}{Colors.RESET}"
                color_value = (
                    f"{Colors.RED}{str(value).ljust(value_width)}{Colors.RESET}"
                )
            else:
                color_label = f"{Colors.GREEN}{label.ljust(label_width)}{Colors.RESET}"
                color_value = (
                    f"{Colors.YELLOW}{str(value).ljust(value_width)}{Colors.RESET}"
                )

            lines.append(f"{color_label} | {color_value}")
        else:
            lines.append(
                f"{label.ljust(label_width)} | {str(value).ljust(value_width)}"
            )

    return "\n".join(lines)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Display system information", prog="sysstatus"
    )

    parser.add_argument(
        "--no-weather", action="store_true", help="Skip weather information"
    )

    parser.add_argument(
        "--no-colors", action="store_true", help="Disable colored output"
    )

    parser.add_argument("--city", type=str, help="City for weather information")

    parser.add_argument("--config", type=str, help="Path to configuration file (.env)")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Set logging level",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def main(args: list | None = None) -> int:
    """Main CLI entry point.

    Args:
        args: Command line arguments (for testing)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Set up logging
    logger = setup_logging(parsed_args.log_level)

    try:
        # Initialize configuration
        config = Config(parsed_args.config)

        # Create SystemInfo instance
        sys_info = SystemInfo(config)

        # Get system information
        include_weather = not parsed_args.no_weather

        # Get weather with custom city if specified
        if include_weather and parsed_args.city:
            try:
                info_data = sys_info.get_all_info(include_weather=False)
                weather_info = sys_info.get_weather(parsed_args.city)
                info_data["Weather"] = weather_info
            except Exception as e:
                info_data = sys_info.get_all_info(include_weather=False)
                info_data["Weather"] = f"Error: {e}"
        else:
            info_data = sys_info.get_all_info(include_weather=include_weather)

        # Format and display output
        use_colors = not parsed_args.no_colors and sys.stdout.isatty()
        formatted_output = format_table(info_data, use_colors=use_colors)

        print(formatted_output)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
