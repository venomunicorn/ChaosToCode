# Project File Extractor

Production-grade tool for extracting and creating project files from structured text using Ollama LLMs (128k context, chat models). Now updated with Anaconda Prompt (Windows) instructions.

## Features
- Extract file structure and code from docs/specs
- Robust tests and secure production logic (OWASP-aligned)
- Cross-platform: Windows (Anaconda Prompt, CMD, PowerShell), Linux, Mac

---

## Quick Start: Windows (Anaconda Prompt)

### 1. Open Anaconda Prompt and set up Python env
```sh
conda create -n fileextractor python=3.10 -y
conda activate fileextractor
```

### 2. Install Ollama for Windows
- Download and install from: [https://ollama.ai/download](https://ollama.ai/download)
- Start Ollama: 
  ```sh
  ollama serve
  ```

### 3. Pull a chat model (in Anaconda Prompt)
```sh
ollama pull qwen2.5:32b
# Or, for lower VRAM
ollama pull qwen2.5:14b
ollama pull gemma2:9b
```

### 4. Get the project and install Python requirements
```sh
git clone https://github.com/venomunicorn/ChaosToCode.git
cd ChaosToCode/project_file_extractor
pip install -r requirements.txt
```

### 5. Create and configure .env
```sh
copy .env.example .env
# Edit .env in Notepad/VSCode to set OLLAMA_MODEL and other values
```

### 6. Run extraction (normal usage)
```sh
python main.py projectTracker.txt
```

### 7. (Optional) Run tests
```sh
pytest tests/ -v --cov=.
```

---

## Linux / Mac Setup
Follow the original README's Linux/Mac section for curl-based Ollama install and steps. All commands work in bash/zsh as shown above.

## Troubleshooting
- If `ollama` is not recognized, add its path to your environment or re-launch Anaconda Prompt after installation.
- If model pulling or extraction fails, verify Ollama is running (`ollama serve`) and model is present (`ollama list`).
- Tune `OLLAMA_TIMEOUT` in `.env` for large docs.

## License
MIT License
