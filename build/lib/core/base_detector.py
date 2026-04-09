"""
Base Detector class for all framework detectors
Provides common utilities for file checking, reading, and dependency parsing
"""
import re
from pathlib import Path
from typing import Optional, Set, Dict


class BaseDetector:
    """Base class for framework-specific detectors"""

    def __init__(self, project_path: Path):
        """
        Initialize detector with project path

        Args:
            project_path: Path to the project to detect
        """
        self.project_path = Path(project_path)

    def detect(self) -> Optional[Dict]:
        """
        Main detection method - must be overridden by child classes

        Returns:
            Dict with detection results or None if not detected
        """
        raise NotImplementedError("Subclasses must implement detect()")

    # ============ Shared File Utilities ============

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in project"""
        return (self.project_path / filename).exists()

    def read_file(self, filename: str) -> str:
        """Read file content safely"""
        try:
            file_path = self.project_path / filename
            if file_path.exists():
                return file_path.read_text()
        except Exception:
            pass
        return ""

    def has_files_with_extension(self, extension: str) -> bool:
        """Check if project has files with given extension"""
        pattern = f"*.{extension}" if not extension.startswith('*') else extension
        return bool(list(self.project_path.rglob(pattern)))

    # ============ Shared Version Detection ============

    def normalize_version(self, version: str) -> str:
        """
        Normalize version to X.Y format
        Example: 3.11.2 -> 3.11
        """
        parts = version.split('.')
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return version

    def extract_version_from_content(self, content: str, pattern: str) -> Optional[str]:
        """
        Extract version using regex pattern

        Args:
            content: File content to search
            pattern: Regex pattern with one capture group for version
        """
        match = re.search(pattern, content)
        if match:
            return self.normalize_version(match.group(1))
        return None

    # ============ Shared Dependency Parsing ============

    def parse_dependencies_from_file(self, filename: str) -> Set[str]:
        """
        Parse dependencies from a requirements-style file
        Returns set of lowercase package names
        """
        deps = set()
        content = self.read_file(filename)

        for line in content.split('\n'):
            line = line.strip().lower()
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('-r'):
                continue

            # Extract package name (before ==, >=, etc.)
            pkg = re.split(r'[=<>~!]', line)[0].strip()
            if pkg:
                deps.add(pkg)

        return deps

    def check_dependency_in_files(self, dependency: str, *filenames) -> bool:
        """
        Check if a dependency exists in any of the given files

        Args:
            dependency: Package name to look for (case-insensitive)
            *filenames: Variable number of filenames to check
        """
        dependency = dependency.lower()
        for filename in filenames:
            deps = self.parse_dependencies_from_file(filename)
            if dependency in deps:
                return True
        return False