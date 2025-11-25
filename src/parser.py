import re
import os
from typing import Iterator
from pathlib import Path

FILE_START_RE = re.compile(r"<<<FILE_START>>>((?:[^<]|<(?!!<))*?)<<<Header_End>>>", re.MULTILINE)
FILE_END = "<<<FILE_END>>>"

class ParsingError(Exception):
    pass

def stream_parse_ollama_output(stream: Iterator[str], output_dir: Path):
    """
    Generator function that parses Ollama output and writes files as soon as <<<FILE_END>>> is hit.
    Handles delimiters that may be split across stream chunks.
    """
    buffer = ""
    open_file = None
    file_path = None
    try:
        for chunk in stream:
            buffer += chunk
            while True:
                if open_file is None:
                    start_match = FILE_START_RE.search(buffer)
                    if start_match:
                        file_path = start_match.group(1).strip()
                        rest = buffer[start_match.end():]
                        open_file = []
                        buffer = rest
                    else:
                        # No file started yet, keep buffering
                        break
                else:
                    end_idx = buffer.find(FILE_END)
                    if end_idx == -1:
                        open_file.append(buffer)
                        buffer = ""
                        break
                    else:
                        open_file.append(buffer[:end_idx])
                        # Assemble content and write file
                        full_file_data = "".join(open_file)
                        abs_path = output_dir / file_path
                        os.makedirs(abs_path.parent, exist_ok=True)
                        try:
                            with open(abs_path, "w", encoding="utf-8") as f:
                                f.write(full_file_data.strip("\n"))
                        except OSError as e:
                            raise ParsingError(f"Failed to write file {abs_path}: {e}")
                        # Reset state for next file
                        buffer = buffer[end_idx + len(FILE_END):]
                        open_file, file_path = None, None
    except Exception as e:
        raise ParsingError(f"Parser error: {e}")
