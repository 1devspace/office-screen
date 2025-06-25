#!/usr/bin/env python3
"""
Version management for office_screen
Handles semantic versioning and automatic version bumping
"""

import re
import os
import json
from datetime import datetime
from typing import Tuple, Optional


class VersionManager:
    """Manages semantic versioning for office_screen"""
    
    def __init__(self, version_file="version.json"):
        self.version_file = version_file
        self.version = self.load_version()
    
    def load_version(self) -> dict:
        """Load current version from file or create default"""
        default_version = {
            "major": 1,
            "minor": 0,
            "patch": 0,
            "build": 0,
            "prerelease": None,
            "build_date": datetime.now().isoformat(),
            "git_commit": self._get_git_commit(),
            "version_string": "1.0.0"
        }
        
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    version_data = json.load(f)
                    # Ensure all required fields exist
                    for key, value in default_version.items():
                        if key not in version_data:
                            version_data[key] = value
                    return version_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load version file: {e}")
                return default_version
        else:
            # Create default version file
            self.save_version(default_version)
            return default_version
    
    def save_version(self, version_data: dict) -> None:
        """Save version data to file"""
        try:
            with open(self.version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
        except IOError as e:
            print(f"Error saving version file: {e}")
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def bump_version(self, bump_type: str = "patch") -> str:
        """Bump version according to semantic versioning rules
        
        Args:
            bump_type: One of "major", "minor", "patch", "build"
        
        Returns:
            New version string
        """
        if bump_type not in ["major", "minor", "patch", "build"]:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        # Create a copy of current version
        new_version = self.version.copy()
        
        if bump_type == "major":
            new_version["major"] += 1
            new_version["minor"] = 0
            new_version["patch"] = 0
            new_version["build"] = 0
        elif bump_type == "minor":
            new_version["minor"] += 1
            new_version["patch"] = 0
            new_version["build"] = 0
        elif bump_type == "patch":
            new_version["patch"] += 1
            new_version["build"] = 0
        elif bump_type == "build":
            new_version["build"] += 1
        
        # Update metadata
        new_version["build_date"] = datetime.now().isoformat()
        new_version["git_commit"] = self._get_git_commit()
        
        # Generate version string
        version_parts = [str(new_version["major"]), str(new_version["minor"]), str(new_version["patch"])]
        version_string = ".".join(version_parts)
        
        if new_version["prerelease"]:
            version_string += f"-{new_version['prerelease']}"
        
        if new_version["build"] > 0:
            version_string += f"+build.{new_version['build']}"
        
        new_version["version_string"] = version_string
        
        # Save new version
        self.save_version(new_version)
        self.version = new_version
        
        return version_string
    
    def get_version_string(self) -> str:
        """Get current version as string"""
        return self.version["version_string"]
    
    def get_version_info(self) -> dict:
        """Get complete version information"""
        return self.version.copy()
    
    def set_prerelease(self, prerelease: str) -> None:
        """Set prerelease identifier (e.g., 'alpha', 'beta', 'rc.1')"""
        self.version["prerelease"] = prerelease
        self.bump_version("build")  # Increment build number
    
    def clear_prerelease(self) -> None:
        """Clear prerelease identifier"""
        self.version["prerelease"] = None
        self.save_version(self.version)
    
    def get_changelog_entry(self) -> str:
        """Generate changelog entry for current version"""
        version_info = self.get_version_info()
        return f"""## [{version_info['version_string']}] - {version_info['build_date'][:10]}

### Added
- New features and improvements

### Changed
- Updates and modifications

### Fixed
- Bug fixes and corrections

### Build Info
- Build Date: {version_info['build_date']}
- Git Commit: {version_info['git_commit']}
"""


def detect_version_bump(commit_messages: list) -> str:
    """Detect version bump type from commit messages
    
    Args:
        commit_messages: List of recent commit messages
    
    Returns:
        Bump type: "major", "minor", "patch", or "build"
    """
    # Keywords that indicate different types of changes
    major_keywords = ["breaking", "major", "incompatible", "deprecate"]
    minor_keywords = ["feature", "enhancement", "new", "add"]
    patch_keywords = ["fix", "bug", "patch", "correct"]
    
    # Check for major version indicators
    for message in commit_messages:
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in major_keywords):
            return "major"
    
    # Check for minor version indicators
    for message in commit_messages:
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in minor_keywords):
            return "minor"
    
    # Check for patch version indicators
    for message in commit_messages:
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in patch_keywords):
            return "patch"
    
    # Default to build bump for any other changes
    return "build"


def get_recent_commits(count: int = 10) -> list:
    """Get recent commit messages
    
    Args:
        count: Number of commits to retrieve
    
    Returns:
        List of commit messages
    """
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', f'--oneline', '-n', str(count)],
            capture_output=True,
            text=True,
            check=True
        )
        return [line.split(' ', 1)[1] for line in result.stdout.strip().split('\n') if line]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python version.py [bump|get|info|detect] [bump_type]")
        sys.exit(1)
    
    command = sys.argv[1]
    vm = VersionManager()
    
    if command == "bump":
        bump_type = sys.argv[2] if len(sys.argv) > 2 else "patch"
        new_version = vm.bump_version(bump_type)
        print(f"Version bumped to: {new_version}")
    
    elif command == "get":
        print(vm.get_version_string())
    
    elif command == "info":
        info = vm.get_version_info()
        print(json.dumps(info, indent=2))
    
    elif command == "detect":
        commits = get_recent_commits()
        bump_type = detect_version_bump(commits)
        print(f"Detected bump type: {bump_type}")
        print("Recent commits:")
        for commit in commits[:5]:
            print(f"  - {commit}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 