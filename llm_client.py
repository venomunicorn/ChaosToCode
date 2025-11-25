"""Ollama LLM client with retry logic and error handling."""

import requests
import json
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """Initialize Ollama client with configuration."""
        self.base_url = (base_url or Config.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or Config.OLLAMA_MODEL
        self.timeout = timeout or Config.OLLAMA_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        logger.info(f"Initialized Ollama client: {self.base_url}, model: {self.model}")
    
    def check_connection(self) -> bool:
        """Check if Ollama server is accessible."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            logger.info("Ollama server connection successful")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Ollama server: {e}")
            return False
    
    def list_models(self) -> list:
        """List available models."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            logger.info(f"Available models: {models}")
            return models
        except requests.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    @retry(
        stop=stop_after_attempt(Config.OLLAMA_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion from Ollama with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        
        Raises:
            requests.RequestException: On API error
            ValueError: On invalid response
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Prompt cannot be empty")
        
        if temperature < 0 or temperature > 1:
            raise ValueError("Temperature must be between 0 and 1")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        logger.info(f"Generating completion (prompt length: {len(prompt)} chars)")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            if not generated_text:
                raise ValueError("Empty response from LLM")
            
            logger.info(f"Generated response (length: {len(generated_text)} chars)")
            return generated_text
            
        except requests.Timeout:
            logger.error(f"Request timeout after {self.timeout}s")
            raise
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise ValueError("Invalid JSON response from Ollama")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
        logger.info("Ollama client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
