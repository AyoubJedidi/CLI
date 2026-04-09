"""
Maven Project Detector
Detects Maven-based Java projects
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict
from core.base_detector import BaseDetector


class MavenDetector(BaseDetector):
    """Detector for Maven projects"""

    def detect(self) -> Optional[Dict]:
        """Detect Maven project configuration"""
        # Must have pom.xml
        if not self.file_exists('pom.xml'):
            return None

        return {
            "language": "java",
            "build_tool": "maven",
            "framework": self._detect_framework(),
            "java_version": self._detect_java_version(),
            "test_framework": self._detect_test_framework(),
            "is_multi_module": self._is_multi_module(),
            "packaging": self._detect_packaging(),
        }

    def _detect_java_version(self) -> str:
        """Detect Java version from pom.xml"""
        pom_content = self.read_file('pom.xml')
        if not pom_content:
            return '17'

        try:
            root = ET.fromstring(pom_content)
            ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}

            # Look for properties
            properties = root.find('.//maven:properties', ns)
            if properties is not None:
                for prop in ['maven.compiler.source', 'maven.compiler.target', 'java.version']:
                    elem = properties.find(f'maven:{prop}', ns)
                    if elem is not None and elem.text:
                        return elem.text.strip()

            # Fallback to regex
            version_match = re.search(r'<maven\.compiler\.source>(\d+)', pom_content)
            if version_match:
                return version_match.group(1)

            version_match = re.search(r'<java\.version>(\d+)', pom_content)
            if version_match:
                return version_match.group(1)

        except Exception:
            pass

        return '17'

    def _detect_framework(self) -> Optional[str]:
        """Detect Spring Boot, Quarkus, Micronaut, etc."""
        pom_content = self.read_file('pom.xml').lower()

        if 'spring-boot-starter' in pom_content:
            return 'spring-boot'
        elif 'quarkus' in pom_content:
            return 'quarkus'
        elif 'micronaut' in pom_content:
            return 'micronaut'
        elif 'jakarta.ee' in pom_content or 'javax.ee' in pom_content:
            return 'jakarta-ee'

        return None

    def _detect_test_framework(self) -> str:
        """Detect JUnit, TestNG"""
        pom_content = self.read_file('pom.xml').lower()

        if 'junit-jupiter' in pom_content or 'junit5' in pom_content:
            return 'junit5'
        elif 'junit' in pom_content:
            return 'junit4'
        elif 'testng' in pom_content:
            return 'testng'

        return 'junit5'

    def _is_multi_module(self) -> bool:
        """Check if this is a multi-module Maven project"""
        pom_content = self.read_file('pom.xml')
        return '<modules>' in pom_content and '<module>' in pom_content

    def _detect_packaging(self) -> str:
        """Detect packaging type (jar, war, pom)"""
        pom_content = self.read_file('pom.xml')

        match = re.search(r'<packaging>(\w+)</packaging>', pom_content)
        if match:
            return match.group(1)

        return 'jar'  # Default