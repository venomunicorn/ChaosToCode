import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.ai import OllamaClient, SYSTEM_PROMPT, OllamaClientError
from src.parser import stream_parse_ollama_output, ParsingError
from src.ollama_manager import OllamaManager
import shutil
import sys

app = typer.Typer()
console = Console()

@app.command()
def organize(
    source_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to unstructured source text file."),
    model: str = typer.Option("qwen2.5:7b", help="Ollama model name (e.g., qwen2.5:7b, qwen3:8b)"),
    output_dir: Path = typer.Option("output", file_okay=False, help="Directory to write extracted files."),
    skip_setup: bool = typer.Option(False, help="Skip automatic Ollama setup (use if already configured)")
):
    """
    Organize a massive text dump into proper folder/file structure using a local Ollama model.
    """
    # Auto-setup Ollama unless explicitly skipped
    if not skip_setup:
        console.print("[cyan]Checking Ollama setup...[/cyan]")
        manager = OllamaManager()
        
        # Check if Ollama is running, start if needed
        if not manager.is_ollama_running():
            console.print("[yellow]Starting Ollama service...[/yellow]")
            if not manager.start_ollama():
                console.print("[red]Failed to start Ollama. Please start it manually with 'ollama serve'[/red]")
                raise typer.Exit(1)
        else:
            console.print("[green]✓[/green] Ollama is running")
        
        # Check if model is available, download if needed
        if not manager.is_model_available(model):
            console.print(f"[yellow]Downloading model '{model}'...[/yellow]")
            if not manager.download_model(model):
                console.print(f"[red]Failed to download model '{model}'. Please download it manually with 'ollama pull {model}'[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"[green]✓[/green] Model '{model}' is available")
        
        console.print("[green]Setup complete! Starting file organization...[/green]\n")
    
    # Read source file
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            src_text = f.read()
    except OSError as e:
        console.print(f"[red]Error reading input: {e}[/red]")
        raise typer.Exit(1)

    # Process with Ollama
    client = OllamaClient(model=model)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
        t = progress.add_task("Contacting Ollama and parsing files...", start=False)
        try:
            stream = client.stream(src_text, system_prompt=SYSTEM_PROMPT)
            stream_parse_ollama_output(stream, output_dir=output_dir)
            progress.update(t, description="[green]All files organized!")
        except OllamaClientError as err:
            console.print(f"[red]Ollama connection error: {err}[/red]")
            raise typer.Exit(2)
        except ParsingError as e:
            console.print(f"[red]Stream parser error: {e}[/red]")
            raise typer.Exit(3)
        except Exception as ex:
            console.print(f"[red]Unexpected error: {ex}[/red]")
            raise typer.Exit(4)

@app.command()
def clean(output_dir: Path = typer.Option("output", file_okay=False, help="Output directory to wipe.")):
    """
    Wipes the output directory completely.
    """
    try:
        if output_dir.exists() and output_dir.is_dir():
            shutil.rmtree(output_dir)
            console.print(f"[yellow]Directory '{output_dir}' wiped.[/yellow]")
        else:
            console.print(f"[grey]No output directory to clean.[/grey]")
    except Exception as e:
        console.print(f"[red]Failed to remove output directory: {e}[/red]")
        raise typer.Exit(5)

@app.command()
def setup(
    model: str = typer.Option("qwen2.5:7b", help="Ollama model name to download and prepare")
):
    """
    Setup Ollama service and download the required model.
    """
    manager = OllamaManager()
    if manager.setup(model_name=model):
        console.print("[green]✓ Setup completed successfully![/green]")
    else:
        console.print("[red]Setup failed. Check the error messages above.[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
