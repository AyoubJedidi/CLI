"""
Maven Project Generator
Generates Maven-specific CI/CD files
"""
from pathlib import Path
from typing import Dict, Any
from core.base_generator import BaseGenerator


class MavenGenerator(BaseGenerator):
    """Generator for Maven projects"""

    def __init__(self):
        super().__init__('maven')

    def generate(self, detection_result: Dict, output_dir: Path) -> Dict:
        """Generate CI/CD files for Maven project"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        project_path = Path(detection_result.get('project_path', output_dir))
        context = self._prepare_context(detection_result, project_path)

        print(f"\n📦 Generating files for: {context['project_name']}")
        print(f"   Java: {context['java_version']}")
        print(f"   Build Tool: Maven")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Multi-module: {context['is_multi_module']}")

        generated_files = {}

        # Generate Jenkinsfile
        jenkinsfile_path = output_path / 'Jenkinsfile'
        self.generate_file_from_template('Jenkinsfile.j2', context, jenkinsfile_path)
        generated_files['jenkinsfile'] = str(jenkinsfile_path)

        # Generate Dockerfile
        dockerfile_path = output_path / 'Dockerfile'
        self.generate_file_from_template('Dockerfile.j2', context, dockerfile_path)
        generated_files['dockerfile'] = str(dockerfile_path)

        return {
            'context': context,
            'generated_files': generated_files
        }

    def _prepare_context(self, detection_result: Dict, project_path: Path) -> Dict[str, Any]:
        """Prepare Maven-specific template context"""
        context = self.add_base_context(detection_result, project_path)

        java_version = detection_result.get('java_version', '17')

        context.update({
            'java_version': java_version,
            'build_tool': 'maven',
            'test_framework': detection_result.get('test_framework', 'junit5'),
            'is_multi_module': detection_result.get('is_multi_module', False),
            'packaging': detection_result.get('packaging', 'jar'),
            'docker_base_image': f"eclipse-temurin:{java_version}-jdk-alpine",
            'docker_runtime_image': f"eclipse-temurin:{java_version}-jre-alpine",
            'docker_port': self._get_framework_port(detection_result.get('framework')),
        })

        return context

    def _get_framework_port(self, framework: str) -> int:
        """Get default port for Java framework"""
        ports = {
            'spring-boot': 8080,
            'quarkus': 8080,
            'micronaut': 8080,
            'jakarta-ee': 8080,
        }
        return ports.get(framework, 8080)