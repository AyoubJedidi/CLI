"""
CLI for cicd-framework tool
Auto-detects project framework and generates CI/CD files
"""
from typing import Optional, List
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from frameworks import AVAILABLE_FRAMEWORKS

app = typer.Typer(
    help="CI/CD Framework Generator - Auto-detect and generate pipeline files",
    add_completion=False
)
console = Console()


@app.command()
def init(
    path: Path = typer.Argument(
        Path("."),
        help="Project path to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True
    ),
    framework: Optional[str] = typer.Option(
        None,
        "--framework",
        "-f",
        help="Force specific framework (python, node, java, etc.)"
    ),
    platforms: str = typer.Option(
        "jenkins",
        "--platforms",
        "-p",
        help="Comma-separated CI/CD platforms to generate (jenkins,gitlab,github)"
    ),
):
    """
    Initialize CI/CD pipeline for a project.

    Auto-detects project framework and generates pipeline files.

    Examples:

        # Generate Jenkins pipeline (default)
        $ cicd-framework init

        # Generate GitLab CI only
        $ cicd-framework init --platforms gitlab

        # Generate all platforms
        $ cicd-framework init --platforms jenkins,gitlab,github

        # Force Python framework with multiple platforms
        $ cicd-framework init --framework python --platforms gitlab,github
    """
    console.print("🔍 Detecting project framework...\n")

    project_path = Path(path).resolve()

    # Parse and validate platforms
    requested_platforms = [p.strip().lower() for p in platforms.split(',')]
    valid_platforms = ['jenkins', 'gitlab', 'github']
    invalid = [p for p in requested_platforms if p not in valid_platforms]

    if invalid:
        console.print(f"[red]✗ Invalid platforms: {', '.join(invalid)}[/red]")
        console.print(f"[yellow]Valid platforms: {', '.join(valid_platforms)}[/yellow]")
        console.print("\n[dim]Tip: Use comma-separated values like --platforms jenkins,gitlab,github[/dim]")
        raise typer.Exit(code=1)

    # If user specified framework, use only that
    if framework:
        if framework not in AVAILABLE_FRAMEWORKS:
            console.print(f"[red]✗ Unknown framework: {framework}[/red]")
            console.print(f"[yellow]Available frameworks: {', '.join(AVAILABLE_FRAMEWORKS.keys())}[/yellow]")
            raise typer.Exit(code=1)

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

        console.print(f"   Trying {fw_name}...", style="dim")

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
        console.print(f"[yellow]Supported frameworks: {', '.join(AVAILABLE_FRAMEWORKS.keys())}[/yellow]")
        console.print("\n[dim]Tip: Use --framework to force a specific framework[/dim]")
        raise typer.Exit(code=1)

    # Add project path to result
    detection_result['project_path'] = str(project_path)

    # Display detection results
    console.print()
    table = Table(title="📊 Detection Results", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="cyan", no_wrap=True)
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
    elif detected_framework == 'node':
        table.add_row("Node Version", detection_result.get("node_version", "N/A"))
        table.add_row("Package Manager", detection_result.get("package_manager", "N/A"))
        if detection_result.get("framework"):
            table.add_row("Framework", detection_result.get("framework"))

    console.print(table)
    console.print()

    # Display platforms to generate
    platforms_display = ", ".join([f"[cyan]{p}[/cyan]" for p in requested_platforms])
    console.print(f"[bold]📦 Generating CI/CD files for: {platforms_display}[/bold]\n")

    # Get the appropriate generator
    GeneratorClass = AVAILABLE_FRAMEWORKS[detected_framework]['generator']
    generator = GeneratorClass()

    try:
        files = generator.generate(detection_result, project_path, requested_platforms)

        console.print("[green]✅ Generation successful![/green]\n")

        # Display generated files
        files_table = Table(title="📄 Generated Files", show_header=True, header_style="bold green")
        files_table.add_column("Platform", style="cyan", no_wrap=True)
        files_table.add_column("File Path", style="yellow")

        for platform, file_path in files['generated_files'].items():
            # Make path relative to project for cleaner display
            try:
                rel_path = Path(file_path).relative_to(project_path)
                files_table.add_row(platform.upper(), str(rel_path))
            except ValueError:
                files_table.add_row(platform.upper(), str(file_path))

        console.print(files_table)
        console.print()

        return files
    except Exception as e:
        console.print(f"[red]✗ Generation failed: {e}[/red]")
        import traceback
        console.print("\n[dim]Stack trace:[/dim]")
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def detect(
    path: Path = typer.Argument(
        Path("."),
        help="Project path to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True
    ),
    framework: Optional[str] = typer.Option(
        None,
        "--framework",
        "-f",
        help="Force specific framework detection"
    ),
):
    """
    Detect project configuration without generating files.

    Useful for testing framework detection.

    Examples:

        # Auto-detect framework
        $ cicd-framework detect

        # Force Python detection
        $ cicd-framework detect --framework python
    """
    project_path = Path(path).resolve()

    console.print("🔍 Detecting project framework...\n")

    # If user specified framework, use only that
    if framework:
        if framework not in AVAILABLE_FRAMEWORKS:
            console.print(f"[red]✗ Unknown framework: {framework}[/red]")
            console.print(f"[yellow]Available frameworks: {', '.join(AVAILABLE_FRAMEWORKS.keys())}[/yellow]")
            raise typer.Exit(code=1)
        frameworks_to_try = [framework]
    else:
        frameworks_to_try = list(AVAILABLE_FRAMEWORKS.keys())

    # Try each framework
    for fw_name in frameworks_to_try:
        fw_config = AVAILABLE_FRAMEWORKS[fw_name]
        DetectorClass = fw_config['detector']

        console.print(f"   Trying {fw_name}...", style="dim")
        detector = DetectorClass(project_path)
        result = detector.detect()

        if result is not None:
            result['project_path'] = str(project_path)
            result['detected_framework'] = fw_name
            console.print(f"\n[green]✓ Detected: {fw_name}[/green]\n")
            console.print_json(data=result)
            return result

    console.print("[red]✗ No supported framework detected![/red]")
    console.print(f"[yellow]Supported frameworks: {', '.join(AVAILABLE_FRAMEWORKS.keys())}[/yellow]")
    raise typer.Exit(code=1)


