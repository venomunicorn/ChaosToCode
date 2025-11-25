# ChaosToCode: Zero-Copy Slicer

ChaosToCode is a tool designed to extract code files from a raw text dump using an LLM to identify boundaries and a Python engine to slice the content efficiently.

## Architecture

The project follows a modular "Zero-Copy Slicer" architecture:

- **`app/core`**: Handles LLM communication and prompts.
- **`app/engine`**: Contains the logic for boundary detection and content slicing.
- **`app/utils`**: Utilities for logging, security, and file I/O.
- **`app/main.py`**: The entry point of the application.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Copy `.env.example` to `.env`.
   - Set your `LLM_API_KEY` and `LLM_ENDPOINT`.

## Usage

To run the slicer:

```bash
python -m app.main --input input_data/dump.txt --output output_sliced_files/
```

- `--input`: Path to the raw text file containing code.
- `--output`: Directory where extracted files will be saved.

## Security

- Path traversal protection is enabled for input and output paths.
- Input text is sanitized before being sent to the LLM.
- Secrets are managed via environment variables.
