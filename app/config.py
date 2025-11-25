import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Externalize configuration via env vars for security and flexibility
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", "https://llm.api/endpoint")  # Placeholder endpoint

settings = Settings()
