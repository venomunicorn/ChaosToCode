"""Fallback file extractor with improved regex handling (fixed broken patterns)."""

import re
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from llm_client import OllamaClient
from logger_config import setup_logger

logger = setup_logger(__name__)


class FileExtractor:
    """Extract file structure and code using LLM and robust fallback."""

    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
        logger.info("FileExtractor initialized")

    def extract_file_structure(self, content: str) -> List[str]:
        logger.info("Extracting file structure from content")
        system_prompt = (
            "You are a file structure extractor. Analyze the provided content and extract ALL file paths.\n"
            "Return ONLY a simple list of file paths, one per line. No explanations, no markdown, no additional text.\n"
            "Format: path/to/file.ext\n\n"
            "Example output:\nrequirements.txt\nsrc/__init__.py\nsrc/main.py\nsrc/config/settings.py\ntests/test_main.py"
        )
        user_prompt = (
            "Extract ALL file paths from this content. Return only the file paths, one per line.\n"
            "Do not include folder-only entries (folders will be created automatically from file paths).\n\n"
            f"Content:\n{content[:120000]}"
        )
        try:
            response = self.llm.generate(prompt=user_prompt, system_prompt=system_prompt, temperature=0.1)
            file_paths = self._parse_file_paths(response)
            logger.info(f"Extracted {len(file_paths)} file paths")
            return file_paths
        except Exception as e:
            logger.error(f"Failed to extract file structure: {e}")
            return self._fallback_extract_structure(content)

    def _parse_file_paths(self, response: str) -> List[str]:
        lines = response.strip().split('\n')
        file_paths = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('```'):
                continue
            # Remove markdown list markers
            line = re.sub(r'^\s*[-*]\s+', '', line)
            line = re.sub(r'^\d+\.\s+', '', line)
            # Validate file path pattern
            if '/' in line or '\\' in line or '.' in line:
                line = line.replace('\\', '/')
                line = line.rstrip('/')
                if '.' in Path(line).name:
                    file_paths.append(line)
        return file_paths

    def _fallback_extract_structure(self, content: str) -> List[str]:
        logger.warning("Using fallback file structure extraction")
        file_paths = []
        # Find lines likely to be file paths
        lines = content.split('\n')
        path_pattern = re.compile(r"[a-zA-Z0-9_/\\.-]+\.[a-zA-Z0-9]+")
        for line in lines:
            matches = path_pattern.findall(line)
            for match in matches:
                normalized = match.replace('\\', '/').rstrip('/')
                if normalized not in file_paths:
                    file_paths.append(normalized)
        logger.info(f"Fallback extracted {len(file_paths)} file paths")
        return file_paths

    def extract_code_for_file(self, content: str, file_path: str) -> Optional[str]:
        logger.info(f"Extracting code for: {file_path}")
        system_prompt = (
            "You are a code extractor. Extract ONLY the code content for the specified file.\n"
            "Return ONLY the raw code without any explanations, markdown fences, or additional text.\n"
            "If the file is not found, return FILE_NOT_FOUND."
        )
        user_prompt = (
            f"Extract the complete code content for this file: {file_path}\n\n"
            "Return ONLY the code itself, no explanations, no markdown code fences.\n\n"
            f"Content:\n{content[:120000]}"
        )
        try:
            response = self.llm.generate(prompt=user_prompt, system_prompt=system_prompt, temperature=0.1)
            if "FILE_NOT_FOUND" in response:
                logger.warning(f"File not found in content: {file_path}")
                return self._fallback_extract_code(content, file_path)
            return self._clean_code_response(response)
        except Exception as e:
            logger.error(f"Failed to extract code for {file_path}: {e}")
            return self._fallback_extract_code(content, file_path)

    def _clean_code_response(self, response: str) -> str:
        code = re.sub(r'```[a-z]*\n', '', response)
        code = re.sub(r'```', '', code)
        return code.strip()

    def _fallback_extract_code(self, content: str, file_path: str) -> Optional[str]:
        logger.warning(f"Using fallback code extraction for {file_path}")
        # Better fallback: Find anchors by file path lines and extract until possible new path
        pattern = re.compile(
            rf"(##+\s*{re.escape(file_path)}\s*\n+|{re.escape(file_path)}:?\s*\n+)(.*?)(?=\n##+\s|\n[a-zA-Z0-9_/\\.-]+\.[a-zA-Z0-9]+:?\s*\n+|\Z)",
            re.DOTALL | re.IGNORECASE
        )
        match = pattern.search(content)
        if match:
            code = match.group(2) or match.group(0)
            code = code.strip()
            if code:
                logger.info(f"Fallback extracted code for {file_path} ({len(code)} chars)")
                return code
        logger.error(f"Could not extract code for {file_path} using fallback")
        return None
