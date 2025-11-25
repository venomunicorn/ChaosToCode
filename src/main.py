import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.ai import OllamaClient, SYSTEM_PROMPT, OllamaClientError
from src.parser import stream_parse_ollama_output, ParsingError
import shutil

app = typer.Typer()
console = Console()

@app.command()
def organize(
    source_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to unstructured source text file."),
    model: str = typer.Option("qwen2.5:7b", help="Ollama model name (e.g., qwen2.5:7b, qwen3:8b)"),
    output_dir: Path = typer.Option("output", file_okay=False, help="Directory to write extracted files.")
):
    """
    Organize a massive text dump into proper folder/file structure using a local Ollama model.
    """
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            src_text = f.read()
    except OSError as e:
        console.print(f"[red]Error reading input: {e}[/red]")
        raise typer.Exit(1)

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

if __name__ == "__main__":
    app()
