"""
Pi-Pages - Advanced Web Automation Tool

A robust, enterprise-grade web automation tool designed for continuous browsing 
and monitoring of multiple websites.
"""

import os
import json

def get_version():
    """Get version from version.json file."""
    try:
        version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
        with open(version_file, "r") as f:
            version_data = json.load(f)
            return version_data["version_string"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return "1.0.0"

__version__ = get_version()
__author__ = "Pi-Pages Team"
__description__ = "Advanced web automation tool for continuous browsing and monitoring"

from .pi_pages import PiPages

__all__ = ["PiPages"] 