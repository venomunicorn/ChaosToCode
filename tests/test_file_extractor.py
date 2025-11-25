"""Unit tests for file_extractor.py: structure extraction, code extraction, and fallback logic."""

import pytest
from unittest.mock import MagicMock
from file_extractor import FileExtractor
from llm_client import OllamaClient

CONTENT = """
project_file_extractor/
├── requirements.txt
├── .env.example
├── file_creator.py
├── main.py
├── README.md
# requirement.txt
requests>=2.31.0
pytest>=7.4.0
# file_creator.py
print('hello world')
# main.py
if __name__ == '__main__': print('run')
"""

@pytest.fixture
def mock_llm():
    mock = MagicMock(spec=OllamaClient)
    return mock

def test_extract_file_structure_llm_and_regex(mock_llm):
    # Examine both LLM and fallback path parsing
    llm_response = 'requirements.txt\nfile_creator.py\nmain.py\nREADME.md'
    mock_llm.generate.return_value = llm_response
    ext = FileExtractor(mock_llm)
    paths = ext.extract_file_structure(CONTENT)
    assert set(paths) == {"requirements.txt", "main.py", "file_creator.py", "README.md"}

    # Simulate LLM failure; force fallback
    mock_llm.generate.side_effect = Exception("fail")
    paths_fallback = ext.extract_file_structure(CONTENT)
    assert "file_creator.py" in paths_fallback


def test_extract_code_for_file_llm_and_fallback(mock_llm):
    ext = FileExtractor(mock_llm)

    # LLM returns code
    mock_llm.generate.return_value = "print('hello world')"
    code = ext.extract_code_for_file(CONTENT, "file_creator.py")
    assert "hello world" in code

    # LLM can't find, fallback triggers
    mock_llm.generate.return_value = "FILE_NOT_FOUND"
    fallback_code = ext.extract_code_for_file(CONTENT, "main.py")
    assert "if __name__" in fallback_code
    # Edge: no code found
    none = ext.extract_code_for_file(CONTENT, "not_real.py")
    assert none is None


def test_clean_code_response():
    ext = FileExtractor(MagicMock())
    resp = "```python\nprint('x')\n```"
    assert ext._clean_code_response(resp) == "print('x')"
