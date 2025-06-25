#!/usr/bin/env python3
"""
Setup script for Pi-Pages
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pi-pages",
    version="2.0.0",
    author="Pi-Pages Team",
    author_email="",
    description="Advanced web automation tool for continuous browsing and monitoring",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pi-pages",
    packages=find_packages(),
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
            "pi-pages=pi_pages:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="web automation selenium browser monitoring",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pi-pages/issues",
        "Source": "https://github.com/yourusername/pi-pages",
        "Documentation": "https://github.com/yourusername/pi-pages#readme",
    },
) 