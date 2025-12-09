[![CI](https://github.com/1devspace/office-screen/actions/workflows/ci.yml/badge.svg)](https://github.com/1devspace/office-screen/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/1devspace/office-screen)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

# office_screen

Advanced web automation tool for continuous browsing and monitoring of multiple websites. Built with Python and Selenium, featuring error handling, stealth capabilities, and performance monitoring.

## Features

- **Multi-site browsing**: Automatically cycles through configurable URLs
- **Error handling**: URL validation, browser crash recovery, retry logic
- **Stealth mode**: User agent rotation, proxy support, fingerprinting evasion
- **Performance monitoring**: Real-time metrics, adaptive intervals, memory management
- **Production ready**: 24/7 operation with graceful shutdown

## Requirements

- Python 3.7+
- Chrome browser (uses your system's Chrome)
- ChromeDriver (matching your Chrome version)

## Installation

```bash
# Clone repository
git clone https://github.com/1devspace/office-screen.git
cd office-screen

# Install dependencies
pip3 install -r requirements.txt
```

## Quick Start

```bash
# Run with default settings
python3 office_screen.py

# Use different URL sets
python3 office_screen.py --urls config/urls/urls-business.json
python3 office_screen.py --urls config/urls/urls-software.json
python3 office_screen.py --list-urls

# Custom configuration
python3 office_screen.py --config config/my-config.json
```

## Configuration

### Application Config (`config/config.json`)

```json
{
  "interval": 90,
  "adaptive_interval": true,
  "min_interval": 30,
  "max_interval": 180,
  "max_retries": 3,
  "max_browser_restarts": 5,
  "proxies": [],
  "user_agents": []
}
```

### URL Files (`config/urls/`)

Available URL files:
- `urls.json` (default)
- `urls-business.json` - Business, finance, productivity
- `urls-software.json` - Developer resources, tech news
- `urls-tech.json` - Technology, AI, cloud, security
- `urls-design.json` - Design inspiration and tools
- `urls-news.json` - General and tech news
- `urls-gaming.json` - Gaming news and platforms

Create custom URL files by copying and editing existing ones.

## Usage Examples

### Command Line

```bash
python3 office_screen.py --help
python3 office_screen.py --urls config/urls/urls-business.json
python3 office_screen.py --config config/my-config.json --urls config/urls/my-urls.json
```

### Programmatic

```python
from office_screen import OfficeScreen

# Basic usage
office = OfficeScreen()
office.run()

# Custom configuration
office = OfficeScreen(
    config_file="config/config.json",
    urls_file="config/urls/urls-business.json"
)
office.run()
```

## Project Structure

```
office-screen/
├── office_screen.py          # Main application
├── config/                   # Configuration files
│   ├── config.json
│   └── urls/                 # URL files
├── examples/                 # Usage examples
└── docs/                     # Documentation
```

## Monitoring

Logs are saved to `logs/` directory:
- `logs/office-screen.log` - Main log file
- `logs/performance_metrics.json` - Performance analytics

## Troubleshooting

**ChromeDriver not found:** Install ChromeDriver matching your Chrome version  
**Memory issues:** Reduce `max_memory_usage` in config  
**High failure rate:** Increase `interval` or add proxies  
**Browser crashes:** Check system resources and update Chrome

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This tool is for educational and legitimate automation purposes only. Users are responsible for complying with website terms of service and applicable laws.
