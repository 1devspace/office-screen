#!/usr/bin/env python3
"""
Local test script to verify workflow functionality.
This script runs the same checks that the GitHub Actions workflows would perform.
"""

import subprocess
import sys
import os
import json
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_python_syntax():
    """Check Python syntax."""
    return run_command("python -m py_compile pi-pages.py", "Python syntax check")


def check_imports():
    """Check if the module can be imported."""
    return run_command("python -c 'import pi_pages; print(\"Import successful\")'", "Module import test")


def check_requirements():
    """Check if requirements can be installed."""
    return run_command("pip install -r requirements.txt", "Requirements installation")


def check_code_formatting():
    """Check code formatting with Black."""
    try:
        subprocess.run("pip install black", shell=True, capture_output=True)
        return run_command("black --check --diff .", "Code formatting (Black)")
    except:
        print("⚠️  Black not available, skipping formatting check")
        return True


def check_import_sorting():
    """Check import sorting with isort."""
    try:
        subprocess.run("pip install isort", shell=True, capture_output=True)
        return run_command("isort --check-only --diff .", "Import sorting (isort)")
    except:
        print("⚠️  isort not available, skipping import sorting check")
        return True


def check_linting():
    """Check code with flake8."""
    try:
        subprocess.run("pip install flake8", shell=True, capture_output=True)
        return run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Code linting (flake8)")
    except:
        print("⚠️  flake8 not available, skipping linting check")
        return True


def check_security():
    """Check security with bandit."""
    try:
        subprocess.run("pip install bandit", shell=True, capture_output=True)
        return run_command("bandit -r . -f json", "Security scan (bandit)")
    except:
        print("⚠️  bandit not available, skipping security check")
        return True


def check_dependencies():
    """Check dependencies with safety."""
    try:
        subprocess.run("pip install safety", shell=True, capture_output=True)
        return run_command("safety check --json", "Dependency security (safety)")
    except:
        print("⚠️  safety not available, skipping dependency check")
        return True


def check_tests():
    """Run tests with pytest."""
    try:
        subprocess.run("pip install pytest pytest-cov", shell=True, capture_output=True)
        return run_command("python -m pytest tests/ -v --cov=pi_pages", "Unit tests (pytest)")
    except:
        print("⚠️  pytest not available, skipping tests")
        return True


def check_docker_build():
    """Check if Dockerfile can be built."""
    if not Path("Dockerfile").exists():
        print("⚠️  Dockerfile not found, skipping Docker check")
        return True
    
    return run_command("docker build -t pi-pages-test .", "Docker build test")


def check_config_files():
    """Check if configuration files are valid JSON."""
    config_files = ["config.json", "urls.json"]
    all_valid = True
    
    for config_file in config_files:
        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    json.load(f)
                print(f"✅ {config_file} - Valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ {config_file} - Invalid JSON: {e}")
                all_valid = False
        else:
            print(f"⚠️  {config_file} - Not found")
    
    return all_valid


def main():
    """Run all checks."""
    print("🚀 Starting local workflow tests...")
    print("=" * 50)
    
    checks = [
        ("Python Syntax", check_python_syntax),
        ("Module Import", check_imports),
        ("Requirements", check_requirements),
        ("Code Formatting", check_code_formatting),
        ("Import Sorting", check_import_sorting),
        ("Code Linting", check_linting),
        ("Security Scan", check_security),
        ("Dependency Security", check_dependencies),
        ("Unit Tests", check_tests),
        ("Docker Build", check_docker_build),
        ("Config Files", check_config_files),
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All checks passed! Your workflows should work correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} check(s) failed. Please fix the issues before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 