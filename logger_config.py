"""Centralized logging configuration with security filters."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import Config


class SensitiveDataFilter(logging.Filter):
    """Filter to prevent logging sensitive data."""
    
    SENSITIVE_PATTERNS = [
        'password',
        'token',
        'secret',
        'api_key',
        'credential',
        'auth',
        'bearer',
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record for sensitive data."""
        message = record.getMessage().lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                record.msg = f"[REDACTED - Contains sensitive data: {pattern}]"
                record.args = ()
        return True


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """Setup logger with file and console handlers."""
    
    logger = logging.getLogger(name)
    log_level = getattr(logging, level or Config.LOG_LEVEL)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = Config.LOG_DIR / f"project_extractor_{timestamp}.log"
    
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        file_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to setup file logging: {e}")
    
    return logger


# Global logger
logger = setup_logger(__name__)
