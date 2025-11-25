# Project File Extractor

Production-ready tool to extract and create project files from text documents using local LLM (Ollama).

## Features

- ✅ Extract file structure from text documents
- ✅ Generate code for each file using LLM
- ✅ Create complete project directory structure
- ✅ Secure file operations with path traversal protection
- ✅ Comprehensive logging and error handling
- ✅ Retry logic for LLM requests
- ✅ Production-ready security practices

## Requirements

- Python 3.8+
- Ollama installed and running locally
- LLM model (default: llama3.2:latest)

## Installation

1. Install Ollama:
```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

2. Pull required model:
```bash
ollama pull llama3.2:latest
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
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
python main.py projectTracker.txt -m codellama:latest
```

### Verbose Logging
```bash
python main.py projectTracker.txt -v
```

## Configuration

Edit .env file:
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_TIMEOUT=300

# Application Settings
OUTPUT_BASE_DIR=./output
MAX_INPUT_FILE_SIZE_MB=100
```

## How It Works

1. Parse Input: Reads the input text file containing project structure and code.
2. Extract Structure: Uses LLM to identify all file paths.
3. Create Directories: Creates the complete folder structure.
4. Extract Code: For each file, uses LLM to extract its specific code.
5. Write Files: Writes code to files with proper permissions.
6. Log Results: Provides detailed summary of created files.

## Security

- ✅ Input validation and sanitization
- ✅ Path traversal protection
- ✅ File size limits
- ✅ Secure file permissions (600)
- ✅ Sensitive data filtering in logs
- ✅ Timeout and retry limits

## Testing

```bash
pytest tests/ -v --cov=.
```

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama service
ollama serve
```

### Model Not Found
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3.2:latest
```

### Connection Timeout
Increase timeout in .env:
```bash
OLLAMA_TIMEOUT=600
```

## License

MIT License
