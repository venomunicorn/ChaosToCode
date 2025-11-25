# Project File Extractor

Production-ready tool for extracting and creating project files from structured text (like specs or README docs) using local LLMs with 128k context (Ollama chat models).

## Features
- Full extraction and code generation pipeline ready for production
- Secure, validated input and output (OWASP-aligned)
- Comprehensive tests:
  - Unit, integration, error path, e2e coverage
- Works on **Windows, Linux, and Mac**, with extra clarity for Windows setup
- Stepwise setup and troubleshooting instructions

## Requirements
- Python 3.8+
- Ollama running locally, with a "chat" model (128k context recommended: `qwen2.5:32b`)
- See requirements.txt for all Python dependencies

## Installation and Setup

### 1. Install Ollama:
#### Windows:
- Download & install from [https://ollama.ai/download](https://ollama.ai/download)
- Launch from Start menu or run:  
  ```powershell
  ollama serve
  ```
#### Linux/Mac:
- Terminal:  
  ```bash
  curl https://ollama.ai/install.sh | sh
  ollama serve
  ```

### 2. Pull your model (all OSes):
```shell
ollama pull qwen2.5:32b
# for lower VRAM, try qwen2.5:14b or gemma2:9b
```

### 3. Clone and install the extractor:
```shell
git clone https://github.com/venomunicorn/ChaosToCode.git
cd ChaosToCode/project_file_extractor
pip install -r requirements.txt
```

### 4. Configure:
```shell
cp .env.example .env   # (Windows: copy .env.example .env)
edit .env              # set OLLAMA_MODEL, paths
```

## Usage
- Extract from doc:
  ```shell
  python main.py projectTracker.txt
  ```
- Custom output location:
  ```shell
  python main.py mydoc.txt -o ./my_extracted_project
  ```
- Change model (if needed):
  ```shell
  python main.py mydoc.txt -m qwen2.5:14b
  ```
- Verbose mode:
  ```shell
  python main.py mydoc.txt -v
  ```

## Advanced: Running tests
```shell
pytest tests/ -v --cov=.
```

## Model management/troubleshooting (all OS):
```shell
python ollama_manager.py --model qwen2.5:32b
```
- Increase `OLLAMA_TIMEOUT` in `.env` for very large projects (e.g., 600s for 128k content)

## Security Considerations
- All file/system and model input/output is validated and sanitized
- Path traversal and unsafe files are skipped with strong logging
- Secrets are never logged and must be set as env vars or in `.env`
- Logs redact sensitive terms and are rotated to avoid leaks

## FAQ
- For permissions, encoding, or executable errors on Windows: **always run shells "As Administrator" if needed.**
- All example commands run on Windows (PowerShell/CMD) and Linux/Mac.

## Support
- [Raise issues here](https://github.com/venomunicorn/ChaosToCode/issues) or [discuss](https://github.com/venomunicorn/ChaosToCode/discussions)
- PRs welcome for new LLM models, security, or OS improvements

## License
MIT License
