"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import main
from config import Config

@pytest.fixture
def temp_workspace():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_project_doc(temp_workspace):
    doc_path = temp_workspace / "project.txt"
    content = """
# My Python Project

project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── requirements.txt

## src/__init__.py
```python
"""Package initialization."""
__version__ = "1.0.0"
```

## src/main.py
```python
"""Main application entry point."""

def main():
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    exit(main())
```

## src/utils.py
```python
"""Utility functions."""

def helper():
    return "helper"
```

## tests/test_main.py
```python
"""Tests for main module."""
import pytest
from src.main import main

def test_main():
    assert main() == 0
```

## requirements.txt
```
pytest>=7.0.0
```
"""
    doc_path.write_text(content, encoding='utf-8')
    return doc_path

@patch('main.OllamaClient')
def test_integration_full_extraction_workflow(mock_client_class, sample_project_doc, temp_workspace):
    output_dir = temp_workspace / "output"
    mock_client = MagicMock()
    mock_client.check_connection.return_value = True
    mock_client.list_models.return_value = [Config.OLLAMA_MODEL]
    def mock_generate(prompt, system_prompt=None, **kwargs):
        if "extract ALL file paths" in prompt.lower():
            return """
src/__init__.py
src/main.py
src/utils.py
tests/test_main.py
requirements.txt
"""
        if "src/main.py" in prompt:
            return 'def main():\n    print("Hello, World!")\n    return 0'
        elif "src/__init__.py" in prompt:
            return '__version__ = "1.0.0"'
        elif "src/utils.py" in prompt:
            return 'def helper():\n    return "helper"'
        elif "test_main.py" in prompt:
            return 'import pytest\nfrom src.main import main\n\ndef test_main():\n    assert main() == 0'
        elif "requirements.txt" in prompt:
            return 'pytest>=7.0.0'
        return "# placeholder"
    mock_client.generate = mock_generate
    mock_client_class.return_value.__enter__.return_value = mock_client
    exit_code = main(sample_project_doc, output_dir)
    assert exit_code == 0
    assert (output_dir / "src" / "main.py").exists()
    assert (output_dir / "src" / "__init__.py").exists()
    assert (output_dir / "src" / "utils.py").exists()
    assert (output_dir / "tests" / "test_main.py").exists()
    assert (output_dir / "requirements.txt").exists()
    main_content = (output_dir / "src" / "main.py").read_text()
    assert "Hello, World!" in main_content

@patch('main.OllamaClient')
def test_integration_partial_failure_handling(mock_client_class, sample_project_doc, temp_workspace):
    output_dir = temp_workspace / "output"
    mock_client = MagicMock()
    mock_client.check_connection.return_value = True
    mock_client.list_models.return_value = [Config.OLLAMA_MODEL]
    call_count = [0]
    def mock_generate_with_failures(prompt, system_prompt=None, **kwargs):
        call_count[0] += 1
        if "extract ALL file paths" in prompt.lower():
            return "src/main.py\nsrc/broken.py\ntests/test.py"
        if call_count[0] == 3:
            raise Exception("LLM extraction failed")
        return f"# code {call_count[0]}"
    mock_client.generate = mock_generate_with_failures
    mock_client_class.return_value.__enter__.return_value = mock_client
    exit_code = main(sample_project_doc, output_dir)
    assert exit_code in [0, 1]
    assert output_dir.exists()
    assert len(list(output_dir.rglob("*.py"))) >= 1

@patch('main.OllamaClient')
def test_integration_security_path_traversal_prevention(mock_client_class, temp_workspace):
    malicious_doc = temp_workspace / "malicious.txt"
    content = """
## ../../../etc/passwd
```
root:x:0:0:root:/root:/bin/bash
```

## ../../windows/system32/config/sam
```
malicious content
```
"""
    malicious_doc.write_text(content)
    output_dir = temp_workspace / "output"
    mock_client = MagicMock()
    mock_client.check_connection.return_value = True
    mock_client.list_models.return_value = [Config.OLLAMA_MODEL]
    mock_client.generate.return_value = "../../../etc/passwd\n../../windows/system32/config/sam"
    mock_client_class.return_value.__enter__.return_value = mock_client
    exit_code = main(malicious_doc, output_dir)
    assert exit_code == 1
    if output_dir.exists():
        created_files = list(output_dir.rglob("*"))
        for file in created_files:
            assert file.is_relative_to(output_dir)