@app.command(name="list")
def list_frameworks():
    """
    List all supported frameworks and platforms.

    Shows available framework detectors and generators.
    """
    console.print("\n[bold cyan]🚀 CI/CD Framework Generator[/bold cyan]\n")

    # Frameworks table
    frameworks_table = Table(title="Supported Frameworks", show_header=True, header_style="bold cyan")
    frameworks_table.add_column("Framework", style="cyan", no_wrap=True)
    frameworks_table.add_column("Detector", style="yellow")
    frameworks_table.add_column("Generator", style="green")

    for fw_name, fw_config in AVAILABLE_FRAMEWORKS.items():
        frameworks_table.add_row(
            fw_name.upper(),
            fw_config['detector'].__name__,
            fw_config['generator'].__name__
        )

    console.print(frameworks_table)
    console.print()

    # Platforms table
    platforms_table = Table(title="Supported CI/CD Platforms", show_header=True, header_style="bold green")
    platforms_table.add_column("Platform", style="green", no_wrap=True)
    platforms_table.add_column("File Generated", style="yellow")
    platforms_table.add_column("Description", style="dim")

    platforms_table.add_row("Jenkins", "Jenkinsfile", "Declarative pipeline for Jenkins")
    platforms_table.add_row("GitLab CI", ".gitlab-ci.yml", "GitLab CI/CD configuration")
    platforms_table.add_row("GitHub Actions", ".github/workflows/ci.yml", "GitHub Actions workflow")

    console.print(platforms_table)
    console.print()


@app.command()
def version():
    """
    Show version information.
    """
    console.print("\n[bold cyan]CI/CD Framework Generator[/bold cyan]")
    console.print("[dim]Version:[/dim] [green]1.0.0[/green]")
    console.print("[dim]Author:[/dim] [yellow]Ayoub Jedidi[/yellow]")
    console.print()


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()