"""
Python Project Detector
Inherits from BaseDetector and implements Python-specific detection logic
"""
import re
from pathlib import Path
from typing import Optional, Dict, Set
from core.base_detector import BaseDetector


class PythonDetector(BaseDetector):
    """Detector for Python projects"""

    def detect(self) -> Optional[Dict]:
        """
        Detect Python project configuration

        Returns:
            Dict with Python project details or None if not a Python project
        """
        # Check if this is a Python project
        if not self._has_python_files():
            return None

        # Return detection results
        return {
            "language": "python",
            "framework": self._detect_framework(),
            "package_manager": self._detect_package_manager(),
            "python_version": self._detect_python_version(),
            "test_framework": self._detect_test_framework(),
        }

    # ============ Python-Specific Detection ============

    def _has_python_files(self) -> bool:
        """Check if project has Python files"""
        return self.has_files_with_extension('py')

    def _detect_package_manager(self) -> str:
        """Detect pip, poetry, or pipenv"""
        # Poetry uses poetry.lock and pyproject.toml with [tool.poetry]
        if self.file_exists('poetry.lock'):
            return 'poetry'

        # Pipenv uses Pipfile
        if self.file_exists('Pipfile'):
            return 'pipenv'

        # Default to pip if requirements.txt exists
        if self.file_exists('requirements.txt'):
            return 'pip'

        # Check pyproject.toml for poetry section
        pyproject_content = self.read_file('pyproject.toml')
        if '[tool.poetry]' in pyproject_content:
            return 'poetry'

        return 'pip'  # Default fallback

    def _detect_python_version(self) -> str:
        """Detect Python version from various sources"""
        # 1. Check .python-version (pyenv standard)
        if self.file_exists('.python-version'):
            version = self.read_file('.python-version').strip()
            return self.normalize_version(version)

        # 2. Check runtime.txt (Heroku standard)
        runtime_content = self.read_file('runtime.txt')
        if runtime_content:
            # Format: python-3.11.2
            version = self.extract_version_from_content(
                runtime_content,
                r'python-(\d+\.\d+(?:\.\d+)?)'
            )
            if version:
                return version

        # 3. Check pyproject.toml
        pyproject_content = self.read_file('pyproject.toml')
        if pyproject_content:
            # Look for: python = "^3.11"
            version = self.extract_version_from_content(
                pyproject_content,
                r'python\s*=\s*["\'][\^~>=]*(\d+\.\d+)'
            )
            if version:
                return version

        # 4. Check setup.py
        setup_content = self.read_file('setup.py')
        if setup_content:
            # Look for: python_requires='>=3.11'
            version = self.extract_version_from_content(
                setup_content,
                r'python_requires\s*=\s*["\'][>=~]*(\d+\.\d+)'
            )
            if version:
                return version

        # Default to 3.11 (current stable)
        return '3.11'

    def _detect_test_framework(self) -> str:
        """Detect pytest or unittest"""
        # 1. Check for pytest.ini
        if self.file_exists('pytest.ini'):
            return 'pytest'

        # 2. Check pyproject.toml for [tool.pytest]
        pyproject_content = self.read_file('pyproject.toml')
        if '[tool.pytest' in pyproject_content:
            return 'pytest'

        # 3. Check setup.cfg for [tool:pytest]
        setup_cfg_content = self.read_file('setup.cfg')
        if '[tool:pytest]' in setup_cfg_content or '[pytest]' in setup_cfg_content:
            return 'pytest'

        # 4. Check dependencies
        deps = self._read_all_dependencies()
        if 'pytest' in deps:
            return 'pytest'

        # 5. Check test files for imports
        if self._has_pytest_imports():
            return 'pytest'

        # Default to pytest (most common)
        return 'pytest'

    def _detect_framework(self) -> Optional[str]:
        """Detect Flask, Django, FastAPI, etc."""
        deps = self._read_all_dependencies()

        # Check in priority order
        if 'fastapi' in deps:
            return 'fastapi'
        elif 'flask' in deps:
            return 'flask'
        elif 'django' in deps:
            return 'django'

        return None  # Generic Python project

    # ============ Helper Methods ============

    def _read_all_dependencies(self) -> Set[str]:
        """Read dependencies from all common Python dependency files"""
        deps = set()

        # Check requirements.txt
        deps.update(self.parse_dependencies_from_file('requirements.txt'))

        # Check requirements-dev.txt
        deps.update(self.parse_dependencies_from_file('requirements-dev.txt'))

        # Check pyproject.toml
        pyproject_content = self.read_file('pyproject.toml')
        if pyproject_content:
            # Simple regex to find package names in dependencies list
            matches = re.findall(r'["\']([a-z0-9\-_]+)["\']', pyproject_content.lower())
            deps.update(matches)

        return deps

    def _has_pytest_imports(self) -> bool:
        """Check if test files import pytest"""
        test_dirs = ['tests', 'test']

        for test_dir in test_dirs:
            test_path = self.project_path / test_dir
            if test_path.exists():
                for test_file in test_path.rglob('test_*.py'):
                    try:
                        content = test_file.read_text()
                        if 'import pytest' in content or 'from pytest' in content:
                            return True
                    except Exception:
                        continue

        return False


# Example usage
if __name__ == "__main__":
    detector = PythonDetector(Path("/path/to/project"))
    config = detector.detect()
    print(config)