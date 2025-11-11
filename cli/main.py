# python
from typing import Optional
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .detector import ProjectDetector  # Changed from ProjectDetector
from .generator import ProjectGenerator

app = typer.Typer()
console = Console()


@app.command()
def init(
        path: Path = typer.Argument(Path("."), help="Project Path"),
        project_type: Optional[str] = typer.Option(None, "--type", help="Force Project Type"),
):
    console.print("Detecting project")

    # Initialize detector
    detector = ProjectDetector(path)  # Changed class name
    result = detector.detect()

    # Check if detection failed
    if result is None:
        console.print("[red]✗ No Python project detected![/red]")
        return

    # Add project path to result
    result['project_path'] = str(path)

    # Display detection results
    table = Table(title="Detection Results")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Use correct keys from detector (lowercase)
    table.add_row("Language", result.get("language", "N/A"))
    table.add_row("Framework", result.get("framework") or "N/A")
    table.add_row("Python Version", result.get("python_version", "N/A"))
    table.add_row("Package Manager", result.get("package_manager", "N/A"))
    table.add_row("Test Framework", result.get("test_framework", "N/A"))

    console.print(table)

    # Generate pipeline files
    console.print("\n[bold]Generating pipeline files...[/bold]")
    templates_dir = Path(__file__).parent.parent / "templates"
    generator = ProjectGenerator(templates_dir)

    try:
        files = generator.generate(result, path)
        console.print("\n[green]✅ Generation successful![/green]")
        console.print(f"\n[bold]Generated files:[/bold]")
        for file_type, file_path in files['generated_files'].items():
            console.print(f"  ✓ {file_type}: {file_path}")
        return files
    except Exception as e:
        console.print(f"[red]✗ Generation failed: {e}[/red]")
        raise


@app.command()
def detect(path: Path = typer.Argument(Path("."), help="Project Path")):
    """Detect project configuration without generating files"""
    detector = ProjectDetector(path)  # Changed class name
    result = detector.detect()

    if result is None:
        console.print("[red]✗ No Python project detected![/red]")
        return

    result['project_path'] = str(path)
    console.print_json(data=result)


if __name__ == "__main__":
    app()