"""Frameworks module"""
from .python import PythonDetector, PythonGenerator

AVAILABLE_FRAMEWORKS = {
    'python': {
        'detector': PythonDetector,
        'generator': PythonGenerator
    }
}

__all__ = ['AVAILABLE_FRAMEWORKS', 'PythonDetector', 'PythonGenerator']