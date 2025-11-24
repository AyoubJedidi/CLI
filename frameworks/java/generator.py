"""
Generic Java Project Generator (Fallback)
"""
from pathlib import Path
from typing import Dict, Any
from core.base_generator import BaseGenerator


class JavaGenerator(BaseGenerator):
    """Generic generator for Java projects"""

    def __init__(self):
        super().__init__('java')

    def generate(self, detection_result: Dict, output_dir: Path) -> Dict:
        """Generate basic CI/CD files for Java project"""
        output_path = Path(output_dir)
        project_path = Path(detection_result.get('project_path', output_dir))

        context = self.add_base_context(detection_result, project_path)
        context.update({
            'java_version': '17',
            'docker_port': 8080
        })

        print(f"\n⚠️  Generic Java project detected (no build tool)")
        print(f"   Consider adding Maven (pom.xml) or Gradle (build.gradle)")

        return {'context': context, 'generated_files': {}}