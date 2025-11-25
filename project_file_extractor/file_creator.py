"""Create files and folders from extracted data."""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import os

from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)


class FileCreator:
    """Create project files and folders."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize file creator."""
        self.output_dir = output_dir or Config.OUTPUT_BASE_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.created_files: List[str] = []
        self.created_dirs: List[str] = []
        self.failed_files: List[Dict[str, str]] = []
        
        logger.info(f"FileCreator initialized with output_dir: {self.output_dir}")
    
    def create_directory_structure(self, file_paths: List[str]) -> None:
        """
        Create all necessary directories from file paths.
        
        Args:
            file_paths: List of file paths
        """
        logger.info(f"Creating directory structure for {len(file_paths)} files")
        
        directories = set()
        
        for file_path in file_paths:
            # Get directory path
            file_obj = self.output_dir / file_path
            dir_path = file_obj.parent
            
            if dir_path != self.output_dir:
                directories.add(dir_path)
        
        # Create all directories
        for dir_path in sorted(directories):
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.created_dirs.append(str(dir_path.relative_to(self.output_dir)))
                logger.debug(f"Created directory: {dir_path.relative_to(self.output_dir)}")
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {e}")
        
        logger.info(f"Created {len(self.created_dirs)} directories")
    
    def write_file(self, file_path: str, content: str) -> bool:
        """
        Write content to a file.
        
        Args:
            file_path: Relative file path
            content: File content
        
        Returns:
            True if successful, False otherwise
        """
        if not content:
            logger.warning(f"Empty content for {file_path}, skipping")
            self.failed_files.append({
                'path': file_path,
                'reason': 'Empty content'
            })
            return False
        
        try:
            full_path = self.output_dir / file_path
            
            # Security check: Prevent path traversal
            try:
                full_path.resolve().relative_to(self.output_dir.resolve())
            except ValueError:
                logger.error(f"Path traversal attempt detected: {file_path}")
                self.failed_files.append({
                    'path': file_path,
                    'reason': 'Path traversal attempt'
                })
                return False
            
            # Create parent directory if not exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Set file permissions (read/write for owner only)
            os.chmod(full_path, 0o600)
            
            self.created_files.append(file_path)
            logger.info(f"Created file: {file_path} ({len(content)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            self.failed_files.append({
                'path': file_path,
                'reason': str(e)
            })
            return False
    
    def get_summary(self) -> Dict[str, any]:
        """Get creation summary."""
        return {
            'total_directories': len(self.created_dirs),
            'total_files': len(self.created_files),
            'failed_files': len(self.failed_files),
            'created_files': self.created_files,
            'created_dirs': self.created_dirs,
            'failed_files': self.failed_files,
            'output_directory': str(self.output_dir)
        }
    
    def print_summary(self) -> None:
        """Print creation summary."""
        summary = self.get_summary()
        
        print("\n" + "="*70)
        print("PROJECT CREATION SUMMARY")
        print("="*70)
        print(f"Output Directory: {summary['output_directory']}")
        print(f"Directories Created: {summary['total_directories']}")
        print(f"Files Created: {summary['total_files']}")
        print(f"Files Failed: {summary['failed_files']}")
        
        if summary['failed_files'] > 0:
            print("\nFailed Files:")
            for failed in summary['failed_files']:
                print(f"  - {failed['path']}: {failed['reason']}")
        
        print("="*70 + "\n")
