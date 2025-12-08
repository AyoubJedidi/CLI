"""
.NET Project Generator
Generates CI/CD files for .NET projects
"""
from pathlib import Path
from typing import Dict, Any, List
from core.base_generator import BaseGenerator


class DotNetGenerator(BaseGenerator):
    """Generator for .NET projects"""

    def __init__(self):
        super().__init__('dotnet')

    def get_platform_template_map(self) -> Dict[str, Dict[str, str]]:
        """Get platform-specific template mapping for .NET"""
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
        Generate CI/CD files for .NET project

        Args:
            detection_result: Detection results from DotNetDetector
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
        print(f"   .NET: {context['dotnet_version']}")
        print(f"   Project Type: {context['project_type']}")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Web App: {context['is_web_app']}")
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
        """Prepare .NET-specific template context"""
        context = self.add_base_context(detection_result, project_path)

        dotnet_version = detection_result.get('dotnet_version', '8.0')
        project_type = detection_result.get('project_type', 'console')
        is_web_app = detection_result.get('is_web_app', False)

        context.update({
            'dotnet_version': dotnet_version,
            'project_type': project_type,
            'test_framework': detection_result.get('test_framework', 'xunit'),
            'has_solution': detection_result.get('has_solution', False),
            'is_web_app': is_web_app,
            'docker_base_image': f"mcr.microsoft.com/dotnet/sdk:{dotnet_version}",
            'docker_runtime_image': self._get_runtime_image(dotnet_version, is_web_app),
            'docker_port': self._get_framework_port(detection_result.get('framework')),
            'matrix': {
                'dotnet_version': [dotnet_version]
            }
        })

        return context

    def _get_runtime_image(self, dotnet_version: str, is_web_app: bool) -> str:
        """Get appropriate runtime image"""
        if is_web_app:
            return f"mcr.microsoft.com/dotnet/aspnet:{dotnet_version}"
        else:
            return f"mcr.microsoft.com/dotnet/runtime:{dotnet_version}"

    def _get_framework_port(self, framework: str) -> int:
        """Get default port for .NET framework"""
        ports = {
            'aspnetcore': 8080,
            'blazor-server': 8080,
            'blazor-wasm': 8080,
        }
        return ports.get(framework, 8080)
