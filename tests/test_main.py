"""Unit tests for main.py entry point and validation logic."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import validate_input_file, read_input_file, main
from config import Config

@pytest.fixture
def temp_dir():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def valid_input_file(temp_dir):
    file_path = temp_dir / "test_input.txt"
    content = """
project_structure/
├── main.py
├── config.py

## main.py
```python
print('hello')
```

## config.py
```python
DEBUG = True
```
"""
    file_path.write_text(content, encoding='utf-8')
    return file_path

def test_validate_input_file_success(valid_input_file):
    assert validate_input_file(valid_input_file) is True

def test_validate_input_file_not_exists(temp_dir):
    fake_path = temp_dir / "nonexistent.txt"
    assert validate_input_file(fake_path) is False

def test_validate_input_file_wrong_extension(temp_dir):
    file_path = temp_dir / "test.exe"
    file_path.write_text("content")
    assert validate_input_file(file_path) is False

def test_validate_input_file_too_large(temp_dir, monkeypatch):
    file_path = temp_dir / "large.txt"
    file_path.write_text("x" * 1000)
    monkeypatch.setattr(Config, 'MAX_INPUT_FILE_SIZE_MB', 0.0001)
    from main import MAX_FILE_SIZE_BYTES
    assert validate_input_file(file_path) is False

def test_validate_input_file_empty(temp_dir):
    file_path = temp_dir / "empty.txt"
    file_path.write_text("")
    assert validate_input_file(file_path) is False

def test_read_input_file_success(valid_input_file):
    content = read_input_file(valid_input_file)
    assert content is not None
    assert "main.py" in content
    assert "config.py" in content

def test_read_input_file_empty_content(temp_dir):
    file_path = temp_dir / "whitespace.txt"
    file_path.write_text("   \n\n\t  ")
    content = read_input_file(file_path)
    assert content is None

@patch('main.OllamaClient')
def test_main_no_ollama_connection(mock_client_class, valid_input_file, temp_dir):
    mock_client = MagicMock()
    mock_client.check_connection.return_value = False
    mock_client_class.return_value.__enter__.return_value = mock_client
    exit_code = main(valid_input_file, temp_dir / "output")
    assert exit_code == 1

@patch('main.OllamaClient')
def test_main_model_not_available(mock_client_class, valid_input_file, temp_dir):
    mock_client = MagicMock()
    mock_client.check_connection.return_value = True
    mock_client.list_models.return_value = ["other:model"]
    mock_client_class.return_value.__enter__.return_value = mock_client
    exit_code = main(valid_input_file, temp_dir / "output")
    assert exit_code == 1

@patch('main.OllamaClient')
@patch('main.FileExtractor')
@patch('main.FileCreator')
def test_main_success_path(mock_creator_class, mock_extractor_class, mock_client_class, valid_input_file, temp_dir):
    mock_client = MagicMock()
    mock_client.check_connection.return_value = True
    mock_client.list_models.return_value = [Config.OLLAMA_MODEL]
    mock_client_class.return_value.__enter__.return_value = mock_client
    mock_extractor = MagicMock()
    mock_extractor.extract_file_structure.return_value = ["main.py", "config.py"]
    mock_extractor.extract_code_for_file.return_value = "print('test')"
    mock_extractor_class.return_value = mock_extractor
    mock_creator = MagicMock()
    mock_creator.created_files = ["main.py", "config.py"]
    mock_creator.failed_files = []
    mock_creator.write_file.return_value = True
    mock_creator_class.return_value = mock_creator
    exit_code = main(valid_input_file, temp_dir / "output")
    assert exit_code == 0
    assert mock_extractor.extract_file_structure.called
    assert mock_creator.write_file.called

def test_main_invalid_input_file(temp_dir):
    fake_file = temp_dir / "nonexistent.txt"
    exit_code = main(fake_file, temp_dir / "output")
    assert exit_code == 1
