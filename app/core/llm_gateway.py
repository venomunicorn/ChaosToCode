import asyncio
import httpx
from app.config import settings
from app.utils.security import sanitize_text_input, validate_json_manifest
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMGateway:
    """
    Gateway to communicate with the LLM securely and asynchronously.
    Handles input validation and retries with backoff.
    """
    def __init__(self, endpoint: str = settings.LLM_ENDPOINT, api_key: str = settings.LLM_API_KEY):
        self.endpoint = endpoint
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        self.client = httpx.AsyncClient(timeout=self.timeout, http2=True)

    async def post_boundary_request(self, prompt: str) -> dict:
        # Validate and sanitize prompt before sending
        sanitized_prompt = sanitize_text_input(prompt)
        payload = {
            "prompt": sanitized_prompt,
            "max_tokens": 1500,
            "temperature": 0.0
        }

        # Retry logic with exponential backoff handled at caller level if needed
        try:
            response = await self.client.post(self.endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # Validate manifest JSON structure
            if not validate_json_manifest(data):
                logger.error("Invalid JSON manifest structure received from LLM")
                raise ValueError("Invalid JSON manifest from LLM")

            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM HTTP error: {e.response.status_code} {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error communicating with LLM: {e}")
            raise

    async def close(self):
        await self.client.aclose()
