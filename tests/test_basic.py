"""Basic tests for OfficeScreen class."""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from office_screen import OfficeScreen


class TestOfficeScreenBasic:
    """Basic test cases for OfficeScreen class."""

    def test_init_with_default_config(self):
        """Test OfficeScreen initialization with default config."""
        with patch(
            "office_screen.OfficeScreen.load_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "interval": 90,
                "adaptive_interval": True,
                "min_interval": 30,
                "max_interval": 180,
                "max_retries": 3,
                "max_browser_restarts": 5,
                "memory_check_interval": 300,
                "max_memory_usage": 80,
                "proxies": [],
                "user_agents": [],
            }

            with patch(
                "office_screen.OfficeScreen.load_urls"
            ) as mock_load_urls:
                mock_load_urls.return_value = []

                # Create a mock logger
                mock_logger = MagicMock()
                
                def setup_logging_side_effect(self):
                    """Side effect that sets logger attribute."""
                    self.logger = mock_logger
                
                with patch(
                    "office_screen.OfficeScreen.setup_logging",
                    side_effect=setup_logging_side_effect,
                    autospec=False,
                ):
                    office_screen = OfficeScreen()

                    assert office_screen.interval == 90
                    assert office_screen.adaptive_interval is True
                    assert office_screen.max_retries == 3

    def test_load_config_from_file(self):
        """Test loading configuration from JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            config_data = {
                "interval": 120,
                "adaptive_interval": False,
                "min_interval": 60,
                "max_interval": 300,
            }
            json.dump(config_data, f)
            config_file = f.name

        try:
            # Create a mock logger
            mock_logger = MagicMock()
            
            def setup_logging_side_effect(self):
                """Side effect that sets logger attribute."""
                self.logger = mock_logger
            
            with patch(
                "office_screen.OfficeScreen.setup_logging",
                side_effect=setup_logging_side_effect,
                autospec=False,
            ):
                with patch(
                    "office_screen.OfficeScreen.load_urls"
                ) as mock_load_urls:
                    mock_load_urls.return_value = []

                    office_screen = OfficeScreen(config_file)

                    assert office_screen.interval == 120
                    assert office_screen.adaptive_interval is False
        finally:
            os.unlink(config_file)

    def test_load_urls_from_file(self):
        """Test loading URLs from JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            urls_data = {
                "urls": [
                    {
                        "category": "Test Category",
                        "urls": ["https://example.com", "https://test.com"],
                    }
                ]
            }
            json.dump(urls_data, f)
            urls_file = f.name

        try:
            # Create a mock logger
            mock_logger = MagicMock()
            
            def setup_logging_side_effect(self):
                """Side effect that sets logger attribute."""
                self.logger = mock_logger
            
            with patch(
                "office_screen.OfficeScreen.setup_logging",
                side_effect=setup_logging_side_effect,
                autospec=False,
            ):
                with patch(
                    "office_screen.OfficeScreen.load_config"
                ) as mock_load_config:
                    mock_load_config.return_value = {}

                    office_screen = OfficeScreen()
                    urls = office_screen.load_urls(urls_file)

                    assert len(urls) == 2
                    assert "https://example.com" in urls
                    assert "https://test.com" in urls
        finally:
            os.unlink(urls_file)

    def test_validate_url(self):
        """Test URL validation."""
        # Create a mock logger
        mock_logger = MagicMock()
        
        def setup_logging_side_effect(self):
            """Side effect that sets logger attribute."""
            self.logger = mock_logger
        
        with patch(
            "office_screen.OfficeScreen.setup_logging",
            side_effect=setup_logging_side_effect,
            autospec=False,
        ):
            with patch(
                "office_screen.OfficeScreen.load_config"
            ) as mock_load_config:
                # Provide a user agent to avoid random.choice on empty list
                mock_load_config.return_value = {
                    "user_agents": ["Mozilla/5.0 (test)"]
                }

                with patch(
                    "office_screen.OfficeScreen.load_urls"
                ) as mock_load_urls:
                    mock_load_urls.return_value = []

                    office_screen = OfficeScreen()

                    # Mock requests for URL validation
                    with patch("office_screen.requests.head") as mock_head:
                        # Valid URLs
                        mock_response = MagicMock()
                        mock_response.status_code = 200
                        mock_head.return_value = mock_response
                        is_valid, _ = office_screen.validate_url(
                            "https://example.com"
                        )
                        assert is_valid is True

                        # Invalid URLs
                        mock_head.side_effect = Exception("Connection error")
                        is_valid, _ = office_screen.validate_url("not-a-url")
                        assert is_valid is False

    def test_adaptive_interval_adjustment(self):
        """Test adaptive interval adjustment based on success rate."""
        # Create a mock logger
        mock_logger = MagicMock()
        
        def setup_logging_side_effect(self):
            """Side effect that sets logger attribute."""
            self.logger = mock_logger
        
        with patch(
            "office_screen.OfficeScreen.setup_logging",
            side_effect=setup_logging_side_effect,
            autospec=False,
        ):
            with patch(
                "office_screen.OfficeScreen.load_config"
            ) as mock_load_config:
                mock_load_config.return_value = {
                    "adaptive_interval": True,
                    "min_interval": 30,
                    "max_interval": 180,
                }

                with patch(
                    "office_screen.OfficeScreen.load_urls"
                ) as mock_load_urls:
                    mock_load_urls.return_value = []

                    office_screen = OfficeScreen()
                    office_screen.interval = 90
                    office_screen.successful_visits = 4  # 40% success rate (< 50%)
                    office_screen.total_visits = 10
                    office_screen.min_interval = 30
                    office_screen.max_interval = 180

                    new_interval = office_screen.adaptive_interval_adjustment()

                    # Should increase interval for low success rate (< 50%)
                    assert new_interval > 90
                    assert new_interval <= 180


if __name__ == "__main__":
    pytest.main([__file__])

