"""Performance tests for PiPages class."""

import pytest
import time
import json
import tempfile
import os
from pi_pages import PiPages


class TestPiPagesPerformance:
    """Performance test cases for PiPages class."""

    def test_config_loading_performance(self, benchmark):
        """Benchmark configuration loading performance."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                'interval': 90,
                'adaptive_interval': True,
                'min_interval': 30,
                'max_interval': 180,
                'max_retries': 3,
                'max_browser_restarts': 5,
                'memory_check_interval': 300,
                'max_memory_usage': 80,
                'proxies': ['http://proxy1.com', 'http://proxy2.com'],
                'user_agents': [
                    'Mozilla/5.0 (Test Browser)',
                    'Mozilla/5.0 (Another Browser)'
                ]
            }
            json.dump(config_data, f)
            config_file = f.name

        try:
            def load_config():
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_f:
                    json.dump(config_data, temp_f)
                    temp_config = temp_f.name
                
                try:
                    pi_pages = PiPages(temp_config)
                    return pi_pages
                finally:
                    os.unlink(temp_config)

            # Benchmark the configuration loading
            result = benchmark(load_config)
            assert result is not None

        finally:
            os.unlink(config_file)

    def test_url_validation_performance(self, benchmark):
        """Benchmark URL validation performance."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {'interval': 90}
            json.dump(config_data, f)
            config_file = f.name

        try:
            pi_pages = PiPages(config_file)
            
            test_urls = [
                'https://example.com',
                'https://test.com',
                'https://httpbin.org/get',
                'https://httpbin.org/status/200',
                'https://httpbin.org/status/404',
                'not-a-valid-url',
                'ftp://example.com',
                'https://github.com',
                'https://stackoverflow.com',
                'https://techcrunch.com'
            ]

            def validate_urls():
                return [pi_pages.validate_url(url) for url in test_urls]

            # Benchmark URL validation
            results = benchmark(validate_urls)
            assert len(results) == len(test_urls)
            assert all(isinstance(result, bool) for result in results)

        finally:
            os.unlink(config_file)

    def test_url_loading_performance(self, benchmark):
        """Benchmark URL loading performance."""
        # Create a large URLs file for testing
        large_urls_data = {
            'urls': []
        }
        
        # Generate 100 categories with 10 URLs each
        for i in range(100):
            category = {
                'category': f'Category {i}',
                'urls': [f'https://example{i}-{j}.com' for j in range(10)]
            }
            large_urls_data['urls'].append(category)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_urls_data, f)
            urls_file = f.name

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
                config_data = {'interval': 90}
                json.dump(config_data, config_f)
                config_file = config_f.name

            try:
                pi_pages = PiPages(config_file)

                def load_urls():
                    return pi_pages.load_urls(urls_file)

                # Benchmark URL loading
                urls = benchmark(load_urls)
                assert len(urls) == 1000  # 100 categories * 10 URLs

            finally:
                os.unlink(config_file)

        finally:
            os.unlink(urls_file)

    def test_category_filtering_performance(self, benchmark):
        """Benchmark category filtering performance."""
        # Create a large URLs file
        large_urls_data = {
            'urls': []
        }
        
        # Generate 50 categories with 20 URLs each
        for i in range(50):
            category = {
                'category': f'Category {i}',
                'urls': [f'https://example{i}-{j}.com' for j in range(20)]
            }
            large_urls_data['urls'].append(category)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_urls_data, f)
            urls_file = f.name

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
                config_data = {'interval': 90}
                json.dump(config_data, config_f)
                config_file = config_f.name

            try:
                pi_pages = PiPages(config_file)

                def filter_categories():
                    results = []
                    for i in range(50):
                        urls = pi_pages.get_urls_by_category(f'Category {i}')
                        results.append(len(urls))
                    return results

                # Benchmark category filtering
                results = benchmark(filter_categories)
                assert len(results) == 50
                assert all(result == 20 for result in results)

            finally:
                os.unlink(config_file)

        finally:
            os.unlink(urls_file)

    def test_adaptive_interval_performance(self, benchmark):
        """Benchmark adaptive interval calculation performance."""
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

            def calculate_adaptive_intervals():
                results = []
                for success_rate in range(0, 101, 10):
                    pi_pages.successful_visits = success_rate
                    pi_pages.total_visits = 100
                    interval = pi_pages.adaptive_interval_adjustment()
                    results.append(interval)
                return results

            # Benchmark adaptive interval calculation
            results = benchmark(calculate_adaptive_intervals)
            assert len(results) == 11  # 0% to 100% in steps of 10
            assert all(30 <= interval <= 180 for interval in results)

        finally:
            os.unlink(config_file)

    def test_memory_usage_under_load(self):
        """Test memory usage under load conditions."""
        import psutil
        import gc

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {'interval': 90}
            json.dump(config_data, f)
            config_file = f.name

        try:
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss

            # Create multiple PiPages instances
            instances = []
            for i in range(100):
                pi_pages = PiPages(config_file)
                instances.append(pi_pages)

            # Get memory usage after creating instances
            memory_after_creation = process.memory_info().rss
            memory_increase = memory_after_creation - initial_memory

            # Clean up
            del instances
            gc.collect()

            # Get memory usage after cleanup
            memory_after_cleanup = process.memory_info().rss

            # Assertions
            assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
            assert memory_after_cleanup <= memory_after_creation

        finally:
            os.unlink(config_file)


if __name__ == '__main__':
    pytest.main([__file__]) 