from __future__ import annotations

from typing import Any, Dict, Optional

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("ia.local.ollama_client")


class OllamaClient:
    """Client minimal pour Ollama (LLM local)."""

    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        model = model or settings.LOCAL_LLM_MODEL
        url = f"{self.base_url}/api/generate"
        payload: Dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return (data.get("response") or "").strip()


ollama_client = OllamaClient()

