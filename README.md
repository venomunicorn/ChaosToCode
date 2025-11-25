# Project File Extractor

Production-ready tool to extract and create project files from text documents using local LLMs with 128k context chat models.

## Features

- Extract file structure from text documents
- Generate code for each file using LLM (Ollama chat models, 128k context)
- Create directory structure for a full project
- Secure file operations (path traversal protection)
- Detailed logging and error handling
- Modern dependency management
- Ready for Pytest-based testing

## Requirements

- Python 3.8+
- Ollama running locally and a chat model (128k context recommended: `qwen2.5:32b`)
- See requirements.txt for all Python dependencies

## Installation

1. **Install Ollama:**
   - Linux/Mac:
    ```bash
    curl https://ollama.ai/install.sh | sh
    ```
   - Windows: Download from https://ollama.ai/download

2. **Pull recommended model:**
   ```bash
   ollama pull qwen2.5:32b
   ```
   *For 8GB VRAM, try also `qwen2.5:14b` or `gemma2:9b` as fallback.*

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env for path, model, and settings
   ```

## Usage

- **Basic usage:**
   ```bash
   python main.py projectTracker.txt
   ```
- **Set output dir:**
   ```bash
   python main.py projectTracker.txt -o ./my_output
   ```
- **Choose another model:**
   ```bash
   python main.py projectTracker.txt -m qwen2.5:14b
   ```
- **Verbose mode:**
   ```bash
   python main.py projectTracker.txt -v
   ```

## Pipeline

- Uses only the following core modules:
  - `main.py` (entry point)
  - `config.py`, `logger_config.py`, `llm_client.py`, `file_extractor.py`, `file_creator.py`
- All logic is unified in these files (NO usage of old ai.py, parser.py, etc.)
- `ollama_manager.py` is a helper CLI to set up and fetch models, not used by extraction pipeline.

## Configuration

- `.env` and `.env.example` contain all variables used in pipeline. 
- Only relevant variables will be read (ignore any others).

## Testing

Run the main test suite with:
```bash
pytest project_file_extractor/tests/ -v --cov=.
```

## Security

- Path traversal protection
- Input size and extension validation
- Secure file permission (600)
- Logging filters for sensitive info
- LLM request timeout/retry safeguards

## Troubleshooting

- Use `ollama_manager.py` (CLI) to check/start Ollama service and download models before running extraction.
- Increase timeout in .env for large projects.
- If requirements missing, update with provided requirements.txt.

## Changelog

- Removed deprecated modules: ai.py, parser.py
- Unified requirements in requirements.txt
- Confirmed LLM and extraction logic only flows through main pipeline
- Ensured consistent configuration, logging, and fallback handling

## License
MIT License
