from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Union

from groq import AsyncGroq

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("ia.groq_client")


class GroqAIClient:
    """
    Client Groq unifié:
    - STT (Whisper)
    - LLM (Llama) pour structuration / génération
    """

    def __init__(self) -> None:
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model_stt = "whisper-large-v3"
        # 💡 On sépare les modèles selon la difficulté de la tâche
        self.model_fast = "llama-3.1-8b-instant" 
        self.model_smart = "llama-3.3-70b-versatile"
        # 💡 SOLUTION : On définit model_llm pour qu'il pointe par défaut sur le modèle "smart"
        self.model_llm = self.model_smart

    async def transcribe(self, audio_path: Union[str, Path], lang: str = "fr") -> Dict[str, Any]:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Fichier audio introuvable : {path}")

        logger.info("🚀 Envoi Groq STT: %s", path.name)
        with path.open("rb") as f:
            response = await self.client.audio.transcriptions.create(
                file=(path.name, f.read()),
                model=self.model_stt,
                response_format="verbose_json",
                prompt="Ceci est un document académique sérieux, en français.",
                language=lang,
                temperature=0.0,
            )

        return {"text": response.text, "segments": response.segments, "language": lang}
    
    async def refine_text(self, raw_text: str) -> str:
        """Correction rapide avec le modèle 8b."""
        completion = await self.client.chat.completions.create(
            model=self.model_fast, # 🚀 Gain de vitesse énorme
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert en transcription académique. "
                        "Corrige les erreurs phonétiques, améliore la ponctuation, "
                        "supprime les répétitions. Réponds uniquement par le texte corrigé."
                    ),
                },
                {"role": "user", "content": raw_text},
            ],
            temperature=0.1,
            max_tokens=4096 # Sécurité
        )
        return completion.choices[0].message.content or raw_text

    async def generate_completion(self, prompt: str, system_msg: str = "Tu es un assistant utile.", temperature: float = 0.2) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model_llm,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return completion.choices[0].message.content or ""

    @staticmethod
    def generate_stable_hash(content: str) -> str:
        return hashlib.md5(content.encode("utf-8")).hexdigest()


groq_client = GroqAIClient()

