import requests
from typing import Iterator, Optional

SYSTEM_PROMPT = """
You are a File Extraction Agent. Your task is to parse unstructured text.
Rules:
1. Identify every file and its path based on context.
2. Output code EXACTLY as provided.
3. YOU MUST USE THIS FORMAT for every file:
<<<FILE_START>>>path/to/filename.ext<<<Header_End>>>
[File Content Here]
<<<FILE_END>>>
"""

MAX_CONTEXT_SIZE = 131072  # Use 128k as the new default

class OllamaClientError(Exception):
    pass

class OllamaClient:
    def __init__(self, model: str = "qwen2.5-coder:7b", host: str = "http://localhost:11434", context_size: int = MAX_CONTEXT_SIZE):
        self.model = model
        self.host = host
        self.context_size = context_size

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        url = f"{self.host}/api/generate"
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {"context_size": self.context_size}
        }
        if system_prompt:
            body["system"] = system_prompt
        try:
            with requests.post(url, json=body, stream=True, timeout=180) as resp:
                if not resp.ok:
                    raise OllamaClientError(f"Ollama error: {resp.status_code} {resp.text}")
                for line in resp.iter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line.decode())
                            if isinstance(data, dict) and "response" in data:
                                yield data["response"]
                        except Exception:
                            continue
        except requests.RequestException as e:
            raise OllamaClientError(f"Failed to connect to Ollama: {e}")
