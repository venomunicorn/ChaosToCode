"""Tests for file creator."""

import pytest
from pathlib import Path
import tempfile
import shutil

from file_creator import FileCreator


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_create_directory_structure(temp_output_dir):
    """Test directory creation."""
    creator = FileCreator(temp_output_dir)
    
    file_paths = [
        'src/main.py',
        'src/config/settings.py',
        'tests/test_main.py',
        'README.md'
    ]
    
    creator.create_directory_structure(file_paths)
    
    assert (temp_output_dir / 'src').exists()
    assert (temp_output_dir / 'src' / 'config').exists()
    assert (temp_output_dir / 'tests').exists()


def test_write_file(temp_output_dir):
    """Test file writing."""
    creator = FileCreator(temp_output_dir)
    
    content = "print('Hello, World!')"
    success = creator.write_file('test.py', content)
    
    assert success
    assert (temp_output_dir / 'test.py').exists()
    assert (temp_output_dir / 'test.py').read_text() == content


def test_write_file_path_traversal(temp_output_dir):
    """Test path traversal protection."""
    creator = FileCreator(temp_output_dir)
    
    # Attempt path traversal
    success = creator.write_file('../../../etc/passwd', 'malicious')
    
    assert not success
    assert len(creator.failed_files) == 1


def test_write_file_empty_content(temp_output_dir):
    """Test handling of empty content."""
    creator = FileCreator(temp_output_dir)
    
    success = creator.write_file('empty.txt', '')
    
    assert not success
    assert len(creator.failed_files) == 1
