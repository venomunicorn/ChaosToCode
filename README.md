# Chaos-to-Code

**An Agentic File Inflator** - Transform messy text dumps into organized project structures using a local LLM.

## Overview

Chaos-to-Code is a Python CLI tool that processes massive, unstructured text files (such as code dumps, chat logs, or documentation) using a local Ollama LLM. It identifies files and produces an organized, valid directory/file structure on disk using a streaming, memory-efficient pipeline.

---

## Features

- **Streaming Pipeline**: Handles very large input files without consuming excessive RAM
- **Regex State Machine Parser**: Extracts files using OTC-delimiters in real time
- **Automated Ollama Setup**: Automatically starts Ollama service and downloads required models
- **Robust Error Handling**: Handles file I/O and Ollama connection issues gracefully
- **Rich UI**: Progress bars and formatted, live output for user feedback
- **Two Commands**: `organize` (main agent function) and `clean` (reset output directory)

---

## Requirements

- **Python** 3.11+
- **Ollama** installed on your system (service will start automatically)
- Supported Models: `qwen2.5:7b` (default), `qwen3:8b`

---

## Installation

### 1. Install Ollama

Download and install Ollama from [https://ollama.com/download](https://ollama.com/download)

- **Windows**: Run the installer and follow the setup wizard
- **macOS**: `brew install ollama` or download from the website
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

Run the Ollama manager to automatically start the service and download the required model:

```bash
python src/ollama_manager.py --model qwen2.5:7b
```

This will:
- Check if Ollama is running and start it if needed
- Download the specified model if not already available
- Verify everything is ready to use

**Alternative Models:**
```bash
python src/ollama_manager.py --model qwen3:8b
```

---

## Usage

### Quick Start

1. **Setup Ollama** (first time only):
   ```bash
   python src/ollama_manager.py
   ```

2. **Organize your text file**:
   ```bash
   python -m src.main organize dump.txt
   ```

3. **Check the output** in the `output` directory

### Organize Unstructured Text

The `organize` command reads your large unstructured text source and streams file creation to the output directory using LLM-powered extraction:

```bash
python -m src.main organize <SOURCE_FILE> [OPTIONS]
```

**Options:**
- `--model TEXT`: The Ollama model to use (default: `qwen2.5:7b`)
- `--output-dir PATH`: Directory to write files (default: `output`)

**Examples:**

```bash
# Basic usage with default settings
python -m src.main organize dump.txt

# Use a different model
python -m src.main organize dump.txt --model qwen3:8b

# Specify custom output directory
python -m src.main organize dump.txt --output-dir extracted_files

# Combine options
python -m src.main organize archive.txt --model qwen3:8b --output-dir my_project
```

During execution, you'll see a spinner/progress indicator. Files will appear in the output directory as they are parsed. Organize can handle gigabyte-scale text files efficiently by streaming and writing immediately.

### Clean Output Directory

The `clean` command wipes the output directory completely:

```bash
python -m src.main clean [OPTIONS]
```

**Options:**
- `--output-dir PATH`: Directory to clean (default: `output`)

**Example:**

```bash
python -m src.main clean --output-dir extracted_files
```

---

## How It Works

### Architecture

1. **Ollama Manager** (`src/ollama_manager.py`)
   - Detects and starts the Ollama service automatically
   - Downloads required models if not available
   - Cross-platform support (Windows, Linux, macOS)

2. **AI Client** (`src/ai.py`)
   - Wraps the Ollama API client with streaming support
   - Injects a strict SYSTEM_PROMPT that forces OTC-delimited output for each file
   - Handles connection errors and timeouts gracefully

3. **Parser** (`src/parser.py`)
   - Runs a regex-based state machine scanning the Ollama output stream
   - Detects `<<<FILE_START>>>...<<<Header_End>>>` ... `<<<FILE_END>>>` blocks
   - Writes content to disk in real time
   - Handles split-delimiters across stream chunks

4. **CLI** (`src/main.py`)
   - Integrates Typer for command-line interface
   - Uses Rich for progress display and user feedback
   - Orchestrates the entire pipeline

### Processing Pipeline

```
Input File → AI Client (Ollama) → Streaming Response → Parser → File System
     ↓              ↓                      ↓              ↓           ↓
  dump.txt    LLM Processing      Chunked Output    Regex FSM    output/
                                                                  ├── file1.py
                                                                  ├── file2.js
                                                                  └── folder/
                                                                      └── file3.txt
```

---

## Output Format

The LLM is instructed to output files using this specific delimiter format:

```
<<<FILE_START>>>path/to/filename.ext<<<Header_End>>>
[File Content Here]
<<<FILE_END>>>
```

This format allows the parser to:
- Identify file boundaries clearly
- Extract the file path and create necessary directories
- Write content accurately without corruption
- Handle files of any size through streaming

---

## Troubleshooting

### Ollama Not Running

If you see connection errors, manually start Ollama:

```bash
# Start Ollama service
ollama serve
```

Or use the automated manager:

```bash
python src/ollama_manager.py
```

### Model Not Found

If the model isn't available, download it:

```bash
# Using Ollama manager (recommended)
python src/ollama_manager.py --model qwen2.5:7b

# Or manually
ollama pull qwen2.5:7b
```

### Large Files Taking Too Long

- Consider using a smaller, faster model like `qwen2.5:7b` instead of larger variants
- Split your input file into smaller chunks
- Ensure your system has adequate RAM (8GB+ recommended for RTX 4060)

### Permission Errors

Ensure you have write permissions for the output directory:

```bash
# Linux/macOS
chmod -R 755 output/

# Windows: Run terminal as Administrator
```

---

## Example Workflow

### First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/venomunicorn/ChaosToCode.git
cd ChaosToCode

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Ollama and download model
python src/ollama_manager.py
```

### Daily Usage

```bash
# 1. Place your unstructured text file in the project directory
# (e.g., dump.txt, archive.txt, code_export.txt)

# 2. Run the organize command
python -m src.main organize dump.txt

# 3. Check the output directory for organized files
ls output/

# 4. If you need to start over
python -m src.main clean
```

### Advanced Usage

```bash
# Process multiple files with different configurations
python -m src.main organize project1.txt --output-dir project1_output
python -m src.main organize project2.txt --model qwen3:8b --output-dir project2_output

# Clean specific directories
python -m src.main clean --output-dir project1_output
```

---

## Error Handling

- All file operations and LLM invocations include robust `try/except` blocks
- Clear error messages are displayed for common issues:
  - Ollama service not running
  - Model not available
  - File permission errors
  - Invalid input file format
  - Network connectivity issues
- The process stops with meaningful exit codes for automation

---

## Performance Considerations

- **Memory Efficient**: Streaming pipeline processes files without loading entire content into RAM
- **GPU Acceleration**: Leverages your RTX 4060 GPU when using Ollama with compatible models
- **Optimal Model**: `qwen2.5:7b` provides the best balance of speed and accuracy for 8GB VRAM
- **Batch Processing**: Can handle multiple gigabyte-scale files sequentially

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## License

MIT License

---

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/venomunicorn/ChaosToCode/issues)
- Check the [Ollama documentation](https://ollama.com/docs) for model-specific questions
