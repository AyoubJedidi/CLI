# frameworks/node/detector.py
import json
from pathlib import Path
from typing import Optional, Dict
from core.base_detector import BaseDetector


class NodeDetector(BaseDetector):
    """Detector for Node.js projects"""

    def detect(self) -> Optional[Dict]:
        """Detect Node.js project configuration"""
        if not self.file_exists('package.json'):
            return None

        return {
            "language": "node",
            "framework": self._detect_framework(),
            "node_version": self._detect_node_version(),
            "package_manager": self._detect_package_manager(),
            "test_framework": self._detect_test_framework(),
        }

    def _detect_node_version(self) -> str:
        """Detect Node version from .nvmrc or package.json"""
        # Check .nvmrc
        if self.file_exists('.nvmrc'):
            version = self.read_file('.nvmrc').strip()
            return version.replace('v', '')

        # Check package.json engines
        pkg = self._read_package_json()
        if pkg and 'engines' in pkg and 'node' in pkg['engines']:
            version = pkg['engines']['node']
            # Extract first number from ">=18.0.0" or "^20"
            import re
            match = re.search(r'(\d+)', version)
            if match:
                return match.group(1)

        return '20'  # Default LTS

    def _detect_framework(self) -> Optional[str]:
        """Detect Express, NestJS, Next.js, etc."""
        pkg = self._read_package_json()
        if not pkg:
            return None

        deps = self._get_all_dependencies(pkg)

        if 'next' in deps:
            return 'nextjs'
        elif '@nestjs/core' in deps:
            return 'nestjs'
        elif 'express' in deps:
            return 'express'
        elif 'fastify' in deps:
            return 'fastify'
        elif 'koa' in deps:
            return 'koa'

        return None

    def _detect_package_manager(self) -> str:
        """Detect npm, yarn, or pnpm"""
        if self.file_exists('pnpm-lock.yaml'):
            return 'pnpm'
        elif self.file_exists('yarn.lock'):
            return 'yarn'
        elif self.file_exists('package-lock.json'):
            return 'npm'
        return 'npm'

    def _detect_test_framework(self) -> str:
        """Detect Jest, Mocha, etc."""
        pkg = self._read_package_json()
        if not pkg:
            return 'jest'

        deps = self._get_all_dependencies(pkg)

        if 'jest' in deps:
            return 'jest'
        elif 'mocha' in deps:
            return 'mocha'
        elif 'vitest' in deps:
            return 'vitest'

        return 'jest'

    def _read_package_json(self) -> Optional[Dict]:
        """Read and parse package.json"""
        content = self.read_file('package.json')
        if not content:
            return None

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

    def _get_all_dependencies(self, pkg: Dict) -> set:
        """Get all dependencies from package.json"""
        deps = set()

        for key in ['dependencies', 'devDependencies', 'peerDependencies']:
            if key in pkg:
                deps.update(pkg[key].keys())

        return deps