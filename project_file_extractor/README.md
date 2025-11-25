# Project File Extractor

Production-ready tool to extract and create project files from text documents using local LLM (Ollama 128k context, chat models).

## Features

- ✅ Extract file structure from text documents
- ✅ Generate code for each file using LLM (chat models, 128k context)
- ✅ Create complete project directory structure
- ✅ Secure file operations with path traversal protection
- ✅ Comprehensive logging and error handling
- ✅ Retry logic for LLM requests
- ✅ OWASP security practices

## Requirements

- Python 3.8+
- Ollama installed and running locally
- Chat LLM model with 128k context (`qwen2.5:32b` recommended for stability and quality)

## Installation

1. Install Ollama:
```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh
# Windows download: https://ollama.ai/download
```

2. Pull the recommended chat model (128k context):
```bash
ollama pull qwen2.5:32b
```
*If you run out of VRAM, try `qwen2.5:14b` or `gemma2:9b`*.

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env (make sure OLLAMA_MODEL=qwen2.5:32b)
```

## Usage

### Basic Usage
```bash
python main.py projectTracker.txt
```

### Custom Output Directory
```bash
python main.py projectTracker.txt -o ./my_project
```

### Use Different Model
```bash
python main.py projectTracker.txt -m qwen2.5:14b
```

### Verbose Logging
```bash
python main.py projectTracker.txt -v
```

## Configuration

Edit your `.env` file:
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
OLLAMA_TIMEOUT=300
```

## How It Works

1. Read input: Loads your text file with project structure & code
2. Extract structure: LLM identifies all file paths (128k context model)
3. Create directories: Builds folder structure automatically
4. Extract code: Pulls full code for each file, robust fallback if LLM fails
5. Write files: Saves extracted code securely, with strict path safety
6. Logs results: Detailed creation summary in logs

## Security Features

- Input validation and sanitization
- Path traversal protection
- File size limits
- Secure file permissions (600)
- Sensitive data filtering in logs
- Timeout and retry limits

## Testing

Run comprehensive tests:
```bash
pytest project_file_extractor/tests/ -v --cov=.
```

## Troubleshooting

- Ollama Not Running:
  ```bash
  ollama serve
  ```
- Model Not Found:
  ```bash
  ollama list
  ollama pull qwen2.5:32b
  ```
- VRAM issues: Use `qwen2.5:14b` or `gemma2:9b`
- Increasing timeout for large projects: set `OLLAMA_TIMEOUT=600` in `.env`

## Hardware Advice

For RTX 4060 (8GB VRAM) / 16GB RAM, `qwen2.5:32b` works for most projects. For very large files, try smaller models if needed.

## License

MIT License
