"""Extract file structure and code from input file using LLM."""

import re
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from llm_client import OllamaClient
from logger_config import setup_logger

logger = setup_logger(__name__)


class FileExtractor:
    """Extract file structure and code using LLM."""
    
    def __init__(self, llm_client: OllamaClient):
        """Initialize file extractor."""
        self.llm = llm_client
        logger.info("FileExtractor initialized")
    
    def extract_file_structure(self, content: str) -> List[str]:
        """
        Extract file structure (list of file paths) from content.
        
        Args:
            content: Input file content
        
        Returns:
            List of file paths (e.g., ['src/main.py', 'config.py'])
        """
        logger.info("Extracting file structure from content")
        
        system_prompt = """You are a file structure extractor. Analyze the provided content and extract ALL file paths.
Return ONLY a simple list of file paths, one per line. No explanations, no markdown, no additional text.
Format: path/to/file.ext

Example output:
requirements.txt
src/__init__.py
src/main.py
src/config/settings.py
tests/test_main.py
"""
        
        user_prompt = f"""Extract ALL file paths from this content. Return only the file paths, one per line.
Do not include folder-only entries (folders will be created автоматически from file paths).

Content:
{content[:50000]}
"""  # Limit content to prevent token overflow
        
        try:
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Parse file paths from response
            file_paths = self._parse_file_paths(response)
            
            logger.info(f"Extracted {len(file_paths)} file paths")
            return file_paths
            
        except Exception as e:
            logger.error(f"Failed to extract file structure: {e}")
            # Fallback: Try to extract manually
            return self._fallback_extract_structure(content)
    
    def _parse_file_paths(self, response: str) -> List[str]:
        """Parse file paths from LLM response."""
        lines = response.strip().split('\n')
        file_paths = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines, comments, markdown
            if not line or line.startswith('#') or line.startswith('```'):
                continue
            
            # Remove markdown list markers
            line = re.sub(r'^\s*[-*]\s+', '', line)
            line = re.sub(r'^\d+\.\s+', '', line)
            
            # Validate file path pattern
            if '/' in line or '\\' in line or '.' in line:
                # Normalize path separators
                line = line.replace('\\', '/')
                
                # Remove trailing slashes (directories only)
                line = line.rstrip('/')
                
                # Must have file extension
                if '.' in Path(line).name:
                    file_paths.append(line)
        
        return file_paths
    
    def _fallback_extract_structure(self, content: str) -> List[str]:
        """Fallback method to extract file structure using regex."""
        logger.warning("Using fallback file structure extraction")
        
        file_paths = []
        
        # Pattern to match file headers (##, ###, etc.)
        pattern = r'^#+\s+([a-zA-Z0-9_\-./\$]+\.[a-zA-Z0-9]+)\s*$'
        
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                path = match.group(1).replace('\\', '/')
                file_paths.append(path)
        
        logger.info(f"Fallback extracted {len(file_paths)} file paths")
        return file_paths
    
    def extract_code_for_file(self, content: str, file_path: str) -> Optional[str]:
        """
        Extract code content for a specific file.
        
        Args:
            content: Full input content
            file_path: Target file path to extract
        
        Returns:
            Code content for the file, or None if not found
        """
        logger.info(f"Extracting code for: {file_path}")
        
        system_prompt = """You are a code extractor. Extract ONLY the code content for the specified file.
Return ONLY the raw code without any explanations, markdown fences, or additional text.
If the file is not found, return "FILE_NOT_FOUND"."""
        
        user_prompt = f"""Extract the complete code content for this file: {file_path}

Return ONLY the code itself, no explanations, no markdown code fences.

Content:
{content[:100000]}
"""
        
        try:
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            if "FILE_NOT_FOUND" in response:
                logger.warning(f"File not found in content: {file_path}")
                # Try fallback extraction
                return self._fallback_extract_code(content, file_path)
            
            # Clean up response
            code = self._clean_code_response(response)
            
            logger.info(f"Extracted code for {file_path} ({len(code)} chars)")
            return code
            
        except Exception as e:
            logger.error(f"Failed to extract code for {file_path}: {e}")
            # Try fallback
            return self._fallback_extract_code(content, file_path)
    
    def _clean_code_response(self, response: str) -> str:
        """Clean up LLM response to get pure code."""
        # Remove markdown code fences
        code = re.sub(r'```[a-z]*\n', '', response)
        code = re.sub(r'```', '', code)
        
        return code.strip()
    
    def _fallback_extract_code(self, content: str, file_path: str) -> Optional[str]:
        """Fallback method to extract code using pattern matching."""
        logger.warning(f"Using fallback code extraction for {file_path}")
        
        # Normalize path for matching
        normalized_path = file_path.replace('\\', '/')
        
        # Try to find file section in content
        patterns = [
            r'```[a-z]*\n(.*?)```',
            rf'##\s+{re.escape(normalized_path)}\s*\n(.*?)(?=\n##|\Z)',
            rf'###\s+{re.escape(normalized_path)}\s*\n```[a-z]*\n(.*?)```'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            if match:
                code = match.group(1).strip()
                logger.info(f"Fallback extracted code for {file_path} ({len(code)} chars)")
                return code
        
        logger.error(f"Could not extract code for {file_path} using fallback")
        return None
