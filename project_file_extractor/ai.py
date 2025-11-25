import requests
from typing import Iterator, Optional

SYSTEM_PROMPT = """
You are a File Extraction Agent. Your ONLY task is to parse and organize existing code.

STRICT RULES:
1. ONLY extract code that already exists in the input text
2. DO NOT generate new code, implementations, or complete incomplete functions
3. DO NOT fill in TODOs, comments, or missing code
4. DO NOT modify, improve, or fix existing code
5. Copy code EXACTLY as provided - character for character
6. Identify file paths based on context clues in the input
7. If the input contains descriptions/instructions instead of actual code, output nothing

OUTPUT FORMAT (for existing code only):
<<<FILE_START>>>path/to/filename.ext<<<Header_End>>>
[Exact code from input - no modifications]
<<<FILE_END>>>

If input has no actual code to extract, respond with: "No code found to organize"
"""

MAX_CONTEXT_SIZE = 131072

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
