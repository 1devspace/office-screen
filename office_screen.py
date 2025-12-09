#!/usr/bin/env python3
"""
office_screen - Advanced Web Automation Tool

A robust, enterprise-grade web automation tool designed for continuous browsing
and monitoring of multiple websites. Built with Python and Selenium, featuring
advanced error handling, self-healing capabilities, and comprehensive monitoring.

Author: office_screen Team
License: MIT
Version: 2.0.0
"""

import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import psutil
import requests
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchWindowException,
    SessionNotCreatedException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options


class OfficeScreen:
    """
    Advanced web automation tool for continuous browsing and monitoring.

    This class provides functionality for automated web browsing with features
    like error handling, stealth mode, performance monitoring, and adaptive
    behavior.

    Attributes:
        driver: Selenium WebDriver instance
        interval: Time to spend on each page (seconds)
        adaptive_interval: Whether to adjust intervals based on success rate
        max_retries: Maximum retry attempts for failed URLs
        max_browser_restarts: Maximum browser restart attempts
        failed_urls: List of URLs that failed during the session
        successful_visits: Count of successful URL visits
        total_visits: Total number of URL visit attempts
        start_time: Session start timestamp
        config: Configuration dictionary
        urls: List of URLs to visit
        logger: Logger instance for logging

    Example:
        >>> from office_screen import OfficeScreen
        >>> office = OfficeScreen()
        >>> office.run()
    """

    def __init__(
        self,
        config_file: str = "config/config.json",
        urls_file: str = "config/urls/urls.json",
    ) -> None:
        """
        Initialize OfficeScreen instance.

        Args:
            config_file: Path to configuration JSON file
            urls_file: Path to URLs JSON file
        """
        self.driver = None
        self.max_retries = 3
        self.browser_restart_count = 0
        self.max_browser_restarts = 5
        self.failed_urls = []
        self.successful_visits = 0
        self.total_visits = 0
        self.start_time = datetime.now()
        self.last_memory_check = time.time()
        self.memory_check_interval = 300  # 5 minutes
        self.max_memory_usage = 80  # percentage
        
        # Set up logging first
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Performance metrics
        self.performance_metrics = {
            'start_time': self.start_time,
            'successful_visits': 0,
            'failed_visits': 0,
            'browser_restarts': 0,
            'avg_load_time': 0,
            'memory_usage': []
        }
        
        # Load URLs from file
        self.urls = self.load_urls(urls_file)
        
        self.interval = self.config.get('interval', 90)  # seconds
        self.adaptive_interval = self.config.get('adaptive_interval', True)
        self.min_interval = self.config.get('min_interval', 30)
        self.max_interval = self.config.get('max_interval', 180)
        
        # Proxy configuration
        self.proxies = self.config.get('proxies', [])
        self.current_proxy_index = 0
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            'interval': 90,
            'adaptive_interval': True,
            'min_interval': 30,
            'max_interval': 180,
            'max_retries': 3,
            'max_browser_restarts': 5,
            'memory_check_interval': 300,
            'max_memory_usage': 80,
            'proxies': [],
            'user_agents': [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
                    self.logger.info(f"Loaded configuration from {config_file}")
            else:
                # Create default config file
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"Created default configuration file: {config_file}")
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON in config file {config_file}: {e}. Using defaults.")
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing {config_file}: {e}. Using defaults.")
        except Exception as e:
            self.logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        return default_config

    def setup_logging(self):
        """Set up logging with rotation"""
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            'logs/office-screen.log', 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_current_proxy(self):
        """Get next proxy from rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    def check_memory_usage(self):
        """Check and log memory usage"""
        try:
            process = psutil.Process()
            memory_percent = process.memory_percent()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            self.performance_metrics['memory_usage'].append({
                'timestamp': datetime.now(),
                'percent': memory_percent,
                'mb': memory_mb
            })
            
            # Keep only last 100 memory readings (efficient slice)
            if len(self.performance_metrics['memory_usage']) > 100:
                self.performance_metrics['memory_usage'] = self.performance_metrics['memory_usage'][-100:]
            
            if memory_percent > self.max_memory_usage:
                self.logger.warning(f"High memory usage: {memory_percent:.1f}% ({memory_mb:.1f}MB)")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking memory: {e}")
            return True

    def adaptive_interval_adjustment(self):
        """Adjust interval based on success rate"""
        if not self.adaptive_interval or self.total_visits == 0:
            return self.interval
        
        success_rate = self.successful_visits / self.total_visits
        
        if success_rate < 0.5:  # Less than 50% success
            new_interval = min(self.interval * 1.5, self.max_interval)
        elif success_rate > 0.9:  # More than 90% success
            new_interval = max(self.interval * 0.8, self.min_interval)
        else:
            new_interval = self.interval
        
        if new_interval != self.interval:
            self.logger.info(f"Adjusting interval from {self.interval}s to {new_interval:.1f}s (success rate: {success_rate:.2f})")
            self.interval = new_interval
        
        return self.interval

    def signal_handler(self, signum, frame):
        """Handle interrupt signals to close browser gracefully"""
        self.logger.info(f"Received signal {signum}. Closing browser...")
        self.save_performance_metrics()
        self.close_browser()
        self.logger.info("Shutdown complete")
        sys.exit(0)

    def save_performance_metrics(self):
        """Save performance metrics to file"""
        try:
            metrics = {
                'session_duration': str(datetime.now() - self.start_time),
                'total_visits': self.total_visits,
                'successful_visits': self.successful_visits,
                'success_rate': self.successful_visits / max(self.total_visits, 1),
                'browser_restarts': self.browser_restart_count,
                'avg_memory_usage': sum(m['percent'] for m in self.performance_metrics['memory_usage']) / max(len(self.performance_metrics['memory_usage']), 1),
                'failed_urls': self.failed_urls
            }
            
            with open('logs/performance_metrics.json', 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            
            self.logger.info("Performance metrics saved")
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")

    def validate_url(self, url):
        """Validate if URL is accessible"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
            
            # Quick check if URL is reachable
            headers = {
                'User-Agent': random.choice(self.config.get('user_agents', ['Mozilla/5.0 (compatible; OfficeScreen/1.0)']))
            }
            response = requests.head(url, timeout=10, allow_redirects=True, headers=headers)
            return response.status_code < 400, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def setup_browser(self):
        """Set up Chrome browser with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Ensure browser opens in full screen/maximized mode
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add random user agent
        user_agent = random.choice(self.config.get('user_agents', [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]))
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # Add proxy if available
        proxy = self.get_current_proxy()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
            self.logger.info(f"Using proxy: {proxy}")
        
        try:
            # Use system Chrome browser (not webdriver-manager)
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Wait a moment for browser to fully initialize
            time.sleep(1)
            
            # Maximize window to fill the entire screen
            try:
                # First, maximize using Selenium's built-in method
                self.driver.maximize_window()
                time.sleep(0.5)  # Give it time to maximize
                
                # Get screen dimensions (available screen space)
                screen_width = self.driver.execute_script("return screen.availWidth;")
                screen_height = self.driver.execute_script("return screen.availHeight;")
                
                # Get current window size and position
                current_size = self.driver.get_window_size()
                current_position = self.driver.get_window_position()
                
                # Set window to fill entire screen
                # Position at (0, 0) to ensure it starts from top-left
                self.driver.set_window_position(0, 0)
                # Set size to match screen dimensions exactly
                self.driver.set_window_size(screen_width, screen_height)
                
                # Verify it worked
                final_size = self.driver.get_window_size()
                final_position = self.driver.get_window_position()
                
                self.logger.info(
                    f"Browser window set to fill screen: {final_size['width']}x{final_size['height']} "
                    f"at position ({final_position['x']}, {final_position['y']})"
                )
                
            except Exception as e:
                self.logger.warning(f"Could not set window to full screen: {e}. Trying fallback method.")
                # Fallback: just maximize
                try:
                    self.driver.maximize_window()
                except Exception as fallback_error:
                    self.logger.error(f"Fallback maximize also failed: {fallback_error}")
            
            self.logger.info("Chrome browser started successfully using system Chrome")
            return True
        except SessionNotCreatedException as e:
            self.logger.error(f"Failed to create browser session: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to start Chrome browser: {e}")
            return False

    def restart_browser(self):
        """Restart the browser if it crashes"""
        if self.browser_restart_count >= self.max_browser_restarts:
            self.logger.error("Maximum browser restart attempts reached. Exiting.")
            return False
            
        self.logger.warning(f"Restarting browser (attempt {self.browser_restart_count + 1}/{self.max_browser_restarts})")
        self.performance_metrics['browser_restarts'] += 1
        self.close_browser()
        time.sleep(5)  # Wait before restarting
        
        if self.setup_browser():
            self.browser_restart_count += 1
            return True
        return False

    def close_browser(self):
        """Close the browser safely"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None

    def is_browser_healthy(self):
        """Check if browser is still responsive"""
        try:
            if not self.driver:
                return False
            # Try to get current URL to test if browser is responsive
            self.driver.current_url
            return True
        except (WebDriverException, NoSuchWindowException):
            return False

    def visit_url(self, url, retry_count=0):
        """Visit a URL in a new tab with retry logic"""
        if retry_count >= self.max_retries:
            self.logger.error(f"Max retries reached for {url}. Skipping.")
            self.failed_urls.append(url)
            return False
            
        start_time = time.time()
        self.total_visits += 1
        
        try:
            # Check memory usage periodically
            if time.time() - self.last_memory_check > self.memory_check_interval:
                if not self.check_memory_usage():
                    self.logger.warning("High memory usage detected, restarting browser")
                    if not self.restart_browser():
                        return False
                self.last_memory_check = time.time()
            
            # Validate URL before visiting
            is_valid, status = self.validate_url(url)
            if not is_valid:
                self.logger.warning(f"URL validation failed for {url}: {status}")
                self.failed_urls.append(url)
                return False
            
            # Check browser health
            if not self.is_browser_healthy():
                self.logger.warning("Browser not healthy, attempting restart")
                if not self.restart_browser():
                    return False
            
            # Open new tab
            self.driver.execute_script("window.open('');")
            
            # Switch to the new tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to URL with timeout
            self.logger.info(f"Visiting: {url}")
            self.driver.set_page_load_timeout(30)
            self.driver.get(url)
            
            # Wait for page to load and check for common error pages
            time.sleep(5)
            
            # Check if page loaded successfully
            current_url = self.driver.current_url
            if "error" in current_url.lower() or "404" in current_url or "not found" in current_url.lower():
                raise Exception("Page returned error status")
            
            # Check for common error indicators in page content
            page_source = self.driver.page_source.lower()
            if any(error_indicator in page_source for error_indicator in ["error", "not found", "404", "unavailable", "maintenance"]):
                self.logger.warning(f"Error indicators found on page: {url}")
            
            # Stay on page for specified interval
            self.logger.info(f"Staying on page for {self.interval} seconds...")
            time.sleep(self.interval)
            
            # Close the tab
            self.driver.close()
            
            # Switch back to first tab
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            # Update metrics
            load_time = time.time() - start_time
            self.successful_visits += 1
            self.performance_metrics['avg_load_time'] = (
                (self.performance_metrics['avg_load_time'] * (self.successful_visits - 1) + load_time) / self.successful_visits
            )
            
            return True
            
        except TimeoutException:
            self.logger.warning(f"Timeout loading {url}, retrying...")
            return self.visit_url(url, retry_count + 1)
        except WebDriverException as e:
            self.logger.error(f"WebDriver error visiting {url}: {e}")
            if "chrome not reachable" in str(e).lower() or "session deleted" in str(e).lower():
                if self.restart_browser():
                    return self.visit_url(url, retry_count + 1)
            return False
        except Exception as e:
            self.logger.error(f"Error visiting {url}: {e}")
            # Try to close tab and continue
            try:
                if self.driver and len(self.driver.window_handles) > 1:
                    self.driver.close()
                    if len(self.driver.window_handles) > 0:
                        self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return False

    def get_working_urls(self):
        """Filter out URLs that consistently fail"""
        working_urls = []
        for url in self.urls:
            if url not in self.failed_urls:
                working_urls.append(url)
        return working_urls

    def run(self):
        """Main loop to cycle through URLs"""
        self.logger.info("Starting office_screen...")
        
        # Set up browser
        if not self.setup_browser():
            self.logger.error("Failed to start browser. Exiting.")
            return
        
        # Wait for browser to fully load
        time.sleep(15)
        
        cycle_count = 0
        try:
            # Main loop
            while True:
                cycle_count += 1
                working_urls = self.get_working_urls()
                
                if not working_urls:
                    self.logger.error("No working URLs remaining. Exiting.")
                    break
                
                self.logger.info(f"Starting cycle {cycle_count} with {len(working_urls)} URLs...")
                
                # Shuffle URLs to avoid predictable patterns
                random.shuffle(working_urls)
                
                # Visit each URL
                for url in working_urls:
                    if not self.visit_url(url):
                        self.logger.warning(f"Failed to visit {url}")
                    
                    # Add small random delay between URLs
                    time.sleep(random.uniform(1, 3))
                    
                    # Adjust interval based on performance
                    self.adaptive_interval_adjustment()
                    
                self.logger.info(f"Completed cycle {cycle_count}")
                
                # Report failed URLs
                if self.failed_urls:
                    self.logger.warning(f"Failed URLs in this session: {self.failed_urls}")
                
                # Save metrics periodically
                if cycle_count % 5 == 0:
                    self.save_performance_metrics()
                
                # Reset failed URLs for next cycle
                self.failed_urls = []
                
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.save_performance_metrics()
            self.close_browser()

    def load_urls(self, urls_file="config/urls/urls.json"):
        """Load URLs from JSON file"""
        try:
            if os.path.exists(urls_file):
                with open(urls_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Store categorized URLs for potential filtering
                    self.categorized_urls = data.get('urls', [])
                    # Flatten all URLs from all categories using list comprehension for efficiency
                    all_urls = [
                        url for category in data.get('urls', [])
                        for url in category.get('urls', [])
                    ]
                    self.logger.info(f"Loaded {len(all_urls)} URLs from {urls_file}")
                    return all_urls
            else:
                self.logger.warning(f"URLs file {urls_file} not found, using default URLs")
                return self.get_default_urls()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {urls_file}: {e}. Using default URLs.")
            return self.get_default_urls()
        except Exception as e:
            self.logger.error(f"Failed to load URLs from {urls_file}: {e}. Using default URLs.")
            return self.get_default_urls()

    def get_default_urls(self):
        """Get default URLs as fallback"""
        return [
            "https://news.ycombinator.com/",
            "https://github.com/trending",
            "https://tldr.tech/",
            "https://www.theverge.com/",
            "https://techcrunch.com/"
        ]

    def get_urls_by_category(self, category_name=None):
        """Get URLs filtered by category"""
        if not hasattr(self, 'categorized_urls'):
            return self.urls
        
        if category_name:
            for category in self.categorized_urls:
                if category.get('category', '').lower() == category_name.lower():
                    return category.get('urls', [])
            return []
        else:
            return self.categorized_urls

    def get_available_categories(self):
        """Get list of available categories"""
        if hasattr(self, 'categorized_urls'):
            return [cat.get('category', '') for cat in self.categorized_urls]
        return []

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='office_screen - Advanced Web Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python office_screen.py                                    # Use default config/urls/urls.json
  python office_screen.py --urls config/urls/urls-business.json  # Use business URLs
  python office_screen.py --urls config/urls/urls-software.json # Use software URLs
  python office_screen.py --urls config/urls/urls-tech.json      # Use tech URLs
  python office_screen.py --urls config/urls/urls-design.json    # Use design URLs
  python office_screen.py --urls config/urls/urls-news.json      # Use news URLs
  python office_screen.py --urls config/urls/urls-gaming.json   # Use gaming URLs
  python office_screen.py --list-urls                            # List available URL files

Available URL files:
  - config/urls/urls.json (default)
  - config/urls/urls-business.json
  - config/urls/urls-software.json
  - config/urls/urls-tech.json
  - config/urls/urls-design.json
  - config/urls/urls-news.json
  - config/urls/urls-gaming.json
        """
    )
    
    parser.add_argument(
        '--urls', '-u',
        type=str,
        default='config/urls/urls.json',
        help='Path to URLs JSON file (default: config/urls/urls.json)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.json',
        help='Path to configuration JSON file (default: config/config.json)'
    )
    
    parser.add_argument(
        '--list-urls', '-l',
        action='store_true',
        help='List all available URL configuration files'
    )
    
    args = parser.parse_args()
    
    # List available URL files
    if args.list_urls:
            url_files = [
                'config/urls/urls.json',
                'config/urls/urls-business.json',
                'config/urls/urls-software.json',
                'config/urls/urls-tech.json',
                'config/urls/urls-design.json',
                'config/urls/urls-news.json',
                'config/urls/urls-gaming.json'
            ]
            print("\n📋 Available URL Configuration Files:")
            print("=" * 50)
            for url_file in url_files:
                exists = "✓" if os.path.exists(url_file) else "✗"
                print(f"  {exists} {url_file}")
            print("\n💡 Usage: python office_screen.py --urls <filename>")
            return
    
    try:
        office_screen = OfficeScreen(config_file=args.config, urls_file=args.urls)
        office_screen.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutdown requested by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 