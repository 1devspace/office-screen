"""Unit tests for OfficeScreen class."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from office_screen import OfficeScreen


class TestOfficeScreen:
    """Test cases for OfficeScreen class."""

    def test_init_with_default_config(self):
        """Test OfficeScreen initialization with default config."""
        with patch('office_screen.OfficeScreen.load_config') as mock_load_config:
            mock_load_config.return_value = {
                'interval': 90,
                'adaptive_interval': True,
                'min_interval': 30,
                'max_interval': 180,
                'max_retries': 3,
                'max_browser_restarts': 5,
                'memory_check_interval': 300,
                'max_memory_usage': 80,
                'proxies': [],
                'user_agents': []
            }
            
            with patch('office_screen.OfficeScreen.load_urls') as mock_load_urls:
                mock_load_urls.return_value = []
                
                with patch('office_screen.OfficeScreen.setup_logging'):
                    office_screen = OfficeScreen()
                    
                    assert office_screen.interval == 90
                    assert office_screen.adaptive_interval is True
                    assert office_screen.min_interval == 30
                    assert office_screen.max_interval == 180
                    assert office_screen.max_retries == 3
                    assert office_screen.max_browser_restarts == 5

    def test_load_config_from_file(self):
        """Test loading configuration from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                'interval': 120,
                'adaptive_interval': False,
                'min_interval': 60,
                'max_interval': 300
            }
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            with patch('office_screen.OfficeScreen.setup_logging'):
                with patch('office_screen.OfficeScreen.load_urls') as mock_load_urls:
                    mock_load_urls.return_value = []
                    
                    office_screen = OfficeScreen(config_file)
                    
                    assert office_screen.interval == 120
                    assert office_screen.adaptive_interval is False
                    assert office_screen.min_interval == 60
                    assert office_screen.max_interval == 300
        finally:
            os.unlink(config_file)

    def test_load_urls_from_file(self):
        """Test loading URLs from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            urls_data = {
                'urls': [
                    {
                        'category': 'Test Category',
                        'urls': ['https://example.com', 'https://test.com']
                    }
                ]
            }
            json.dump(urls_data, f)
            urls_file = f.name
        
        try:
            with patch('office_screen.PiPages.setup_logging'):
                with patch('office_screen.PiPages.load_config') as mock_load_config:
                    mock_load_config.return_value = {}
                    
                    pi_pages = PiPages()
                    urls = pi_pages.load_urls(urls_file)
                    
                    assert len(urls) == 2
                    assert 'https://example.com' in urls
                    assert 'https://test.com' in urls
        finally:
            os.unlink(urls_file)

    def test_validate_url(self):
        """Test URL validation."""
        with patch('office_screen.PiPages.setup_logging'):
            with patch('office_screen.PiPages.load_config') as mock_load_config:
                mock_load_config.return_value = {}
                
                with patch('office_screen.PiPages.load_urls') as mock_load_urls:
                    mock_load_urls.return_value = []
                    
                    pi_pages = PiPages()
                    
                    # Valid URLs
                    assert pi_pages.validate_url('https://example.com') is True
                    assert pi_pages.validate_url('http://test.com') is True
                    
                    # Invalid URLs
                    assert pi_pages.validate_url('not-a-url') is False
                    assert pi_pages.validate_url('ftp://example.com') is False

    def test_adaptive_interval_adjustment(self):
        """Test adaptive interval adjustment based on success rate."""
        with patch('office_screen.PiPages.setup_logging'):
            with patch('office_screen.PiPages.load_config') as mock_load_config:
                mock_load_config.return_value = {
                    'adaptive_interval': True,
                    'min_interval': 30,
                    'max_interval': 180
                }
                
                with patch('office_screen.PiPages.load_urls') as mock_load_urls:
                    mock_load_urls.return_value = []
                    
                    pi_pages = PiPages()
                    pi_pages.interval = 90
                    pi_pages.successful_visits = 5
                    pi_pages.total_visits = 10  # 50% success rate
                    
                    new_interval = pi_pages.adaptive_interval_adjustment()
                    
                    # Should increase interval for low success rate
                    assert new_interval > 90
                    assert new_interval <= 180

    def test_get_urls_by_category(self):
        """Test filtering URLs by category."""
        with patch('office_screen.PiPages.setup_logging'):
            with patch('office_screen.PiPages.load_config') as mock_load_config:
                mock_load_config.return_value = {}
                
                with patch('office_screen.PiPages.load_urls') as mock_load_urls:
                    mock_load_urls.return_value = [
                        {'category': 'Tech', 'urls': ['https://tech1.com', 'https://tech2.com']},
                        {'category': 'News', 'urls': ['https://news1.com']}
                    ]
                    
                    pi_pages = PiPages()
                    
                    tech_urls = pi_pages.get_urls_by_category('Tech')
                    assert len(tech_urls) == 2
                    assert 'https://tech1.com' in tech_urls
                    assert 'https://tech2.com' in tech_urls

    def test_get_available_categories(self):
        """Test getting available categories."""
        with patch('office_screen.PiPages.setup_logging'):
            with patch('office_screen.PiPages.load_config') as mock_load_config:
                mock_load_config.return_value = {}
                
                with patch('office_screen.PiPages.load_urls') as mock_load_urls:
                    mock_load_urls.return_value = [
                        {'category': 'Tech', 'urls': []},
                        {'category': 'News', 'urls': []}
                    ]
                    
                    pi_pages = PiPages()
                    
                    categories = pi_pages.get_available_categories()
                    assert 'Tech' in categories
                    assert 'News' in categories
                    assert len(categories) == 2


if __name__ == '__main__':
    pytest.main([__file__]) 