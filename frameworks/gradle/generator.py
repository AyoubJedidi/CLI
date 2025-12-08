"""
Gradle Project Generator
Generates Gradle-specific CI/CD files
"""
from pathlib import Path
from typing import Dict, Any, List
from core.base_generator import BaseGenerator


class GradleGenerator(BaseGenerator):
    """Generator for Gradle projects"""

    def __init__(self):
        super().__init__('gradle')

    def get_platform_template_map(self) -> Dict[str, Dict[str, str]]:
        """Get platform-specific template mapping for Gradle"""
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
                'output': '.github/workflows/ci-cd.yml'
            },
            'docker': {
                'template': 'Dockerfile.j2',
                'output': 'Dockerfile'
            }
        }

    def generate(self, detection_result: Dict, output_dir: Path, platforms: List[str] = None) -> Dict:
        """
        Generate CI/CD files for Gradle project

        Args:
            detection_result: Detection results from GradleDetector
            output_dir: Directory where files will be generated
            platforms: List of platforms to generate for (default: ['jenkins'])

        Returns:
            Dict with generated files and context
        """
        if platforms is None:
            platforms = ['jenkins']

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        project_path = Path(detection_result.get('project_path', output_dir))
        context = self._prepare_context(detection_result, project_path)

        print(f"\n📦 Generating files for: {context['project_name']}")
        print(f"   Java: {context['java_version']}")
        print(f"   Build Tool: Gradle")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Kotlin DSL: {context['uses_kotlin_dsl']}")
        print(f"   Platforms: {', '.join(platforms)}")

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

        # Generate additional files
        self._generate_additional_files(context, output_path, generated_files)

        return {
            'context': context,
            'generated_files': generated_files
        }

    def _generate_additional_files(self, context: Dict, output_path: Path, generated_files: Dict) -> None:
        """Generate additional files like Dockerfile, docker-compose"""
        try:
            dockerfile_path = output_path / 'Dockerfile'
            self.generate_file_from_template(
                'Dockerfile.j2',
                context,
                dockerfile_path,
                verbose=True
            )
            generated_files['dockerfile'] = str(dockerfile_path)
        except Exception as e:
            print(f"   ⚠️  Skipping Dockerfile: {e}")



    def _prepare_context(self, detection_result: Dict, project_path: Path) -> Dict[str, Any]:
        """Prepare Gradle-specific template context"""
        context = self.add_base_context(detection_result, project_path)

        java_version = detection_result.get('java_version', '17')

        context.update({
            'java_version': java_version,
            'build_tool': 'gradle',
            'test_framework': detection_result.get('test_framework', 'junit5'),
            'uses_kotlin_dsl': detection_result.get('uses_kotlin_dsl', False),
            'is_multi_project': detection_result.get('is_multi_project', False),
            'packaging': detection_result.get('packaging', 'jar'),
            'docker_base_image': f"eclipse-temurin:{java_version}-jdk-alpine",
            'docker_runtime_image': f"eclipse-temurin:{java_version}-jre-alpine",
            'docker_port': self._get_framework_port(detection_result.get('framework')),
            'matrix': {
                'java_version': [java_version]
            }
        })

        return context

    def _get_framework_port(self, framework: str) -> int:
        """Get default port for Java framework"""
        ports = {
            'spring-boot': 8080,
            'quarkus': 8080,
            'micronaut': 8080,
        }
        return ports.get(framework, 8080)
