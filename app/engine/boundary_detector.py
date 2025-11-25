import asyncio
import json
from app.core.llm_gateway import LLMGateway
from app.core.prompts import LLM_BOUNDARY_DETECTION_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)

class BoundaryDetector:
    """
    Uses the LLMGateway to detect boundaries in raw text input by invoking the LLM with
    a prompt that instructs it to identify code boundaries in JSON format.
    """

    def __init__(self):
        self.llm_gateway = LLMGateway()

    async def detect_boundaries(self, raw_text: str) -> list:
        # Compose prompt with instructions and the raw input context (limited if needed)
        prompt = LLM_BOUNDARY_DETECTION_PROMPT + "\n\n" + raw_text[:10000]  # limit length for LLM

        try:
            response = await self.llm_gateway.post_boundary_request(prompt)
            # response expected to be JSON array as per prompt instructions
            boundaries = response if isinstance(response, list) else json.loads(response)
            logger.info(f"Detected {len(boundaries)} boundaries in text.")

            return boundaries
        except Exception as ex:
            logger.error(f"Error detecting boundaries with LLM: {ex}", exc_info=True)
            raise
        finally:
            await self.llm_gateway.close()
