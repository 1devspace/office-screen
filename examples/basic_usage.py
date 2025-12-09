#!/usr/bin/env python3
"""
Basic usage example for office_screen.

This example demonstrates how to use office_screen programmatically.
"""

from office_screen import OfficeScreen


def main():
    """Example: Basic usage of OfficeScreen."""
    # Initialize with default configuration
    office = OfficeScreen()
    
    # Or initialize with custom configuration
    # office = OfficeScreen(
    #     config_file="config/my-config.json",
    #     urls_file="config/urls/urls-business.json"
    # )
    
    # Start the automation
    office.run()


if __name__ == "__main__":
    main()

