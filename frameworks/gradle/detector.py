"""
Gradle Project Detector
Detects Gradle-based Java projects
"""
import re
from pathlib import Path
from typing import Optional, Dict
from core.base_detector import BaseDetector


class GradleDetector(BaseDetector):
    """Detector for Gradle projects"""

    def detect(self) -> Optional[Dict]:
        """Detect Gradle project configuration"""
        # Must have build.gradle or build.gradle.kts
        if not (self.file_exists('build.gradle') or self.file_exists('build.gradle.kts')):
            return None

        return {
            "language": "java",
            "build_tool": "gradle",
            "framework": self._detect_framework(),
            "java_version": self._detect_java_version(),
            "test_framework": self._detect_test_framework(),
            "uses_kotlin_dsl": self.file_exists('build.gradle.kts'),
            "is_multi_project": self._is_multi_project(),
        "packaging": self._detect_packaging(),  # ← ADD THIS

        }

    def _detect_java_version(self) -> str:
        """Detect Java version from build.gradle"""
        gradle_content = self.read_file('build.gradle')
        if not gradle_content:
            gradle_content = self.read_file('build.gradle.kts')

        if not gradle_content:
            return '17'

        # Look for sourceCompatibility
        version_match = re.search(r'sourceCompatibility\s*=\s*["\']?(\d+)', gradle_content)
        if version_match:
            return version_match.group(1)

        # Look for JavaVersion
        version_match = re.search(r'JavaVersion\.VERSION_(\d+)', gradle_content)
        if version_match:
            return version_match.group(1)

        # Look for toolchain
        version_match = re.search(r'languageVersion\.set\(JavaLanguageVersion\.of\((\d+)\)\)', gradle_content)
        if version_match:
            return version_match.group(1)

        return '17'

    def _detect_framework(self) -> Optional[str]:
        """Detect Spring Boot, Quarkus, Micronaut, etc."""
        gradle_content = self.read_file('build.gradle').lower()
        if not gradle_content:
            gradle_content = self.read_file('build.gradle.kts').lower()

        if 'spring-boot' in gradle_content or 'org.springframework.boot' in gradle_content:
            return 'spring-boot'
        elif 'quarkus' in gradle_content:
            return 'quarkus'
        elif 'micronaut' in gradle_content:
            return 'micronaut'

        return None

    def _detect_test_framework(self) -> str:
        """Detect JUnit, TestNG, Spock"""
        gradle_content = self.read_file('build.gradle').lower()
        if not gradle_content:
            gradle_content = self.read_file('build.gradle.kts').lower()

        if 'junit-jupiter' in gradle_content or "'junit5'" in gradle_content:
            return 'junit5'
        elif 'junit' in gradle_content:
            return 'junit4'
        elif 'testng' in gradle_content:
            return 'testng'
        elif 'spock' in gradle_content:
            return 'spock'

        return 'junit5'

    def _is_multi_project(self) -> bool:
        """Check if this is a multi-project Gradle build"""
        return self.file_exists('settings.gradle') or self.file_exists('settings.gradle.kts')

    def _detect_packaging(self) -> str:
        """Detect packaging type (jar, war)"""
        gradle_content = self.read_file('build.gradle')
        if not gradle_content:
            gradle_content = self.read_file('build.gradle.kts')

        if not gradle_content:
            return 'jar'

        # Check for war plugin
        if "id 'war'" in gradle_content or 'id("war")' in gradle_content:
            return 'war'

        # Check for apply plugin
        if "apply plugin: 'war'" in gradle_content or 'apply plugin: "war"' in gradle_content:
            return 'war'

        # Check for bootWar task (Spring Boot)
        if 'bootWar' in gradle_content:
            return 'war'

        return 'jar'  # Default