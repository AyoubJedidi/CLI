"""
Generator for Python projects
Place this at: cli/generator.py
"""

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


class ProjectGenerator:  # Keep your original class name
    def __init__(self, templates_dir):
        """
        Initialize generator with templates directory

        Args:
            templates_dir: Path to templates folder
        """
        self.templates_dir = Path(templates_dir)

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(self, detection_result, output_dir):
        """
        Generate pipeline files based on detection result

        Args:
            detection_result: Dict from detector
            output_dir: Where to write generated files

        Returns:
            Dict with paths of generated files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Get project path
        project_path = Path(detection_result.get('project_path', output_dir))

        # Prepare template context
        context = self._prepare_context(detection_result, project_path)

        print(f"\n📦 Generating files for: {context['project_name']}")
        print(f"   Python: {context['python_version']}")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Package Manager: {context['package_manager']}")

        # Generate files
        generated_files = {}

        # 1. Generate Jenkinsfile
        jenkinsfile_path = output_path / 'jenkinsfile'
        self._generate_file('jenkins_test.j2', context, jenkinsfile_path)
        generated_files['jenkinsfile'] = str(jenkinsfile_path)

        # 2. Generate Dockerfile
        dockerfile_path = output_path / 'Dockerfile'
        self._generate_file('docker_test.j2', context, dockerfile_path)
        generated_files['dockerfile'] = str(dockerfile_path)

        # 3. Generate docker-compose.yml (if template exists)
        if (self.templates_dir / 'docker-compose.yml.j2').exists():
            compose_path = output_path / 'docker-compose.yml'
            self._generate_file('docker-compose.yml.j2', context, compose_path)
            generated_files['docker_compose'] = str(compose_path)

        # 4. Generate README (if template exists)
        if (self.templates_dir / 'README.md.j2').exists():
            readme_path = output_path / 'CICD_README.md'
            self._generate_file('README.md.j2', context, readme_path)
            generated_files['readme'] = str(readme_path)

        return {
            'context': context,
            'generated_files': generated_files
        }

    def _prepare_context(self, detection_result, project_path):
        """Prepare Jinja2 template context from detection results"""

        # Get project name from directory
        project_name = project_path.name if project_path.name else 'my-app'

        # Detect app module (main source code directory)
        app_module = self._detect_app_module(project_path)

        # Check for requirements files
        has_requirements_txt = (project_path / 'requirements.txt').exists()
        has_requirements_dev = (project_path / 'requirements-dev.txt').exists()

        # Determine if this is a library or application
        build_package = self._is_library(project_path)

        context = {
            # Basic info
            'project_name': project_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

            # From detection
            'language': detection_result.get('language', 'python'),
            'python_version': detection_result.get('python_version', '3.11'),
            'framework': detection_result.get('framework'),
            'package_manager': detection_result.get('package_manager', 'pip'),
            'test_framework': detection_result.get('test_framework', 'pytest'),

            # Detected project structure
            'app_module': app_module,
            'has_requirements_txt': has_requirements_txt,
            'has_requirements_dev': has_requirements_dev,
            'build_package': build_package,

            # Pipeline configuration
            'enable_linting': True,
            'enable_security_scan': True,
            'enable_docker': True,

            # Docker config
            'docker_base_image': f"python:{detection_result.get('python_version', '3.11')}-slim",
            'docker_port': self._get_framework_port(detection_result.get('framework')),
        }

        return context

    def _detect_app_module(self, project_path):
        """
        Detect the main application module name
        Common patterns: app/, src/, project_name/
        """
        # Check common directories
        for candidate in ['app', 'src', 'cli', project_path.name]:
            candidate_path = project_path / candidate
            if candidate_path.is_dir() and (candidate_path / '__init__.py').exists():
                return candidate

        # Fallback: find any directory with __init__.py
        try:
            for item in project_path.iterdir():
                if item.is_dir() and (item / '__init__.py').exists():
                    # Skip common non-app directories
                    if item.name not in ['tests', 'test', 'docs', 'scripts', 'venv', '.venv', 'templates']:
                        return item.name
        except:
            pass

        return 'app'  # Default fallback

    def _is_library(self, project_path):
        """
        Determine if this is a library (needs package building) or application
        """
        if (project_path / 'setup.py').exists():
            return True

        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                if '[build-system]' in content:
                    return True
            except:
                pass

        return False

    def _get_framework_port(self, framework):
        """Get default port for framework"""
        ports = {
            'flask': 5000,
            'django': 8000,
            'fastapi': 8000,
        }
        return ports.get(framework, 8000)

    def _generate_file(self, template_name, context, output_path):
        """Generate a single file from template"""
        try:
            template = self.jinja_env.get_template(template_name)
            content = template.render(context)
            output_path.write_text(content)
            print(f"   ✓ Generated: {output_path.name}")
        except Exception as e:
            print(f"   ✗ Failed to generate {template_name}: {e}")
            raise


# For testing
if __name__ == "__main__":
    # Example usage
    detection = {
        'language': 'python',
        'framework': 'flask',
        'python_version': '3.11',
        'package_manager': 'pip',
        'test_framework': 'pytest',
        'project_path': '/tmp/test-flask-app'
    }

    generator = ProjectGenerator('templates')
    result = generator.generate(detection, '/tmp/test-flask-app/generated')

    print("\n✅ Generation complete!")
    print(f"Files: {list(result['generated_files'].keys())}")