# Chaos-to-Code

**Agentic File Organizer – Only for Existing Code**

## Overview
This tool processes messy text/code dumps using Ollama LLM, but **strictly forbids any code generation**. It ONLY extracts and organizes code that already exists in your input text, preserving formatting exactly. It will never write new functions, fill TODOs, or complete incomplete logic.

---

## Features
- STREAMING pipeline for large dumps
- Automated Ollama setup
- Robust error handling
- Two commands: `organize` and `clean`
- **Strict parser mode** (no code generation)

---

## Requirements
- Python 3.11+
- Ollama installed and running locally (auto-launched)
- Default Model: qwen2.5-coder:7b (others supported if specified)

---

## Installation
1. Install Ollama ([link](https://ollama.com/download))
2. Clone repo, install deps:
   ```bash
   git clone https://github.com/venomunicorn/ChaosToCode.git
   cd ChaosToCode
   pip install -r requirements.txt
   ```
3. Setup Ollama and download default model:
   ```bash
   python src/ollama_manager.py
   ```

---

## Usage
#### Only Organizes Existing Code
```bash
python -m src.main organize dump.txt
```
- If dump.txt contains code, it will be PARSED and ORGANIZED into files
- If dump.txt only has descriptions, empty files or NO output will be created
- Will never generate new code

#### Clean Output
```bash
python -m src.main clean --output-dir extracted_files
```

---

## How It Works
- **System Prompt:** Instructs model never to generate or complete code
- **Parser:** Extracts files based on delimiters from LLM output
- **Output:** Only code from input is written, unchanged

---

## Example Workflow
```bash
# Clone, setup, organize ONLY existing code from input
python src/ollama_manager.py
python -m src.main organize dump.txt   # ONLY organizes code in dump.txt
ls output/
```
---

## Support
For issues/questions, open GitHub issues or see [Ollama docs](https://ollama.com/docs)
