#!/usr/bin/env python3
"""
Test workflow for current project structure
Run from project root: python test_workflow.py
"""

import json
import sys
from pathlib import Path

print("=" * 70)
print("CI/CD FRAMEWORK - WORKFLOW TEST")
print("=" * 70)

# ============================================================================
# STEP 0: SETUP
# ============================================================================
print("\n⚙️  STEP 0: CHECKING SETUP...")
print("-" * 70)

# Check if we're in the right directory
project_root = Path(__file__).parent
cli_dir = project_root / "cli"
templates_dir = project_root / "templates"

print(f"Project root: {project_root}")
print(f"CLI directory: {cli_dir}")
print(f"Templates directory: {templates_dir}")

if not cli_dir.exists():
    print("✗ cli/ directory not found!")
    sys.exit(1)
print("✓ cli/ directory exists")

if not templates_dir.exists():
    print("✗ templates/ directory not found!")
    sys.exit(1)
print("✓ templates/ directory exists")

# Check for required files
required_files = [
    cli_dir / "detector.py",
    cli_dir / "generator.py",
    templates_dir / "Jenkinsfile.j2",
    templates_dir / "Dockerfile.j2",
]

missing_files = [f for f in required_files if not f.exists()]
if missing_files:
    print("\n✗ Missing required files:")
    for f in missing_files:
        print(f"  - {f}")
    sys.exit(1)

print("✓ All required files present")

# Add cli to path
sys.path.insert(0, str(project_root))

# ============================================================================
# STEP 1: CREATE TEST PROJECT
# ============================================================================
print("\n\n📁 STEP 1: CREATING TEST PROJECT...")
print("-" * 70)

test_project_path = Path("/tmp/test-flask-app")
test_project_path.mkdir(exist_ok=True)

# Create test project structure
(test_project_path / "app").mkdir(exist_ok=True)
(test_project_path / "tests").mkdir(exist_ok=True)

# Create __init__.py
(test_project_path / "app" / "__init__.py").write_text("")

# Create main.py
(test_project_path / "app" / "main.py").write_text('''from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run()
''')

# Create test file
(test_project_path / "tests" / "test_main.py").write_text('''import pytest
from app.main import app

def test_hello():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
''')

# Create requirements.txt
(test_project_path / "requirements.txt").write_text('''flask==2.3.0
requests==2.31.0
''')

# Create requirements-dev.txt
(test_project_path / "requirements-dev.txt").write_text('''pytest==7.4.0
black==23.7.0
flake8==6.0.0
pytest-cov==4.1.0
''')

# Create .python-version
(test_project_path / ".python-version").write_text('3.11\n')

print(f"✓ Created test project at: {test_project_path}")
print("\nProject structure:")
print("  app/")
print("    __init__.py")
print("    main.py")
print("  tests/")
print("    test_main.py")
print("  requirements.txt")
print("  requirements-dev.txt")
print("  .python-version")

# ============================================================================
# STEP 2: DETECTION
# ============================================================================
print("\n\n🔍 STEP 2: DETECTING PROJECT CONFIGURATION...")
print("-" * 70)

try:
    from core.detector import ProjectDetector

    print("✓ Imported PythonDetector")
except ImportError as e:
    print(f"✗ Failed to import detector: {e}")
    print("\nMake sure cli/detector.py exists and has PythonDetector class")
    sys.exit(1)

print(f"\nAnalyzing: {test_project_path}")

detector = ProjectDetector(str(test_project_path))
detection_result = detector.detect()

if not detection_result:
    print("✗ Detection returned None - check detector.py")
    sys.exit(1)

print("\n✓ Detection complete!")
print("\n📋 Detected Configuration:")
print(json.dumps(detection_result, indent=2))

# ============================================================================
# STEP 3: GENERATION
# ============================================================================
print("\n\n📝 STEP 3: GENERATING PIPELINE FILES...")
print("-" * 70)

try:
    from core.generator import ProjectGenerator

    print("✓ Imported PythonGenerator")
except ImportError as e:
    print(f"✗ Failed to import generator: {e}")
    print("\nMake sure cli/generator.py exists and has PythonGenerator class")
    sys.exit(1)

# Output directory
output_dir = test_project_path / "generated"
output_dir.mkdir(exist_ok=True)

print(f"Output directory: {output_dir}")

# Add project_path to detection result
detection_result['project_path'] = str(test_project_path)

try:
    generator = ProjectGenerator(str(templates_dir))
    result = generator.generate(detection_result, str(output_dir))

    print("\n✅ Generation successful!")

except Exception as e:
    print(f"\n✗ Generation failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 4: PREVIEW RESULTS
# ============================================================================
print("\n\n👀 STEP 4: PREVIEW GENERATED FILES...")
print("-" * 70)

for file_type, file_path in result['generated_files'].items():
    print(f"\n--- {file_type.upper()} ---")
    path = Path(file_path)
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')[:15]  # First 15 lines
        for i, line in enumerate(lines, 1):
            print(f"{i:2d} | {line}")
        if len(content.split('\n')) > 15:
            print(f"... ({len(content.split('\n')) - 15} more lines)")
    else:
        print(f"✗ File not found: {path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\n" + "=" * 70)
print("✅ WORKFLOW TEST COMPLETED!")
print("=" * 70)
print(f"\nGenerated files:")
for file_type, file_path in result['generated_files'].items():
    print(f"  ✓ {file_type}: {file_path}")

print(f"\n📂 Check full output at: {output_dir}")
print("\nNext steps:")
print("  1. Review generated Jenkinsfile")
print("  2. Review generated Dockerfile")
print("  3. Test Docker build: cd /tmp/test-flask-app && docker build -f generated/Dockerfile .")