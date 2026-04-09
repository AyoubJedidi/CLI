"""
.NET Project Detector
Detects .NET Core/.NET 5+/Framework projects
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, List
from core.base_detector import BaseDetector


class DotNetDetector(BaseDetector):
    """Detector for .NET projects"""

    def detect(self) -> Optional[Dict]:
        """Detect .NET project configuration"""
        # Must have .csproj or .sln files
        csproj_files = list(self.project_path.rglob('*.csproj'))
        sln_files = list(self.project_path.rglob('*.sln'))

        if not csproj_files and not sln_files:
            return None

        # Analyze first .csproj file
        project_file = csproj_files[0] if csproj_files else None

        return {
            "language": "dotnet",
            "framework": self._detect_framework(project_file),
            "dotnet_version": self._detect_dotnet_version(project_file),
            "project_type": self._detect_project_type(project_file),
            "test_framework": self._detect_test_framework(),
            "has_solution": bool(sln_files),
            "is_web_app": self._is_web_app(project_file),
        }

    def _detect_dotnet_version(self, project_file: Optional[Path]) -> str:
        """Detect .NET version from .csproj"""
        if not project_file or not project_file.exists():
            return '8.0'

        try:
            content = project_file.read_text()

            # Look for TargetFramework
            match = re.search(r'<TargetFramework>net(\d+\.\d+)</TargetFramework>', content)
            if match:
                return match.group(1)

            # Look for net8.0, net7.0 format
            match = re.search(r'<TargetFramework>net(\d)\.(\d+)</TargetFramework>', content)
            if match:
                return f"{match.group(1)}.{match.group(2)}"

            # Look for older format netcoreapp3.1
            match = re.search(r'<TargetFramework>netcoreapp(\d+\.\d+)</TargetFramework>', content)
            if match:
                return match.group(1)

        except Exception:
            pass

        return '8.0'  # Default to .NET 8 (LTS)

    def _detect_framework(self, project_file: Optional[Path]) -> Optional[str]:
        """Detect ASP.NET Core, Blazor, etc."""
        if not project_file or not project_file.exists():
            return None

        try:
            content = project_file.read_text().lower()

            if 'microsoft.aspnetcore.blazor' in content or 'microsoft.aspnetcore.components' in content:
                if 'webassembly' in content:
                    return 'blazor-wasm'
                else:
                    return 'blazor-server'
            elif 'microsoft.aspnetcore' in content:
                return 'aspnetcore'
            elif 'microsoft.net.sdk.web' in content:
                return 'aspnetcore'
            elif 'microsoft.entityframeworkcore' in content:
                return 'efcore'

        except Exception:
            pass

        return None

    def _detect_project_type(self, project_file: Optional[Path]) -> str:
        """Detect project type (Web, Console, Library, etc.)"""
        if not project_file or not project_file.exists():
            return 'console'

        try:
            content = project_file.read_text()

            # Check SDK type
            if 'Microsoft.NET.Sdk.Web' in content:
                return 'web'
            elif 'Microsoft.NET.Sdk.Worker' in content:
                return 'worker'
            elif '<OutputType>Exe</OutputType>' in content:
                return 'console'
            elif '<OutputType>Library</OutputType>' in content:
                return 'library'

        except Exception:
            pass

        return 'console'

    def _detect_test_framework(self) -> str:
        """Detect xUnit, NUnit, MSTest"""
        csproj_files = list(self.project_path.rglob('*.csproj'))

        for csproj in csproj_files:
            try:
                content = csproj.read_text().lower()

                if 'xunit' in content:
                    return 'xunit'
                elif 'nunit' in content:
                    return 'nunit'
                elif 'mstest' in content:
                    return 'mstest'

            except Exception:
                continue

        return 'xunit'  # Default

    def _is_web_app(self, project_file: Optional[Path]) -> bool:
        """Check if this is a web application"""
        if not project_file or not project_file.exists():
            return False

        try:
            content = project_file.read_text()
            return (
                    'Microsoft.NET.Sdk.Web' in content or
                    'Microsoft.AspNetCore' in content or
                    '<Project Sdk="Microsoft.NET.Sdk.Web">' in content
            )
        except Exception:
            return False