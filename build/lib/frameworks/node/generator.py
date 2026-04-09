# frameworks/node/generator.py
from pathlib import Path
from typing import Dict, Any, List
from core.base_generator import BaseGenerator


class NodeGenerator(BaseGenerator):
    """Generator for Node.js projects"""

    def __init__(self):
        super().__init__('node')

    def get_platform_template_map(self) -> Dict[str, Dict[str, str]]:
        """Get platform-specific template mapping for Node.js"""
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
        Generate CI/CD files for Node.js project

        Args:
            detection_result: Detection results from NodeDetector
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
        print(f"\n🔧 Generating files for: {context['project_name']}")
        print(f"   Node: {context['node_version']}")
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

    def _generate_additional_files(self, context: Dict, output_path: Path, generated_files: Dict) -> None:
        """Generate additional files like Dockerfile, docker-compose, README"""
        try:
            # Generate Dockerfile
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
        """Prepare template context"""
        context = self.add_base_context(detection_result, project_path)
        node_version = detection_result.get('node_version', '20')
        context.update({
            'node_version': node_version,
            'package_manager': detection_result.get('package_manager', 'npm'),
            'test_framework': detection_result.get('test_framework', 'jest'),
            'docker_base_image': f"node:{node_version}-alpine",
            'docker_port': self._get_framework_port(detection_result.get('framework')),

            # Deployment configuration
            'deployment_type': detection_result.get('deployment_type', 'webapp'),
            'cloud_provider': detection_result.get('cloud_provider', 'local'),

            # Add matrix configuration for CI/CD
            'matrix': {
                'node_version': [node_version]
            }
        })

        return context

    def _get_framework_port(self, framework: str) -> int:
        """Get default port for Node framework"""
        ports = {
            'express': 3000,
            'nestjs': 3000,
            'nextjs': 3000,
            'fastify': 3000,
            'koa': 3000,
        }
        return ports.get(framework, 3000)
