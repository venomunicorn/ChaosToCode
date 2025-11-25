# Project File Extractor

Production-ready tool for extracting and creating project files from text documents using local LLMs (Ollama chat models, 128k context). Now includes full setup, usage, and troubleshooting instructions for Windows, Linux, and Mac.

## Features

- Extract file structure and code from text files
- Generate valid, full Python projects using a modern chat LLM
- Robust fallback structure/code extraction logic
- Path traversal, size, and extension security
- CLI for model management (startup/check/pull)
- Detailed logging & error handling

## Requirements

- **Python 3.8+**
- **Ollama** installed and running locally
- **Windows:** CMD, PowerShell, or Windows Terminal
- **Linux/Mac:** Bash/zsh/compatible shell (with curl)

**Recommended LLM:** qwen2.5:32b chat model (128k context). For 8GB VRAM, use qwen2.5:14b or gemma2:9b.

## Installation Instructions

### 1. Install Ollama

**Windows:**
1. Download Ollama from https://ollama.ai/download and install.
2. Launch 'Ollama' from Start Menu or use terminal:
   ```powershell
   ollama serve
   ```

**Linux/Mac:**
1. Open a terminal and run:
   ```bash
   curl https://ollama.ai/install.sh | sh
   ollama serve
   ```

### 2. Pull the Chat Model

**All OSes:** (After installation)
```shell
ollama pull qwen2.5:32b
# Or, for limited VRAM:
ollama pull qwen2.5:14b
```

### 3. Clone Project and Install Python Requirements

**All OSes:**
```shell
git clone https://github.com/venomunicorn/ChaosToCode.git
cd ChaosToCode/project_file_extractor
pip install -r requirements.txt
```

### 4. Configure Environment
```shell
cp .env.example .env # (or manually create .env on Windows)
edit .env            # Set OLLAMA_MODEL and paths as needed
```
- On **Windows**, use `copy .env.example .env` and edit `.env` in Notepad or VSCode.
- Ensure `OLLAMA_MODEL=qwen2.5:32b` or your selected model.

## Usage

### Basic Usage (All platforms)
```shell
python main.py projectTracker.txt
```

### Custom Output Directory
```shell
python main.py projectTracker.txt -o ./my_output
```

### Select a Model
```shell
python main.py projectTracker.txt -m qwen2.5:14b
```

### Verbose Mode
```shell
python main.py projectTracker.txt -v
```

## Model Setup and Troubleshooting

For help managing Ollama and models across platforms, use:
```shell
python ollama_manager.py --model qwen2.5:32b
```

- **If Ollama is not running on Windows,** make sure to launch it manually before running main.py.
  
- **Large projects:** You may need to increase OLLAMA_TIMEOUT in `.env` (e.g., to 600 seconds).

## Testing
```shell
pytest tests/ -v --cov=.
```

## Security Features

- Path validation & traversal protection
- Configurable allowed file extensions and max size
- Secure file write and env variable handling

## Supporting Mac & Linux
Instructions for Mac/Linux are given above, but all CLI actions and Python code work cross-platform.
If you have any Windows-specific issues (path, encoding, permissions), please report!

## License
MIT License

---
**Quick links:**
- [Ollama Windows Install](https://ollama.ai/download)
- [Ollama Pull Model Docs](https://ollama.com/library)
- [Project Issues / Feedback](https://github.com/venomunicorn/ChaosToCode/issues)
