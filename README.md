# Chaos-to-Code

**An Agentic File Inflator** - Transform messy text dumps into organized project structures using local LLM.

## Overview

Chaos-to-Code is a Python CLI tool that reads massive, unstructured text files (code dumps, chat logs, documentation) and uses a local Ollama LLM to automatically identify files and create a valid directory/file structure.

## Features

- **Streaming Pipeline**: Handles large inputs without RAM issues
- **State Machine Parser**: Real-time extraction with delimiter detection
- **Error Handling**: Comprehensive try/except for I/O and Ollama connections
- **Rich UI**: Progress bars and formatted console output
- **Two Commands**: `organize` and `clean`

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.11+
- Ollama running locally (default: http://localhost:11434)
- Supported models: qwen2.5:7b, qwen3:8b

## Usage

### Organize Files

```bash
python -m src.main organize input.txt --model qwen2.5:7b --output-dir output
```

### Clean Output Directory

```bash
python -m src.main clean --output-dir output
```

## Architecture

- **src/ai.py**: Ollama client with streaming API and system prompt injection
- **src/parser.py**: Regex-based state machine for file extraction
- **src/main.py**: Typer CLI with Rich progress display

## License

MIT License
