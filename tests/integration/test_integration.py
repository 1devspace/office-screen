"""Integration tests for PiPages class."""

import pytest
import json
import tempfile
import os
from pi_pages import PiPages


class TestPiPagesIntegration:
    """Integration test cases for PiPages class."""

    def test_full_configuration_loading(self):
        """Test complete configuration loading from files."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
            config_data = {
                'interval': 60,
                'adaptive_interval': False,
                'min_interval': 30,
                'max_interval': 120,
                'max_retries': 2,
                'max_browser_restarts': 3,
                'memory_check_interval': 200,
                'max_memory_usage': 70,
                'proxies': ['http://proxy1.com', 'http://proxy2.com'],
                'user_agents': [
                    'Mozilla/5.0 (Test Browser)',
                    'Mozilla/5.0 (Another Browser)'
                ]
            }
            json.dump(config_data, config_f)
            config_file = config_f.name

        # Create temporary URLs file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as urls_f:
            urls_data = {
                'urls': [
                    {
                        'category': 'Integration Test',
                        'urls': [
                            'https://httpbin.org/get',
                            'https://httpbin.org/status/200'
                        ]
                    }
                ]
            }
            json.dump(urls_data, urls_f)
            urls_file = urls_f.name

        try:
            # Test PiPages initialization with custom files
            pi_pages = PiPages(config_file)
            
            # Verify configuration was loaded correctly
            assert pi_pages.interval == 60
            assert pi_pages.adaptive_interval is False
            assert pi_pages.min_interval == 30
            assert pi_pages.max_interval == 120
            assert pi_pages.max_retries == 2
            assert pi_pages.max_browser_restarts == 3
            assert pi_pages.memory_check_interval == 200
            assert pi_pages.max_memory_usage == 70
            assert len(pi_pages.proxies) == 2
            assert len(pi_pages.config.get('user_agents', [])) == 2

            # Test URL loading
            urls = pi_pages.load_urls(urls_file)
            assert len(urls) == 2
            assert 'https://httpbin.org/get' in urls
            assert 'https://httpbin.org/status/200' in urls

        finally:
            # Clean up temporary files
            os.unlink(config_file)
            os.unlink(urls_file)

    def test_url_validation_with_real_urls(self):
        """Test URL validation with real HTTP URLs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {'interval': 90}
            json.dump(config_data, f)
            config_file = f.name

        try:
            pi_pages = PiPages(config_file)
            
            # Test with real URLs
            assert pi_pages.validate_url('https://httpbin.org/get') is True
            assert pi_pages.validate_url('https://httpbin.org/status/200') is True
            assert pi_pages.validate_url('https://httpbin.org/status/404') is True
            
            # Test with invalid URLs
            assert pi_pages.validate_url('not-a-valid-url') is False
            assert pi_pages.validate_url('ftp://example.com') is False
            assert pi_pages.validate_url('') is False

        finally:
            os.unlink(config_file)

    def test_category_filtering(self):
        """Test URL filtering by category."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            urls_data = {
                'urls': [
                    {
                        'category': 'Tech News',
                        'urls': [
                            'https://techcrunch.com',
                            'https://theverge.com'
                        ]
                    },
                    {
                        'category': 'Developer Tools',
                        'urls': [
                            'https://github.com',
                            'https://stackoverflow.com'
                        ]
                    }
                ]
            }
            json.dump(urls_data, f)
            urls_file = f.name

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
                config_data = {'interval': 90}
                json.dump(config_data, config_f)
                config_file = config_f.name

            try:
                pi_pages = PiPages(config_file)
                
                # Test filtering by category
                tech_urls = pi_pages.get_urls_by_category('Tech News')
                assert len(tech_urls) == 2
                assert 'https://techcrunch.com' in tech_urls
                assert 'https://theverge.com' in tech_urls

                dev_urls = pi_pages.get_urls_by_category('Developer Tools')
                assert len(dev_urls) == 2
                assert 'https://github.com' in dev_urls
                assert 'https://stackoverflow.com' in dev_urls

                # Test non-existent category
                empty_urls = pi_pages.get_urls_by_category('Non-existent')
                assert len(empty_urls) == 0

                # Test getting all categories
                categories = pi_pages.get_available_categories()
                assert 'Tech News' in categories
                assert 'Developer Tools' in categories
                assert len(categories) == 2

            finally:
                os.unlink(config_file)

        finally:
            os.unlink(urls_file)

    def test_adaptive_interval_calculation(self):
        """Test adaptive interval calculation with various success rates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                'interval': 90,
                'adaptive_interval': True,
                'min_interval': 30,
                'max_interval': 180
            }
            json.dump(config_data, f)
            config_file = f.name

        try:
            pi_pages = PiPages(config_file)
            
            # Test with low success rate (should increase interval)
            pi_pages.successful_visits = 2
            pi_pages.total_visits = 10  # 20% success rate
            new_interval = pi_pages.adaptive_interval_adjustment()
            assert new_interval > 90
            assert new_interval <= 180

            # Test with high success rate (should decrease interval)
            pi_pages.successful_visits = 18
            pi_pages.total_visits = 20  # 90% success rate
            new_interval = pi_pages.adaptive_interval_adjustment()
            assert new_interval < 90
            assert new_interval >= 30

            # Test with medium success rate (should stay similar)
            pi_pages.successful_visits = 7
            pi_pages.total_visits = 10  # 70% success rate
            new_interval = pi_pages.adaptive_interval_adjustment()
            assert 70 <= new_interval <= 110  # Should be close to original

        finally:
            os.unlink(config_file)


if __name__ == '__main__':
    pytest.main([__file__]) 