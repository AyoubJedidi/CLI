"""
Base Generator class for all framework generators
Provides common utilities for template rendering and file generation
"""
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import Dict, Any


class BaseGenerator:
    """Base class for framework-specific generators"""

    def __init__(self, framework_name: str):
        """
        Initialize generator for a specific framework

        Args:
            framework_name: Name of the framework (e.g., 'python', 'node')
        """
        self.framework_name = framework_name

        # Build path to framework templates
        # Assumes structure: frameworks/{framework_name}/templates/
        base_path = Path(__file__).parent.parent  # Go up from core/ to project root
        self.templates_dir = base_path / 'frameworks' / framework_name / 'templates'

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(self, detection_result: Dict, output_dir: Path) -> Dict:
        """
        Main generation method - must be overridden by child classes

        Args:
            detection_result: Dict from detector with project info
            output_dir: Where to write generated files

        Returns:
            Dict with generated file paths
        """
        raise NotImplementedError("Subclasses must implement generate()")

    # ============ Shared Template Rendering ============

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with given context

        Args:
            template_name: Name of template file (e.g., 'Jenkinsfile.j2')
            context: Dict with template variables

        Returns:
            Rendered template content as string
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(context)
        except Exception as e:
            raise Exception(f"Failed to render template {template_name}: {e}")

    # ============ Shared File Writing ============

    def write_file(self, content: str, output_path: Path, verbose: bool = True) -> Path:
        """
        Write content to file

        Args:
            content: String content to write
            output_path: Path where to write file
            verbose: Print success message

        Returns:
            Path to written file
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content)

            if verbose:
                print(f"   ✓ Generated: {output_path.name}")

            return output_path
        except Exception as e:
            raise Exception(f"Failed to write file {output_path}: {e}")

    def generate_file_from_template(
            self,
            template_name: str,
            context: Dict[str, Any],
            output_path: Path,
            verbose: bool = True
    ) -> Path:
        """
        Convenience method: render template and write to file

        Args:
            template_name: Template file name
            context: Template variables
            output_path: Where to write
            verbose: Print messages

        Returns:
            Path to generated file
        """
        content = self.render_template(template_name, context)
        return self.write_file(content, output_path, verbose)

    # ============ Shared Context Building ============

    def add_base_context(self, detection_result: Dict, project_path: Path) -> Dict[str, Any]:
        """
        Add common context fields that all frameworks need

        Args:
            detection_result: Detection results
            project_path: Project directory path

        Returns:
            Dict with base context fields
        """
        project_name = project_path.name if project_path.name else 'my-app'

        return {
            'project_name': project_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'language': detection_result.get('language'),
            'framework': detection_result.get('framework'),
        }

    # ============ Shared File Structure Detection ============

    def detect_app_module(self, project_path: Path, exclude_dirs: list = None) -> str:
        """
        Detect the main application module name
        Common patterns: app/, src/, project_name/

        Args:
            project_path: Project directory
            exclude_dirs: Directories to skip (defaults to common test/docs dirs)

        Returns:
            Main module name
        """
        if exclude_dirs is None:
            exclude_dirs = ['tests', 'test', 'docs', 'scripts', 'venv', '.venv', 'templates', 'node_modules']

        # Check common directories first
        for candidate in ['app', 'src', 'cli', project_path.name]:
            candidate_path = project_path / candidate
            if candidate_path.is_dir() and self._is_valid_module(candidate_path):
                return candidate

        # Find any directory with module indicators
        try:
            for item in project_path.iterdir():
                if item.is_dir() and item.name not in exclude_dirs:
                    if self._is_valid_module(item):
                        return item.name
        except Exception:
            pass

        return 'app'  # Default fallback

    def _is_valid_module(self, path: Path) -> bool:
        """
        Check if directory is a valid module
        Override in child classes for language-specific checks
        """
        return (path / '__init__.py').exists()  # Python default