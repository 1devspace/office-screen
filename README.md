[![CI](https://github.com/1devspace/office-screen/actions/workflows/ci.yml/badge.svg)](https://github.com/1devspace/office-screen/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://1devspace.github.io/office-screen/)
[![License](https://img.shields.io/github/license/1devspace/office-screen)](LICENSE)

[📚 **View Full Documentation**](https://1devspace.github.io/office-screen/)

# Pi-Pages: Advanced Web Automation Tool

A robust, enterprise-grade web automation tool designed for continuous browsing and monitoring of multiple websites. Built with Python and Selenium, featuring advanced error handling, self-healing capabilities, and comprehensive monitoring.

## 🚀 Features

### Core Functionality
- **Multi-site browsing**: Automatically cycles through a configurable list of URLs
- **Tab management**: Opens each URL in a new tab and closes it after viewing
- **Infinite looping**: Continuously cycles through all URLs
- **Configurable intervals**: Adjustable time spent on each page (30-180 seconds)

### Advanced Error Handling & Self-Healing
- **URL validation**: Pre-validates URLs before visiting
- **Browser crash recovery**: Automatically restarts browser up to 5 times
- **Retry logic**: Retries failed visits up to 3 times with different strategies
- **Graceful degradation**: Continues running even if some URLs fail
- **Memory management**: Monitors memory usage and restarts browser if needed

### Anti-Detection & Stealth
- **User agent rotation**: Randomly selects from multiple user agents
- **Proxy support**: Configurable proxy rotation
- **Random delays**: Unpredictable timing between actions
- **URL shuffling**: Randomizes URL order to avoid patterns
- **Browser fingerprinting evasion**: Disables automation indicators

### Performance & Monitoring
- **Real-time metrics**: Tracks success rates, load times, and performance
- **Adaptive intervals**: Automatically adjusts timing based on success rate
- **Memory monitoring**: Tracks memory usage and prevents leaks
- **Comprehensive logging**: Rotating log files with detailed activity tracking
- **Performance analytics**: Saves metrics to JSON for analysis

### Enterprise Features
- **Configuration management**: JSON-based configuration without code changes
- **Log rotation**: Automatic log file management (10MB max, 5 backups)
- **Signal handling**: Graceful shutdown with Ctrl+C
- **Resource management**: Efficient memory and process handling
- **Production ready**: Suitable for 24/7 operation

## 📋 Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)

## 🛠️ Installation

### Option 1: Direct Installation
1. **Clone the repository:**
```bash
git clone <repository-url>
cd pi-pages
```

2. **Install Python dependencies:**
```bash
pip3 install -r requirements.txt
```

3. **Install ChromeDriver (if not already installed):**

**macOS (with Homebrew):**
```bash
brew install chromedriver
```

**Ubuntu/Debian:**
```bash
sudo apt-get install chromium-chromedriver
```

**Windows:**
Download from [ChromeDriver website](https://chromedriver.chromium.org/)

### Option 2: Package Installation
```bash
pip3 install .
```

This will install pi-pages as a system command and make it available globally.

## ⚙️ Configuration

The tool uses JSON configuration files for easy customization:

### URLs Configuration (`urls.json`)

The application loads URLs from `urls.json` file, organized by categories:

```json
{
  "urls": [
    {
      "category": "Tech News & Updates",
      "urls": [
        "https://www.theverge.com/",
        "https://techcrunch.com/",
        "https://www.wired.com/"
      ]
    },
    {
      "category": "Developer Resources",
      "urls": [
        "https://github.com/trending",
        "https://stackoverflow.com/",
        "https://dev.to/"
      ]
    }
  ]
}
```

### Application Configuration (`config.json`)

```json
{
  "interval": 90,
  "adaptive_interval": true,
  "min_interval": 30,
  "max_interval": 180,
  "max_retries": 3,
  "max_browser_restarts": 5,
  "memory_check_interval": 300,
  "max_memory_usage": 80,
  "proxies": [],
  "user_agents": [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  ]
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `interval` | int | 90 | Time (seconds) to stay on each page |
| `adaptive_interval` | bool | true | Enable automatic interval adjustment |
| `min_interval` | int | 30 | Minimum interval when adaptive mode is on |
| `max_interval` | int | 180 | Maximum interval when adaptive mode is on |
| `max_retries` | int | 3 | Maximum retry attempts for failed URLs |
| `max_browser_restarts` | int | 5 | Maximum browser restart attempts |
| `memory_check_interval` | int | 300 | Memory check frequency (seconds) |
| `max_memory_usage` | int | 80 | Maximum memory usage percentage |
| `proxies` | array | [] | List of proxy servers for rotation |
| `user_agents` | array | [] | List of user agents for rotation |

## 📋 URL Categories

The application includes URLs organized into the following categories:

- **Tech News & Updates**: Latest technology news and updates
- **Developer Resources**: Development tools, documentation, and resources  
- **Tunisia & Regional Tech Resources**: Local and regional tech ecosystem
- **AI/ML Resources**: Artificial intelligence and machine learning resources
- **Healthcare Tech**: Healthcare technology news and resources
- **Team Productivity**: Project management and productivity tools
- **Market & Finance**: Financial markets, crypto, and economic data
- **Sports**: Live sports scores and updates
- **Weather & Time**: Weather forecasts and time zone information
- **Social Trends**: Trending topics and social media trends

## 🔧 Customization

### Adding New URLs

1. Edit `urls.json` to add new URLs in appropriate categories
2. Restart the application to load new URLs

### Creating Custom URL Sets

You can create multiple URL files for different purposes:

```bash
# Create a development-focused URL set
cp urls.json dev-urls.json
# Edit dev-urls.json to include only development resources

# Run with custom URL set
python pi-pages.py --urls dev-urls.json
```

### Filtering by Category

The application provides methods to filter URLs by category:

```python
# Get all URLs from a specific category
tech_urls = office_screen.get_urls_by_category("Tech News & Updates")

# Get all available categories
categories = office_screen.get_available_categories()
```

## 🚀 Usage

### Basic Usage
```bash
python3 pi-pages.py
```

### Direct Execution (if made executable)
```bash
./pi-pages.py
```

### Package Installation Usage
```bash
# After installing with pip install .
pi-pages
```

### With Custom Configuration
```bash
python3 pi-pages.py config.json
```

### Running in Background
```bash
nohup python3 pi-pages.py > output.log 2>&1 &
```

### Stopping the Script
- Press `Ctrl+C` for graceful shutdown
- The script will save metrics and close the browser properly

## 📊 Monitoring & Logs

### Log Files
- **`logs/pi-pages.log`**: Main log file with rotating backup
- **`logs/performance_metrics.json`**: Performance analytics data

### Performance Metrics
The tool tracks and saves:
- Session duration
- Total visits vs successful visits
- Success rate percentage
- Browser restart count
- Average memory usage
- Failed URLs list
- Average load times

### Example Log Output
```
2024-01-15 10:30:00 - INFO - Starting pi-pages...
2024-01-15 10:30:15 - INFO - Chrome browser started successfully
2024-01-15 10:30:15 - INFO - Starting cycle 1 with 18 URLs...
2024-01-15 10:30:15 - INFO - Visiting: https://example.com
2024-01-15 10:30:20 - INFO - Staying on page for 90 seconds...
2024-01-15 10:31:50 - INFO - Completed cycle 1
```

## 🔧 Troubleshooting

### Common Issues

**1. ChromeDriver not found:**
```bash
# Install ChromeDriver
brew install chromedriver  # macOS
sudo apt-get install chromium-chromedriver  # Ubuntu
```

**2. Memory issues:**
- Reduce `max_memory_usage` in config
- Increase `memory_check_interval`
- Restart the script periodically

**3. High failure rate:**
- Increase `interval` to reduce server load
- Add proxies to avoid rate limiting
- Check URL accessibility manually

**4. Browser crashes:**
- Increase `max_browser_restarts`
- Check system resources
- Update Chrome browser

### Debug Mode
Enable verbose logging by modifying the logging level in the script:
```python
self.logger.setLevel(logging.DEBUG)
```

## 📁 Project Structure

```
pi-pages/
├── pi-pages.py                 # Main Python script (executable)
├── config.json                 # Configuration file
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation script
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history
├── README.md                   # This file
└── logs/                       # Log directory (created automatically)
    ├── pi-pages.log           # Main log file
    ├── pi-pages.log.1         # Backup log files
    └── performance_metrics.json  # Performance data
```

## 🔄 Adaptive Behavior

The tool automatically adjusts its behavior based on performance:

- **Success Rate < 50%**: Increases interval by 50%
- **Success Rate > 90%**: Decreases interval by 20%
- **High Memory Usage**: Restarts browser automatically
- **Failed URLs**: Tracks and reports problematic URLs

## 🛡️ Security & Privacy

- **No data collection**: Tool doesn't send data anywhere
- **Local operation**: All processing happens locally
- **Configurable privacy**: Adjust user agents and proxies
- **Secure shutdown**: Cleans up resources properly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool is for educational and legitimate automation purposes only. Users are responsible for complying with website terms of service and applicable laws. The authors are not responsible for any misuse of this software.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/pi-pages.log`
3. Open an issue on GitHub with detailed information

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing, code style, and pull requests.

## License

This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.

---

**Version**: 2.0  
**Last Updated**: January 2024  
**Python Version**: 3.7+  
**Status**: Production Ready