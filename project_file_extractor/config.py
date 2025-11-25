"""Configuration management with environment variables and validation."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration with secure defaults and validation."""
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))
    OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
    
    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    OUTPUT_BASE_DIR: Path = Path(os.getenv("OUTPUT_BASE_DIR", "./output"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_CONCURRENT_EXTRACTIONS: int = int(os.getenv("MAX_CONCURRENT_EXTRACTIONS", "1"))
    
    # Security
    MAX_INPUT_FILE_SIZE_MB: int = int(os.getenv("MAX_INPUT_FILE_SIZE_MB", "100"))
    ALLOWED_FILE_EXTENSIONS: set = set(os.getenv("ALLOWED_FILE_EXTENSIONS", ".txt,.md").split(","))
    
    # Logging
    LOG_DIR: Path = Path("./logs")
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration values."""
        # Create required directories
        cls.OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Validate numeric ranges
        if cls.OLLAMA_TIMEOUT < 10 or cls.OLLAMA_TIMEOUT > 600:
            raise ValueError("OLLAMA_TIMEOUT must be between 10 and 600 seconds")
        
        if cls.OLLAMA_MAX_RETRIES < 1 or cls.OLLAMA_MAX_RETRIES > 10:
            raise ValueError("OLLAMA_MAX_RETRIES must be between 1 and 10")
        
        if cls.MAX_FILE_SIZE_MB < 1 or cls.MAX_FILE_SIZE_MB > 1000:
            raise ValueError("MAX_FILE_SIZE_MB must be between 1 and 1000")
        
        if cls.MAX_INPUT_FILE_SIZE_MB < 1 or cls.MAX_INPUT_FILE_SIZE_MB > 1000:
            raise ValueError("MAX_INPUT_FILE_SIZE_MB must be between 1 and 1000")
        
        # Validate URL format
        if not cls.OLLAMA_BASE_URL.startswith(("http://", "https://")):
            raise ValueError("OLLAMA_BASE_URL must start with http:// or https://")
        
        logger.info("Configuration validated successfully")
    
    @classmethod
    def get_ollama_endpoint(cls, endpoint: str) -> str:
        """Get full Ollama API endpoint URL."""
        return f"{cls.OLLAMA_BASE_URL.rstrip('/')}/api/{endpoint}"


# Validate configuration on import
Config.validate()
