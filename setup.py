#!/usr/bin/env python3
"""
Setup script for office_screen
"""

from setuptools import setup
import os
import json

# Read the README file
def read_readme():
    """Read the README.md file and return its content."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    """Read the requirements.txt file and return a list of dependencies."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version - simple and clean
def get_version():
    """Get version - defaults to 2.0.0."""
    return "2.0.0"

setup(
    name="office_screen",
    version=get_version(),
    author="office_screen Team",
    author_email="",
    description="Advanced web automation tool for continuous browsing and monitoring",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/1devspace/office-screen",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "office-screen=office_screen:main",
        ],
    },
    py_modules=["office_screen"],
    include_package_data=True,
    zip_safe=False,
    keywords="web automation selenium browser monitoring",
    project_urls={
        "Bug Reports": "https://github.com/1devspace/office-screen/issues",
        "Source": "https://github.com/1devspace/office-screen",
        "Documentation": "https://github.com/1devspace/office-screen#readme",
    },
) 