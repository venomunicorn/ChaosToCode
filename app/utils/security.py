import os
import re
import json
from typing import Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

def validate_path_safely(path: str) -> bool:
    """
    Ensure path is free from path traversal or illegal characters.
    """
    # Reject if path contains path traversal patterns
    if ".." in path or path.startswith(("/", "\\")) or path.startswith("~"):
        return False
    # Reject unusual control characters, allow typical filename chars
    if re.search(r"[^a-zA-Z0-9_\-./]", path):
        return False
    return True

def sanitize_text_input(user_input: str) -> str:
    """
    Basic sanitization of input text.
    In production, more rigorous validation rules or sanitizers may be applied.
    """
    # Here minimal sanitization to remove dangerous characters not expected in code boundaries
    sanitized = user_input.replace("\x00", "")  # Remove null bytes
    return sanitized

def validate_json_manifest(manifest: Any) -> bool:
    """
    Validates JSON manifest structure: list of dicts with required keys.
    """
    if not isinstance(manifest, list):
        return False
    required_keys = {"filename", "start_marker", "end_marker"}
    for entry in manifest:
        if not isinstance(entry, dict):
            return False
        if not required_keys.issubset(entry.keys()):
            return False
        # Basic validations on values
        if not all(isinstance(entry[key], str) and entry[key].strip() for key in required_keys):
            return False
    return True
