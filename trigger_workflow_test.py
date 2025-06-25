#!/usr/bin/env python3
"""
Script to test workflow functionality and provide guidance on triggering workflows.
"""

import os
import json
import subprocess
import sys
from pathlib import Path


def check_workflow_files():
    """Check if all workflow files exist and are valid."""
    print("🔍 Checking workflow files...")
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ .github/workflows directory not found")
        return False
    
    workflow_files = list(workflow_dir.glob("*.yml"))
    print(f"✅ Found {len(workflow_files)} workflow files:")
    
    for wf in workflow_files:
        print(f"  - {wf.name}")
    
    return True


def validate_yaml_syntax():
    """Validate YAML syntax of workflow files."""
    print("\n🔍 Validating YAML syntax...")
    
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML validation")
        return True
    
    workflow_dir = Path(".github/workflows")
    all_valid = True
    
    for wf_file in workflow_dir.glob("*.yml"):
        try:
            with open(wf_file, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {wf_file.name} - Valid YAML")
        except yaml.YAMLError as e:
            print(f"❌ {wf_file.name} - Invalid YAML: {e}")
            all_valid = False
    
    return all_valid


def check_project_structure():
    """Check if the project structure is correct for workflows."""
    print("\n🔍 Checking project structure...")
    
    required_files = [
        "pi-pages.py",
        "config.json", 
        "urls.json",
        "requirements.txt",
        "pyproject.toml"
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} - Present")
        else:
            print(f"❌ {file} - Missing")
            all_present = False
    
    return all_present


def validate_json_files():
    """Validate JSON configuration files."""
    print("\n🔍 Validating JSON files...")
    
    json_files = ["config.json", "urls.json"]
    all_valid = True
    
    for json_file in json_files:
        if Path(json_file).exists():
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
                print(f"✅ {json_file} - Valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ {json_file} - Invalid JSON: {e}")
                all_valid = False
        else:
            print(f"⚠️  {json_file} - Not found")
    
    return all_valid


def check_python_syntax():
    """Check Python syntax of main files."""
    print("\n🔍 Checking Python syntax...")
    
    python_files = ["pi-pages.py"]
    if Path("pi_pages/pi_pages.py").exists():
        python_files.append("pi_pages/pi_pages.py")
    
    all_valid = True
    for py_file in python_files:
        if Path(py_file).exists():
            try:
                subprocess.run([sys.executable, "-m", "py_compile", py_file], 
                             capture_output=True, check=True)
                print(f"✅ {py_file} - Valid Python syntax")
            except subprocess.CalledProcessError:
                print(f"❌ {py_file} - Invalid Python syntax")
                all_valid = False
        else:
            print(f"⚠️  {py_file} - Not found")
    
    return all_valid


def create_test_commit():
    """Create a test commit to trigger workflows."""
    print("\n🚀 Creating test commit to trigger workflows...")
    
    # Create a simple test file
    test_file = "workflow_test_trigger.txt"
    with open(test_file, 'w') as f:
        f.write(f"Workflow test trigger - {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}\n")
    
    try:
        # Add and commit the file
        subprocess.run(["git", "add", test_file], check=True)
        subprocess.run(["git", "commit", "-m", "test: trigger workflow test"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Test commit created and pushed successfully!")
        print("📊 Check the GitHub Actions tab to see workflows running")
        
        # Clean up the test file
        subprocess.run(["git", "rm", test_file], check=True)
        subprocess.run(["git", "commit", "-m", "test: remove workflow trigger file"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Test file cleaned up")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create test commit: {e}")
        return False
    
    return True


def show_workflow_status():
    """Show information about workflow status."""
    print("\n📊 Workflow Status Information:")
    print("=" * 50)
    
    print("""
🎯 To check workflow status:

1. **GitHub Web Interface:**
   - Go to your repository on GitHub
   - Click on the "Actions" tab
   - You'll see all workflow runs and their status

2. **GitHub CLI (if authenticated):**
   - Run: gh run list
   - Run: gh run view <run-id>

3. **Manual Trigger:**
   - Go to Actions tab on GitHub
   - Click on a workflow (e.g., "Simple Test")
   - Click "Run workflow" button
   - Select branch and click "Run workflow"

4. **Push Trigger:**
   - Any push to main branch triggers workflows
   - Pull requests also trigger workflows

🔧 Workflow Files Created:
- ci.yml - Main CI pipeline
- test-simple.yml - Simple test workflow
- test.yml - Comprehensive testing
- security.yml - Security scanning
- code-quality.yml - Code formatting
- performance.yml - Performance testing
- documentation.yml - Documentation building
- docker.yml - Docker testing
- release.yml - Package publishing
- dependency-update.yml - Dependency updates

✅ Expected Behavior:
- Workflows should run automatically on push/PR
- Each workflow has specific jobs and steps
- Results are reported in the Actions tab
- Failed workflows show detailed error logs
""")


def main():
    """Main function to run all checks."""
    print("🚀 Pi-Pages Workflow Testing Script")
    print("=" * 50)
    
    checks = [
        ("Workflow Files", check_workflow_files),
        ("YAML Syntax", validate_yaml_syntax),
        ("Project Structure", check_project_structure),
        ("JSON Validation", validate_json_files),
        ("Python Syntax", check_python_syntax),
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
        print("\n🎉 All checks passed! Workflows should work correctly.")
        
        # Ask if user wants to trigger a test
        try:
            response = input("\n🤔 Would you like to create a test commit to trigger workflows? (y/n): ")
            if response.lower() in ['y', 'yes']:
                create_test_commit()
        except KeyboardInterrupt:
            print("\n⏹️  Skipping test commit")
        
        show_workflow_status()
        return 0
    else:
        print(f"\n⚠️  {failed} check(s) failed. Please fix the issues before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 