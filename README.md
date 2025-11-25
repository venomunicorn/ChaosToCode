# Chaos-to-Code

**An Agentic File Inflator** - Transform messy text dumps into organized project structures using a local LLM.

## Overview

Chaos-to-Code is a Python CLI tool that processes massive, unstructured text files (such as code dumps, chat logs, or documentation) using a local Ollama LLM. It identifies files and produces an organized, valid directory/file structure on disk using a streaming, memory-efficient pipeline.

---

## Features

- **Streaming Pipeline**: Handles very large input files without consuming excessive RAM
- **Regex State Machine Parser**: Extracts files using OTC-delimiters in real time
- **Robust Error Handling**: Handles file I/O and Ollama connection issues gracefully
- **Rich UI**: Progress bars and formatted, live output for user feedback
- **Two Commands**: `organize` (main agent function) and `clean` (reset output directory)

---

## Requirements

- **Python** 3.11+
- **Ollama** running locally on [http://localhost:11434](http://localhost:11434) (default)
- Models: `qwen2.5:7b`, `qwen3:8b` supported (selectable via CLI)

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/venomunicorn/ChaosToCode.git
    cd ChaosToCode
    ```
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Ensure Ollama is running locally with your selected model downloaded and available.
    For Ollama installation and model management, see: [Ollama Docs](https://ollama.com/)

---

## Usage

### Organize Unstructured Text

The `organize` command reads your large unstructured text source and streams file creation to the output directory using LLM-powered extraction:

```bash
python -m src.main organize <SOURCE_FILE> --model <MODEL_NAME> --output-dir <OUTPUT_DIR>
```

- **SOURCE_FILE**: Path to your unstructured input text file (required)
- **MODEL_NAME**: The Ollama model to use (default: `qwen2.5:7b`)
- **OUTPUT_DIR**: Directory to write files (default: `output`)

#### Example:

```bash
python -m src.main organize dump.txt --model qwen3:8b --output-dir extracted_files
```

During execution, you'll see a spinner/progress indicator. Files will appear in the output directory as they are parsed. Organize can handle gigabyte-scale text files efficiently by streaming and writing immediately.

### Clean Output Directory

The `clean` command wipes the output directory completely:

```bash
python -m src.main clean --output-dir <OUTPUT_DIR>
```

#### Example:

```bash
python -m src.main clean --output-dir extracted_files
```

---

## How It Works

- **src/ai.py** wraps the Ollama client, injecting a strict SYSTEM_PROMPT that forces OTC-delimited output for each file.
- **src/parser.py** runs a regex-based state machine that scans the Ollama output stream for each `<<<FILE_START>>>...<<<Header_End>>>` ... `<<<FILE_END>>>` block and writes content to disk in real time (handles split-delimiters across stream chunks).
- **src/main.py** integrates Typer (CLI) and Rich (progress display) for seamless control and user feedback.

---

## Error Handling

- All file operations and LLM invocations include robust `try/except` blocks. If an error occurs (file write, I/O, Ollama not found, etc), a clear error message will be shown, and the process stops with a meaningful code.

---

## Example Project Workflow

1. Place your dump file (e.g. `archive.txt`) in the project directory.
2. Make sure Ollama is running and your chosen model is downloaded and started. Example (in another terminal):
    ```bash
    ollama run qwen3:8b
    ```
3. Run the organize command:
    ```bash
    python -m src.main organize archive.txt --model qwen3:8b --output-dir project_files
    ```
4. Monitor the output and Rich UI for progress.
5. Check `project_files` for the structured folders and files.
6. To clear and start over:
    ```bash
    python -m src.main clean --output-dir project_files
    ```
---

## License

MIT License
