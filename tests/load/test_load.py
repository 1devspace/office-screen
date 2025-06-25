"""Load tests for OfficeScreen class."""

import pytest
import json
import tempfile
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from office_screen import OfficeScreen


class TestOfficeScreenLoad:
    """Load test cases for OfficeScreen class."""

    def test_concurrent_config_loading(self):
        """Test concurrent configuration loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {'interval': 90}
            json.dump(config_data, f)
            config_file = f.name

        try:
            def create_office_screen():
                return OfficeScreen(config_file)

            # Test with 10 concurrent threads
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(create_office_screen) for _ in range(10)]
                results = [future.result() for future in as_completed(futures)]

            # Verify all instances were created successfully
            assert len(results) == 10
            for office_screen in results:
                assert office_screen.interval == 90

        finally:
            os.unlink(config_file)

    def test_concurrent_url_validation(self):
        """Test concurrent URL validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {'interval': 90}
            json.dump(config_data, f)
            config_file = f.name

        try:
            office_screen = OfficeScreen(config_file)
            
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
            ] * 10  # Repeat 10 times for more load

            def validate_url(url):
                return office_screen.validate_url(url)

            # Test with 5 concurrent threads
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(validate_url, url) for url in test_urls]
                results = [future.result() for future in as_completed(futures)]

            # Verify all validations completed
            assert len(results) == len(test_urls)
            assert all(isinstance(result, bool) for result in results)

        finally:
            os.unlink(config_file)

    def test_large_url_file_loading(self):
        """Test loading a very large URL file."""
        # Create a large URLs file
        large_urls_data = {
            'urls': []
        }
        
        # Generate 1000 categories with 50 URLs each
        for i in range(1000):
            category = {
                'category': f'Category {i}',
                'urls': [f'https://example{i}-{j}.com' for j in range(50)]
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
                office_screen = OfficeScreen(config_file)
                
                # Load the large URL file
                start_time = time.time()
                urls = office_screen.load_urls(urls_file)
                load_time = time.time() - start_time

                # Verify results
                assert len(urls) == 50000  # 1000 categories * 50 URLs
                assert load_time < 5.0  # Should load in under 5 seconds

            finally:
                os.unlink(config_file)

        finally:
            os.unlink(urls_file)

    def test_concurrent_category_filtering(self):
        """Test concurrent category filtering operations."""
        # Create a URLs file with multiple categories
        urls_data = {
            'urls': []
        }
        
        # Generate 100 categories with 10 URLs each
        for i in range(100):
            category = {
                'category': f'Category {i}',
                'urls': [f'https://example{i}-{j}.com' for j in range(10)]
            }
            urls_data['urls'].append(category)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(urls_data, f)
            urls_file = f.name

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
                config_data = {'interval': 90}
                json.dump(config_data, config_f)
                config_file = config_f.name

            try:
                office_screen = OfficeScreen(config_file)

                def filter_category(category_name):
                    return office_screen.get_urls_by_category(category_name)

                # Test with 20 concurrent threads
                with ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [
                        executor.submit(filter_category, f'Category {i}') 
                        for i in range(100)
                    ]
                    results = [future.result() for future in as_completed(futures)]

                # Verify results
                assert len(results) == 100
                for i, urls in enumerate(results):
                    assert len(urls) == 10
                    assert all(f'example{i}-' in url for url in urls)

            finally:
                os.unlink(config_file)

        finally:
            os.unlink(urls_file)

    def test_memory_usage_under_heavy_load(self):
        """Test memory usage under heavy load conditions."""
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

            # Create many OfficeScreen instances
            instances = []
            for i in range(1000):
                office_screen = OfficeScreen(config_file)
                instances.append(office_screen)

            # Get memory usage after creating instances
            memory_after_creation = process.memory_info().rss
            memory_increase = memory_after_creation - initial_memory

            # Perform operations on all instances
            for office_screen in instances:
                office_screen.validate_url('https://example.com')
                office_screen.adaptive_interval_adjustment()

            # Get memory usage after operations
            memory_after_operations = process.memory_info().rss

            # Clean up
            del instances
            gc.collect()

            # Get memory usage after cleanup
            memory_after_cleanup = process.memory_info().rss

            # Assertions
            assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
            assert memory_after_cleanup <= memory_after_creation + (10 * 1024 * 1024)  # Allow 10MB overhead

        finally:
            os.unlink(config_file)

    def test_concurrent_adaptive_interval_calculation(self):
        """Test concurrent adaptive interval calculations."""
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
            office_screen = OfficeScreen(config_file)

            def calculate_interval(success_rate):
                office_screen.successful_visits = success_rate
                office_screen.total_visits = 100
                return office_screen.adaptive_interval_adjustment()

            # Test with 50 concurrent calculations
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(calculate_interval, i) 
                    for i in range(0, 101, 2)  # 0% to 100% in steps of 2
                ]
                results = [future.result() for future in as_completed(futures)]

            # Verify results
            assert len(results) == 51  # 0% to 100% in steps of 2
            assert all(30 <= interval <= 180 for interval in results)

        finally:
            os.unlink(config_file)

    def test_stress_test_url_loading(self):
        """Stress test URL loading with rapid file changes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
            config_data = {'interval': 90}
            json.dump(config_data, config_f)
            config_file = config_f.name

        try:
            office_screen = OfficeScreen(config_file)

            def create_and_load_urls(urls_data):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(urls_data, f)
                    urls_file = f.name

                try:
                    return office_screen.load_urls(urls_file)
                finally:
                    os.unlink(urls_file)

            # Create different URL configurations
            url_configs = []
            for i in range(100):
                urls_data = {
                    'urls': [
                        {
                            'category': f'Stress Category {i}',
                            'urls': [f'https://stress{i}-{j}.com' for j in range(5)]
                        }
                    ]
                }
                url_configs.append(urls_data)

            # Load URLs rapidly
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(create_and_load_urls, config) 
                    for config in url_configs
                ]
                results = [future.result() for future in as_completed(futures)]

            # Verify results
            assert len(results) == 100
            for i, urls in enumerate(results):
                assert len(urls) == 5
                assert all(f'stress{i}-' in url for url in urls)

        finally:
            os.unlink(config_file)


if __name__ == '__main__':
    pytest.main([__file__]) 