"""
Generic Java Project Detector (Fallback)
Used when Maven or Gradle specific detection doesn't match
"""
from pathlib import Path
from typing import Optional, Dict
from core.base_detector import BaseDetector


class JavaDetector(BaseDetector):
    """Generic detector for Java projects"""

    def detect(self) -> Optional[Dict]:
        """Detect generic Java project"""
        # Only detect if has .java files but no build tool
        if not self.has_files_with_extension('java'):
            return None

        # If Maven or Gradle files exist, let their detectors handle it
        if self.file_exists('pom.xml') or self.file_exists('build.gradle') or self.file_exists('build.gradle.kts'):
            return None

        return {
            "language": "java",
            "build_tool": "none",
            "framework": None,
            "java_version": '17',
            "test_framework": 'junit5',
        }