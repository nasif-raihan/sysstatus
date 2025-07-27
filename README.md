# SysStatus 🖥️

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/sysstatus.svg)](https://pypi.org/project/sysstatus/)
[![Build Status](https://img.shields.io/github/workflow/status/nasif-raihan/sysstatus/CI)](https://github.com/nasif-raihan/sysstatus/actions)
[![Coverage](https://img.shields.io/codecov/c/github/nasif-raihan/sysstatus.svg)](https://codecov.io/gh/nasif-raihan/sysstatus)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-grade system information display tool that provides comprehensive system status in a beautifully formatted table. SysStatus displays IP addresses, system uptime, current weather, and more with robust error handling and customizable output.

## ✨ Features

- **🌐 Network Information**: Local IP address and router/gateway detection
- **⏰ System Status**: Current date/time and detailed system uptime
- **🌤️ Weather Integration**: Real-time weather data from OpenWeatherMap API
- **🎨 Beautiful Output**: Colorized table format with terminal detection
- **⚡ Fast & Reliable**: Efficient data collection with graceful error handling
- **🔧 Configurable**: Environment-based configuration with sensible defaults
- **📱 CLI Interface**: Rich command-line interface with comprehensive options
- **🧪 Production Ready**: Comprehensive test suite and error handling
- **🐍 Modern Python**: Type hints, async-ready, and Python 3.10+ support

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install sysstatus

# Install from source
git clone https://github.com/nasif-raihan/sysstatus.git
cd sysstatus
pip install -e .
```

### Basic Usage

```bash
# Display all system information
sysstatus

# Skip weather information
sysstatus --no-weather

# Display without colors (useful for scripts)
sysstatus --no-colors

# Get weather for a different city
sysstatus --city "New York"
```

### Sample Output

```
Item       | Value
---------------------------------------
Date/Time  | 2023-12-01 15:30:45
Weather    | Dhaka: 28.5°C, light rain
IP Address | 192.168.1.100
Router IP  | 192.168.1.1
Uptime     | 2d 5h 30m 15s
```

## 📋 Requirements

- **Python**: 3.10 or higher
- **Dependencies**: `requests`, `python-dotenv`
- **Platform**: Linux/Unix (uses `/proc/uptime` and `ip route`)
- **Optional**: OpenWeatherMap API key for weather data

## ⚙️ Configuration

SysStatus uses environment variables for configuration. Create a `.env` file in your project directory or set environment variables directly.

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEATHER_API_KEY` | OpenWeatherMap API key | None | For weather data |
| `DEFAULT_CITY` | Default city for weather | `Dhaka` | No |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `10` | No |
| `WEATHER_API_URL` | Custom weather API URL template | OpenWeatherMap URL | No |

### Configuration File Example

Create a `.env` file:

```env
# Weather Configuration
WEATHER_API_KEY=your_openweathermap_api_key_here
DEFAULT_CITY=Dhaka

# Request Configuration  
REQUEST_TIMEOUT=10
```

### Getting Weather API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add the key to your `.env` file

## 🖥️ Command Line Interface

### Synopsis

```bash
sysstatus [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--no-weather` | Skip weather information retrieval |
| `--no-colors` | Disable colored output |
| `--city CITY` | Specify city for weather data |
| `--config FILE` | Path to custom .env configuration file |
| `--log-level LEVEL` | Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--version` | Show version information |
| `--help` | Show help message |

### Examples

```bash
# Basic usage with default settings
sysstatus

# Get weather for London instead of default city
sysstatus --city "London"

# Skip weather and disable colors (good for scripting)
sysstatus --no-weather --no-colors

# Use custom configuration file
sysstatus --config /path/to/custom/.env

# Enable debug logging
sysstatus --log-level DEBUG

# Combine multiple options
sysstatus --city "Tokyo" --no-colors --log-level INFO
```

## 🐍 Python API

You can also use SysStatus programmatically in your Python applications.

### Basic Usage

```python
from sysstatus import SystemInfo
from sysstatus.config import Config

# Create system info instance
sys_info = SystemInfo()

# Get all information
info = sys_info.get_all_info()
print(info)

# Get specific information
ip_address = sys_info.get_ip_address()
uptime = sys_info.get_uptime()
weather = sys_info.get_weather("Tokyo")
```

### Custom Configuration

```python
from sysstatus import SystemInfo
from sysstatus.config import Config

# Custom configuration
config = Config("/path/to/.env")
sys_info = SystemInfo(config)

# Get weather for specific city
weather = sys_info.get_weather("Paris")
print(weather)  # Output: Paris: 15.2°C, partly cloudy
```

### Error Handling

```python
from sysstatus import SystemInfo
from sysstatus.exceptions import WeatherAPIError, SystemInfoError

sys_info = SystemInfo()

try:
    weather = sys_info.get_weather("InvalidCity")
except WeatherAPIError as e:
    print(f"Weather error: {e}")

try:
    uptime = sys_info.get_uptime()
except SystemInfoError as e:
    print(f"System error: {e}")
```

## 🏗️ Architecture

SysStatus follows a modular architecture with clear separation of concerns:

```
sysstatus/
├── __init__.py          # Package initialization and exports
├── core.py              # Core system information logic
├── cli.py               # Command-line interface
├── config.py            # Configuration management
├── exceptions.py        # Custom exception classes
└── utils.py             # Utility functions and helpers
```

### Key Components

- **`SystemInfo`**: Main class for collecting system information
- **`Config`**: Configuration management with environment support
- **CLI**: Rich command-line interface with argument parsing
- **Exception Hierarchy**: Structured error handling
- **Utilities**: Helper functions for formatting and logging

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/nasif-raihan/sysstatus.git
cd sysstatus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sysstatus --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run with different Python versions
tox
```

### Code Quality

```bash
# Format code
black sysstatus tests

# Lint code
flake8 sysstatus tests

# Type checking
mypy sysstatus

# Run all quality checks
make lint
```

### Project Commands

The project includes a `Makefile` with common development tasks:

```bash
make help          # Show available commands
make install       # Install package in development mode
make install-dev   # Install with development dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts
make build         # Build package
make upload-test   # Upload to Test PyPI
make upload        # Upload to PyPI
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass (`pytest`)
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to your branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Development Guidelines

- **Code Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Add type annotations for all functions
- **Documentation**: Update docstrings and README as needed
- **Tests**: Maintain or improve test coverage
- **Commits**: Use conventional commit messages

## 🐛 Troubleshooting

### Common Issues

#### Weather API Not Working
```bash
# Check if API key is set
echo $WEATHER_API_KEY

# Test API key manually
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# Run with debug logging
sysstatus --log-level DEBUG
```

#### Permission Errors
```bash
# Check if /proc/uptime is readable
cat /proc/uptime

# Check if ip command is available
which ip
ip route show
```

#### Import Errors
```bash
# Ensure package is installed correctly
pip show sysstatus

# Reinstall if necessary
pip uninstall sysstatus
pip install sysstatus
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/nasif-raihan/sysstatus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nasif-raihan/sysstatus/discussions)
- **Email**: nasif.raihan78@gmail.com

## 📊 Performance

SysStatus is designed for efficiency:

- **Fast Execution**: Typically completes in under 2 seconds
- **Minimal Dependencies**: Only requires `requests` and `python-dotenv`
- **Memory Efficient**: Low memory footprint
- **Network Optimized**: Configurable timeouts and error handling
- **Caching Ready**: Easy to extend with caching mechanisms

### Benchmarks

| Operation | Average Time | Notes |
|-----------|--------------|-------|
| IP Detection | ~50ms | Local socket operation |
| Router Discovery | ~100ms | System command execution |
| Weather API | ~500ms | Network request (varies by location) |
| Total Execution | ~1-2s | Including all operations |

## 🔒 Security

- **API Keys**: Stored in environment variables, never in code
- **Input Validation**: All user inputs are validated and sanitized
- **Error Handling**: No sensitive information leaked in error messages
- **Dependencies**: Regular security updates and vulnerability scanning
- **Minimal Permissions**: No elevated privileges required

## 📈 Roadmap

### Upcoming Features

- **🔌 Plugin System**: Extensible architecture for custom data sources
- **💾 Caching**: Optional caching for weather and network data
- **📱 GUI Version**: Cross-platform desktop application
- **🌍 Internationalization**: Multi-language support
- **📊 Historical Data**: Track system metrics over time
- **🔔 Notifications**: Alert system for system changes
- **☁️ Cloud Integration**: Support for cloud provider APIs

### Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2023 Nasif Raihan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...
```

## 🙏 Acknowledgments

- **OpenWeatherMap**: Weather data API
- **Python Community**: Amazing ecosystem and tools
- **Contributors**: Everyone who helps improve this project
- **Inspiration**: System monitoring tools and CLI utilities

## 📞 Contact

**Nasif Raihan**
- **Email**: nasif.raihan78@gmail.com
- **GitHub**: [@nasif-raihan](https://github.com/nasif-raihan)
- **LinkedIn**: [nasif-raihan](https://linkedin.com/in/nasif-raihan)

---

<div align="center">

**[⭐ Star this project](https://github.com/nasif-raihan/sysstatus) • [🐛 Report Bug](https://github.com/nasif-raihan/sysstatus/issues) • [💡 Request Feature](https://github.com/nasif-raihan/sysstatus/issues)**

Made with ❤️ by [Nasif Raihan](https://github.com/nasif-raihan)

</div>