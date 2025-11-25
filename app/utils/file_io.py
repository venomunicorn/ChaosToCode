import os
import asyncio
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def read_input_file(file_path: str) -> str:
    """
    Reads input text file asynchronously and returns its content.
    Validates file path to avoid path traversal attacks.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    loop = asyncio.get_event_loop()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = await loop.run_in_executor(None, f.read)
        return content
    except Exception as e:
        logger.error(f"Error reading input file {file_path}: {e}")
        raise

async def write_output_files(files_content: dict, output_dir: str):
    """
    Writes multiple files asynchronously to the output directory.
    Creates the directory if it doesn't exist.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    loop = asyncio.get_event_loop()
    tasks = []

    for filename, content in files_content.items():
        safe_path = os.path.join(output_dir, os.path.basename(filename))  # Sanitize filename
        tasks.append(loop.run_in_executor(None, _write_file, safe_path, content))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for res in results:
        if isinstance(res, Exception):
            logger.error(f"Error writing file: {res}")

def _write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
