import os
import re
from pathlib import Path


class ProjectDetector:
    def __init__(self, project_path):
        self.project_path = Path(project_path)

    def detect(self):
        """Detect Python project configuration"""
        if not self._has_python_files():
            return None

        return {
            "language": "python",
            "framework": self._detect_framework(),
            "package_manager": self._detect_package_manager(),
            "python_version": self._detect_python_version(),
            "test_framework": self._detect_test_framework(),
        }

    def _has_python_files(self):
        """Check if project has Python files"""
        for ext in ['*.py']:
            if list(self.project_path.rglob(ext)):
                return True
        return False

    def _detect_package_manager(self):
        """Detect pip, poetry, or pipenv"""
        # Poetry uses poetry.lock and pyproject.toml with [tool.poetry]
        if (self.project_path / 'poetry.lock').exists():
            return 'poetry'

        # Pipenv uses Pipfile
        if (self.project_path / 'Pipfile').exists():
            return 'pipenv'

        # Default to pip if requirements.txt exists or nothing found
        if (self.project_path / 'requirements.txt').exists():
            return 'pip'

        # Check pyproject.toml for poetry section
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            if '[tool.poetry]' in content:
                return 'poetry'

        return 'pip'  # Default fallback

    def _detect_python_version(self):
        """Detect Python version from various sources"""
        # 1. Check .python-version (pyenv standard)
        python_version_file = self.project_path / '.python-version'
        if python_version_file.exists():
            version = python_version_file.read_text().strip()
            return self._normalize_version(version)

        # 2. Check runtime.txt (Heroku standard)
        runtime_file = self.project_path / 'runtime.txt'
        if runtime_file.exists():
            content = runtime_file.read_text().strip()
            # Format: python-3.11.2
            match = re.search(r'python-(\d+\.\d+)', content)
            if match:
                return match.group(1)

        # 3. Check pyproject.toml
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            # Look for: python = "^3.11"
            match = re.search(r'python\s*=\s*["\'][\^~>=]*(\d+\.\d+)', content)
            if match:
                return match.group(1)

        # 4. Check setup.py
        setup_py = self.project_path / 'setup.py'
        if setup_py.exists():
            content = setup_py.read_text()
            # Look for: python_requires='>=3.11'
            match = re.search(r'python_requires\s*=\s*["\'][>=~]*(\d+\.\d+)', content)
            if match:
                return match.group(1)

        # Default to 3.11 (current stable)
        return '3.11'

    def _normalize_version(self, version):
        """Normalize version to X.Y format"""
        # Convert 3.11.2 -> 3.11
        parts = version.split('.')
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return version

    def _detect_test_framework(self):
        """Detect pytest or unittest"""
        # 1. Check for pytest.ini
        if (self.project_path / 'pytest.ini').exists():
            return 'pytest'

        # 2. Check pyproject.toml for [tool.pytest]
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            if '[tool.pytest' in content:
                return 'pytest'

        # 3. Check setup.cfg for [tool:pytest]
        setup_cfg = self.project_path / 'setup.cfg'
        if setup_cfg.exists():
            content = setup_cfg.read_text()
            if '[tool:pytest]' in content or '[pytest]' in content:
                return 'pytest'

        # 4. Check dependencies
        deps = self._read_dependencies()
        if 'pytest' in deps:
            return 'pytest'

        # 5. Check test files for imports
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            test_path = self.project_path / test_dir
            if test_path.exists():
                for test_file in test_path.rglob('test_*.py'):
                    content = test_file.read_text()
                    if 'import pytest' in content or 'from pytest' in content:
                        return 'pytest'

        # Default to pytest (most common)
        return 'pytest'

    def _detect_framework(self):
        """Detect Flask, Django, FastAPI, etc."""
        deps = self._read_dependencies()

        if 'fastapi' in deps:
            return 'fastapi'
        elif 'flask' in deps:
            return 'flask'
        elif 'django' in deps:
            return 'django'

        return None  # Generic Python project

    def _read_dependencies(self):
        """Read dependencies from requirements.txt or pyproject.toml"""
        deps = set()

        # Check requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            content = req_file.read_text()
            for line in content.split('\n'):
                line = line.strip().lower()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, etc.)
                    pkg = re.split(r'[=<>~!]', line)[0].strip()
                    deps.add(pkg)

        # Check requirements-dev.txt
        req_dev = self.project_path / 'requirements-dev.txt'
        if req_dev.exists():
            content = req_dev.read_text()
            for line in content.split('\n'):
                line = line.strip().lower()
                if line and not line.startswith('#') and not line.startswith('-r'):
                    pkg = re.split(r'[=<>~!]', line)[0].strip()
                    deps.add(pkg)

        # Check pyproject.toml
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text().lower()
            # Simple regex to find package names in dependencies list
            matches = re.findall(r'["\']([a-z0-9\-_]+)["\']', content)
            deps.update(matches)

        return deps


# Example usage
if __name__ == "__main__":
    detector = ProjectDetector("/path/to/project")
    config = detector.detect()
    print(config)