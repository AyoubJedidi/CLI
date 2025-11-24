"""
.NET Project Generator
Generates CI/CD files for .NET projects
"""
from pathlib import Path
from typing import Dict, Any
from core.base_generator import BaseGenerator


class DotNetGenerator(BaseGenerator):
    """Generator for .NET projects"""

    def __init__(self):
        super().__init__('dotnet')

    def generate(self, detection_result: Dict, output_dir: Path) -> Dict:
        """Generate CI/CD files for .NET project"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        project_path = Path(detection_result.get('project_path', output_dir))
        context = self._prepare_context(detection_result, project_path)

        print(f"\n📦 Generating files for: {context['project_name']}")
        print(f"   .NET: {context['dotnet_version']}")
        print(f"   Project Type: {context['project_type']}")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Web App: {context['is_web_app']}")

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