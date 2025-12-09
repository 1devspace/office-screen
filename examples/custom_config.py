#!/usr/bin/env python3
"""
Example: Using office_screen with custom configuration.

This example shows how to customize the behavior of office_screen.
"""

from office_screen import OfficeScreen


def main():
    """Example: Custom configuration usage."""
    # Initialize with custom config and URLs
    office = OfficeScreen(
        config_file="config/config.json",
        urls_file="config/urls/urls-software.json"
    )
    
    # Access configuration
    print(f"Interval: {office.interval} seconds")
    print(f"Adaptive interval: {office.adaptive_interval}")
    print(f"Total URLs loaded: {len(office.urls)}")
    
    # Get URLs by category
    categories = office.get_available_categories()
    print(f"Available categories: {categories}")
    
    # Start automation
    office.run()


if __name__ == "__main__":
    main()

