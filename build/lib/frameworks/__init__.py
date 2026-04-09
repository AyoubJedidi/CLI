"""
Frameworks module - Registry of all framework detectors and generators
"""
from .python import PythonDetector, PythonGenerator
from .node import NodeDetector, NodeGenerator
from .maven import MavenDetector, MavenGenerator
from .gradle import GradleDetector, GradleGenerator
from .java import JavaDetector, JavaGenerator
from .dotnet import DotNetDetector, DotNetGenerator

# Order matters! Specific frameworks before generic
AVAILABLE_FRAMEWORKS = {
    'python': {
        'detector': PythonDetector,
        'generator': PythonGenerator
    },
    'node': {
        'detector': NodeDetector,
        'generator': NodeGenerator
    },
    'maven': {
        'detector': MavenDetector,
        'generator': MavenGenerator
    },
    'gradle': {
        'detector': GradleDetector,
        'generator': GradleGenerator
    },
    'java': {
        'detector': JavaDetector,
        'generator': JavaGenerator
    },
    'dotnet': {
        'detector': DotNetDetector,
        'generator': DotNetGenerator
    }
}

__all__ = ['AVAILABLE_FRAMEWORKS']