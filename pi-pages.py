#!/usr/bin/env python3

import time
import signal
import sys
import logging
import requests
import random
import json
import os
import psutil
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchWindowException,
    SessionNotCreatedException, NoSuchElementException
)

class PiPages:
    def __init__(self, config_file="config.json"):
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
        
        self.urls = self.config.get('urls', [
            "https://wise.com/us/currency-converter/usd-to-tnd-rate",
            "https://www.mortgagenewsdaily.com/mortgage-rates/mnd",
            "https://www.forbes.com/advisor/mortgages/mortgage-rates/",
            "https://finance.yahoo.com/most-active/",
            "https://finance.yahoo.com/quote/CNC/",
            "https://www.coindesk.com/price/bitcoin/",
            "https://www.livesport.com/soccer/world/",
            "https://live-tennis.eu/en/atp-live-scores",
            "https://forecast.weather.gov/MapClick.php?CityName=Las+Vegas&state=NV&site=VEF&textField1=36.175&textField2=-115.136&e=0",
            "https://www.weatherbug.com/weather-forecast/10-day-weather/tabarka-jundubah-ts",
            "https://tldr.tech/",
            "https://news.ycombinator.com/",
            "https://gov.nv.gov/Newsroom/PRs/news-releases/",
            "https://cityofnorthlasvegas.org/newslist.php",
            "https://www.lasvegasnevada.gov/Residents/Events#/",
            "https://www.cityofnorthlasvegas.com/things-to-do/events-calendar",
            "https://github.com/trending",
            "https://trends24.in/united-states/"
        ])
        
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
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                    self.logger.info(f"Loaded configuration from {config_file}")
            else:
                # Create default config file
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                    self.logger.info(f"Created default configuration file: {config_file}")
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
            'logs/pi-pages.log', 
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
            
            # Keep only last 100 memory readings
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
                'User-Agent': random.choice(self.config.get('user_agents', ['Mozilla/5.0 (compatible; PiPages/1.0)']))
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
        chrome_options.add_argument("--window-size=1920,1080")
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
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("Chrome browser started successfully")
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
        self.logger.info("Starting pi-pages...")
        
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

def main():
    """Main entry point"""
    try:
        pi_pages = PiPages()
        pi_pages.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 