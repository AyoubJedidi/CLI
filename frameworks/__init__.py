# frameworks/__init__.py
from .python import PythonDetector, PythonGenerator
from .node import NodeDetector, NodeGenerator

AVAILABLE_FRAMEWORKS = {
    'python': {
        'detector': PythonDetector,
        'generator': PythonGenerator
    },
    'node': {
        'detector': NodeDetector,
        'generator': NodeGenerator
    }
}

__all__ = ['AVAILABLE_FRAMEWORKS', 'PythonDetector', 'PythonGenerator', 'NodeDetector', 'NodeGenerator']