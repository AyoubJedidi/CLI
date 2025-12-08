"""
Python Project Generator
Inherits from BaseGenerator and implements Python-specific generation logic
"""
from pathlib import Path
from typing import Dict, Any, List
from core.base_generator import BaseGenerator


class PythonGenerator(BaseGenerator):
    """Generator for Python projects"""

    def __init__(self):
        """Initialize Python generator"""
        super().__init__('python')

    def get_platform_template_map(self) -> Dict[str, Dict]:
        """Define templates for each platform"""
        return {
            'jenkins': {
                'template': 'Jenkinsfile.j2',
                'output': 'Jenkinsfile'
            },
            'gitlab': {
                'template': 'gitlab-ci.yml.j2',
                'output': '.gitlab-ci.yml'
            },
            'github': {
                'template': 'github-actions.yml.j2',
                'output': '.github/workflows/ci.yml'
            }
        }

    def generate(self, detection_result: Dict, output_dir: Path, platforms: List[str] = None) -> Dict:
        """
        Generate CI/CD files for Python project

        Args:
            detection_result: Detection results from PythonDetector
            output_dir: Directory where files will be generated
            platforms: List of platforms to generate for (default: ['jenkins'])

        Returns:
            Dict with generated files and context
        """
        if platforms is None:
            platforms = ['jenkins']

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
        print(f"   Platforms: {', '.join(platforms)}")

        # Get platform template map
        template_map = self.get_platform_template_map()
        generated_files = {}

        # Generate CI/CD files for each requested platform
        for platform in platforms:
            if platform not in template_map:
                print(f"   ⚠️  Skipping unknown platform: {platform}")
                continue

            config = template_map[platform]
            platform_output = output_path / config['output']

            try:
                # Create parent directories if needed (for .github/workflows/)
                platform_output.parent.mkdir(parents=True, exist_ok=True)

                self.generate_file_from_template(
                    config['template'],
                    context,
                    platform_output,
                    verbose=True
                )
                generated_files[platform] = str(platform_output)
            except Exception as e:
                print(f"   ❌ Failed to generate {platform}: {e}")

        # Generate additional files (Dockerfile, docker-compose, README)
        self._generate_additional_files(context, output_path, generated_files)

        return {
            'context': context,
            'generated_files': generated_files
        }

    # ============ Additional Files Generation ============

    def _generate_additional_files(self, context: Dict, output_path: Path, generated_files: Dict):
        """Generate Docker and README files if templates exist"""

        # 1. Generate Dockerfile
        dockerfile_template = self.templates_dir / 'Dockerfile.j2'
        if dockerfile_template.exists():
            dockerfile_path = output_path / 'Dockerfile'
            try:
                self.generate_file_from_template('Dockerfile.j2', context, dockerfile_path)
                generated_files['dockerfile'] = str(dockerfile_path)
            except Exception as e:
                print(f"   ⚠️  Could not generate Dockerfile: {e}")

        # 2. Generate docker-compose.yml
        compose_template = self.templates_dir / 'docker-compose.yml.j2'
        if compose_template.exists():
            compose_path = output_path / 'docker-compose.yml'
            try:
                self.generate_file_from_template('docker-compose.yml.j2', context, compose_path)
                generated_files['docker_compose'] = str(compose_path)
            except Exception as e:
                print(f"   ⚠️  Could not generate docker-compose.yml: {e}")

        # 3. Generate README
        readme_template = self.templates_dir / 'README.md.j2'
        if readme_template.exists():
            readme_path = output_path / 'CICD_README.md'
            try:
                self.generate_file_from_template('README.md.j2', context, readme_path)
                generated_files['readme'] = str(readme_path)
            except Exception as e:
                print(f"   ⚠️  Could not generate README: {e}")

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
            'has_tests': self._has_tests(project_path),
            'build_package': self._is_library(project_path),

            # Pipeline configuration
            'enable_linting': True,
            'enable_security_scan': True,
            'enable_docker': True,

            # Docker config
            'docker_base_image': f"python:{detection_result.get('python_version', '3.11')}-slim",
            'docker_port': self._get_framework_port(detection_result.get('framework')),

            # Additional context for templates
            'has_pyproject_toml': (project_path / 'pyproject.toml').exists(),
            'has_setup_py': (project_path / 'setup.py').exists(),
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
                if '[build-system]' in content or '[tool.poetry]' in content:
                    return True
            except Exception:
                pass

        return False

    def _has_tests(self, project_path: Path) -> bool:
        """Check if project has tests directory"""
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            if (project_path / test_dir).is_dir():
                return True
        return False

    def _get_framework_port(self, framework: str) -> int:
        """Get default port for Python framework"""
        if not framework:
            return 8000

        ports = {
            'flask': 5000,
            'django': 8000,
            'fastapi': 8000,
            'starlette': 8000,
            'tornado': 8888,
            'aiohttp': 8080,
        }
        return ports.get(framework.lower(), 8000)

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

    # Test single platform
    result = generator.generate(detection, Path('/tmp/test-flask-app/generated'), platforms=['jenkins'])
    print("\n✅ Jenkins generation complete!")
    print(f"Files: {list(result['generated_files'].keys())}")

    # Test multiple platforms
    result = generator.generate(detection, Path('/tmp/test-flask-app/generated'),
                                platforms=['jenkins', 'gitlab', 'github'])
    print("\n✅ Multi-platform generation complete!")
    print(f"Files: {list(result['generated_files'].keys())}")