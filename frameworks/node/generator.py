# frameworks/node/generator.py
from pathlib import Path
from typing import Dict, Any
from core.base_generator import BaseGenerator


class NodeGenerator(BaseGenerator):
    """Generator for Node.js projects"""

    def __init__(self):
        super().__init__('node')

    def generate(self, detection_result: Dict, output_dir: Path) -> Dict:
        """Generate CI/CD files for Node.js project"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        project_path = Path(detection_result.get('project_path', output_dir))
        context = self._prepare_context(detection_result, project_path)

        print(f"\n📦 Generating files for: {context['project_name']}")
        print(f"   Node: {context['node_version']}")
        print(f"   Framework: {context['framework'] or 'N/A'}")
        print(f"   Package Manager: {context['package_manager']}")

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
        """Prepare template context"""
        context = self.add_base_context(detection_result, project_path)

        context.update({
            'node_version': detection_result.get('node_version', '20'),
            'package_manager': detection_result.get('package_manager', 'npm'),
            'test_framework': detection_result.get('test_framework', 'jest'),
            'docker_base_image': f"node:{detection_result.get('node_version', '20')}-alpine",
            'docker_port': self._get_framework_port(detection_result.get('framework')),
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