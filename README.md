# Chaos-to-Code

**An Agentic File Inflator** - Transform messy text dumps into organized project structures using a local LLM.

## Overview

Chaos-to-Code is a Python CLI tool that processes massive, unstructured text files using a local Ollama LLM. It identifies files and produces an organized, valid directory/file structure on disk using a streaming, memory-efficient pipeline.

---

## Features

- **Streaming Pipeline**: Handles very large input files without excess RAM
- **Regex State Machine Parser**: Extracts files using OTC-delimiters in real time
- **Automated Ollama Setup**: Starts Ollama service and downloads required models automatically
- **Robust Error Handling**: Handles file I/O and Ollama connection issues
- **Rich UI**: Progress bars and live output for user feedback
- **Two Commands**: `organize` (main agent function) and `clean` (reset output directory)

---

## Requirements

- **Python** 3.11+
- **Ollama** installed and running locally (automatically launched)
- Default Model: `qwen2.5-coder:7b` (recommended); others supported if specified

---

## Installation

### 1. Install Ollama

- [Download Ollama](https://ollama.com/download)
- **Windows**: Installer wizard
- **macOS**: `brew install ollama` or from website
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

### 2. Clone the Repository
```bash
git clone https://github.com/venomunicorn/ChaosToCode.git
cd ChaosToCode
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Ollama and Download Model (Automated)
Default setup ensures `qwen2.5-coder:7b` is available and running:
```bash
python src/ollama_manager.py
```
To select another model:
```bash
python src/ollama_manager.py --model qwen3:8b
```
---

## Usage

### Quick Start
```bash
python src/ollama_manager.py   # Ensures all is ready (default is qwen2.5-coder:7b)
python -m src.main organize dump.txt
```
Organized files will be saved in the `output` directory.

### Organize Unstructured Text
```bash
python -m src.main organize <SOURCE_FILE> [OPTIONS]
```
**Options:**
- `--model TEXT`: Ollama model to use (default: `qwen2.5-coder:7b`)
- `--output-dir PATH`: Directory for extracted files (default: `output`)

#### Examples:
```bash
python -m src.main organize dump.txt                  # Uses default model
python -m src.main organize dump.txt --model qwen3:8b # Uses specified model
python -m src.main organize dump.txt --output-dir extracted_files
python -m src.main organize archive.txt --model qwen3:8b --output-dir my_project
```

### Clean Output Directory
```bash
python -m src.main clean --output-dir extracted_files
```
---

## How It Works

### Architecture
- **Ollama Manager** (`src/ollama_manager.py`): Starts Ollama, downloads models (default: `qwen2.5-coder:7b`)
- **AI Client** (`src/ai.py`): Wraps Ollama API using streaming and context size (default: 128k)
- **Parser** (`src/parser.py`): Regex state-machine parses streamed output and writes files
- **CLI** (`src/main.py`): Orchestrates with Typer CLI and Rich feedback

### Output Format
```
<<<FILE_START>>>path/to/filename.ext<<<Header_End>>>
[File Content Here]
<<<FILE_END>>>
```

---

## Troubleshooting & Tips
- Default setup uses `qwen2.5-coder:7b` for large contexts and coding tasks
- To manually select a different model, specify the name in commands (`--model qwen3:8b`)
- Permission issues: Run command prompt/terminal as administrator if needed

---

## Example Workflow
```bash
# Clone and install
git clone https://github.com/venomunicorn/ChaosToCode.git && cd ChaosToCode
pip install -r requirements.txt
python src/ollama_manager.py  # Ensures the default model is setup
python -m src.main organize dump.txt
ls output/
python -m src.main clean
```
---

## Configuration Scripts
- Configuration and installation scripts now reference the `qwen2.5-coder:7b` model by default. Edit arguments to select other supported models if needed.

---
## License
MIT License

---
## Support
- For issues/questions, open an issue on [GitHub](https://github.com/venomunicorn/ChaosToCode/issues)
- Check [Ollama documentation](https://ollama.com/docs) for model-specific help
