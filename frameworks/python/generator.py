"""
Python Project Generator
Inherits from BaseGenerator and implements Python-specific generation logic
"""
from pathlib import Path
from typing import Dict, Any
from core.base_generator import BaseGenerator


class PythonGenerator(BaseGenerator):
    """Generator for Python projects"""

    def __init__(self):
        """Initialize Python generator"""
        super().__init__('python')

    def generate(self, detection_result: Dict, output_dir: Path) -> Dict:
        """
        Generate CI/CD files for Python project

        Args:
            detection_result: Dict from PythonDetector
            output_dir: Where to write generated files

        Returns:
            Dict with generated file paths and context
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Get project path
        project_path = Path(detection_result.get('project_path', output_dir))

        # Prepare template context
        context = self._prepare_context(detection_result, project_path)

        # Print generation info
        print(f"\n📦 Generating files for: {context['project_name']}")
        print(f"   Python: {context['python_version']}")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Package Manager: {context['package_manager']}")

        # Generate files
        generated_files = {}

        # 1. Generate Jenkinsfile
        jenkinsfile_path = output_path / 'jenkinsfile'
        self.generate_file_from_template('Jenkinsfile.j2', context, jenkinsfile_path)
        generated_files['jenkinsfile'] = str(jenkinsfile_path)

        # 2. Generate Dockerfile
        dockerfile_path = output_path / 'Dockerfile'
        self.generate_file_from_template('Dockerfile.j2', context, dockerfile_path)
        generated_files['dockerfile'] = str(dockerfile_path)

        # 3. Generate docker-compose.yml (if template exists)
        compose_template = self.templates_dir / 'docker-compose.yml.j2'
        if compose_template.exists():
            compose_path = output_path / 'docker-compose.yml'
            self.generate_file_from_template('docker-compose.yml.j2', context, compose_path)
            generated_files['docker_compose'] = str(compose_path)

        # 4. Generate README (if template exists)
        readme_template = self.templates_dir / 'README.md.j2'
        if readme_template.exists():
            readme_path = output_path / 'CICD_README.md'
            self.generate_file_from_template('README.md.j2', context, readme_path)
            generated_files['readme'] = str(readme_path)

        return {
            'context': context,
            'generated_files': generated_files
        }

    # ============ Python-Specific Context Preparation ============

    def _prepare_context(self, detection_result: Dict, project_path: Path) -> Dict[str, Any]:
        """Prepare Jinja2 template context from detection results"""

        # Start with base context from parent
        context = self.add_base_context(detection_result, project_path)

        # Add Python-specific fields
        context.update({
            # Python-specific info
            'python_version': detection_result.get('python_version', '3.11'),
            'package_manager': detection_result.get('package_manager', 'pip'),
            'test_framework': detection_result.get('test_framework', 'pytest'),

            # Detected project structure
            'app_module': self.detect_app_module(project_path),
            'has_requirements_txt': (project_path / 'requirements.txt').exists(),
            'has_requirements_dev': (project_path / 'requirements-dev.txt').exists(),
            'build_package': self._is_library(project_path),

            # Pipeline configuration
            'enable_linting': True,
            'enable_security_scan': True,
            'enable_docker': True,

            # Docker config
            'docker_base_image': f"python:{detection_result.get('python_version', '3.11')}-slim",
            'docker_port': self._get_framework_port(detection_result.get('framework')),
        })

        return context

    # ============ Python-Specific Helper Methods ============

    def _is_library(self, project_path: Path) -> bool:
        """
        Determine if this is a library (needs package building) or application
        """
        # Check for setup.py
        if (project_path / 'setup.py').exists():
            return True

        # Check pyproject.toml for build system
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                if '[build-system]' in content:
                    return True
            except Exception:
                pass

        return False

    def _get_framework_port(self, framework: str) -> int:
        """Get default port for Python framework"""
        ports = {
            'flask': 5000,
            'django': 8000,
            'fastapi': 8000,
        }
        return ports.get(framework, 8000)

    def _is_valid_module(self, path: Path) -> bool:
        """
        Override parent method - Python modules have __init__.py
        """
        return (path / '__init__.py').exists()


# Example usage
if __name__ == "__main__":
    detection = {
        'language': 'python',
        'framework': 'flask',
        'python_version': '3.11',
        'package_manager': 'pip',
        'test_framework': 'pytest',
        'project_path': '/tmp/test-flask-app'
    }

    generator = PythonGenerator()
    result = generator.generate(detection, Path('/tmp/test-flask-app/generated'))

    print("\n✅ Generation complete!")
    print(f"Files: {list(result['generated_files'].keys())}")