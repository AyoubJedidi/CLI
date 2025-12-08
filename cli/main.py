"""
CLI for cicd-framework tool
Auto-detects project framework and generates CI/CD files
"""
from typing import Optional
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from frameworks import AVAILABLE_FRAMEWORKS

app = typer.Typer()
console = Console()


@app.command()
def init(
        path: Path = typer.Argument(Path("."), help="Project Path"),
        framework: Optional[str] = typer.Option(None, "--framework", help="Force specific framework"),
        platforms: Optional[str] = typer.Option("jenkins", "--platforms", help="Comma-separated platforms: jenkins,gitlab,github"),
):
    """
    Initialize CI/CD pipeline for a project
    Auto-detects framework or use --framework to specify
    """
    console.print(" Detecting project framework...")

    project_path = Path(path).resolve()

    requested_platforms = [p.strip().lower() for p in platforms.split(',')]
    valid_platforms = ['jenkins', 'gitlab', 'github']
    invalid = [p for p in requested_platforms if p not in valid_platforms]

    if invalid:
        console.print(f"[red]✗ Invalid platforms: {', '.join(invalid)}[/red]")
        console.print(f"Valid platforms: {', '.join(valid_platforms)}")
        return

    # If user specified framework, use only that
    if framework:
        if framework not in AVAILABLE_FRAMEWORKS:
            console.print(f"[red]✗ Unknown framework: {framework}[/red]")
            console.print(f"Available frameworks: {', '.join(AVAILABLE_FRAMEWORKS.keys())}")
            return

        frameworks_to_try = [framework]
    else:
        # Try all available frameworks
        frameworks_to_try = list(AVAILABLE_FRAMEWORKS.keys())

    # Try each framework detector
    detection_result = None
    detected_framework = None

    for fw_name in frameworks_to_try:
        fw_config = AVAILABLE_FRAMEWORKS[fw_name]
        DetectorClass = fw_config['detector']

        console.print(f"   Trying {fw_name}...")

        # Initialize detector and try detection
        detector = DetectorClass(project_path)
        result = detector.detect()

        if result is not None:
            detection_result = result
            detected_framework = fw_name
            console.print(f"[green]✓ Detected: {fw_name}[/green]")
            break

    # Check if detection failed
    if detection_result is None:
        console.print("[red]✗ No supported framework detected![/red]")
        console.print(f"Supported frameworks: {', '.join(AVAILABLE_FRAMEWORKS.keys())}")
        return

    # Add project path to result
    detection_result['project_path'] = str(project_path)

    # Display detection results
    table = Table(title="Detection Results")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Framework", detected_framework)
    table.add_row("Language", detection_result.get("language", "N/A"))

    # Add framework-specific details
    if detected_framework == 'python':
        table.add_row("Python Version", detection_result.get("python_version", "N/A"))
        table.add_row("Package Manager", detection_result.get("package_manager", "N/A"))
        table.add_row("Test Framework", detection_result.get("test_framework", "N/A"))
        if detection_result.get("framework"):
            table.add_row("Web Framework", detection_result.get("framework"))

    console.print(table)

    # Generate pipeline files
    console.print(f"\n[bold]Generating CI/CD files for: {', '.join(requested_platforms)}...[/bold]")

    # Get the appropriate generator
    GeneratorClass = AVAILABLE_FRAMEWORKS[detected_framework]['generator']
    generator = GeneratorClass()

    try:
        files = generator.generate(detection_result, project_path, requested_platforms)
        console.print("\n[green]  Generation successful![/green]")
        console.print(f"\n[bold]Generated files:[/bold]")
        for platform, file_info in files['generated_files'].items():
            console.print(f"  ✓ {platform}: {file_info}")
        return files
    except Exception as e:
        console.print(f"[red]✗ Generation failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise


@app.command()
def detect(
        path: Path = typer.Argument(Path("."), help="Project Path"),
        framework: Optional[str] = typer.Option(None, "--framework", help="Force specific framework"),
):
    """
    Detect project configuration without generating files
    """
    project_path = Path(path).resolve()

    console.print("🔍 Detecting project framework...")

    # If user specified framework, use only that
    if framework:
        if framework not in AVAILABLE_FRAMEWORKS:
            console.print(f"[red]✗ Unknown framework: {framework}[/red]")
            return
        frameworks_to_try = [framework]
    else:
        frameworks_to_try = list(AVAILABLE_FRAMEWORKS.keys())

    # Try each framework
    for fw_name in frameworks_to_try:
        fw_config = AVAILABLE_FRAMEWORKS[fw_name]
        DetectorClass = fw_config['detector']

        detector = DetectorClass(project_path)
        result = detector.detect()

        if result is not None:
            result['project_path'] = str(project_path)
            result['detected_framework'] = fw_name
            console.print(f"\n[green]✓ Detected: {fw_name}[/green]")
            console.print_json(data=result)
            return result

    console.print("[red]✗ No supported framework detected![/red]")
    return None


@app.command()
def list_frameworks():
    """
    List all supported frameworks
    """
    console.print("\n[bold]Supported Frameworks:[/bold]\n")

    table = Table()
    table.add_column("Framework", style="cyan")
    table.add_column("Detector", style="yellow")
    table.add_column("Generator", style="green")

    for fw_name, fw_config in AVAILABLE_FRAMEWORKS.items():
        table.add_row(
            fw_name,
            fw_config['detector'].__name__,
            fw_config['generator'].__name__
        )

    console.print(table)


if __name__ == "__main__":
    app()