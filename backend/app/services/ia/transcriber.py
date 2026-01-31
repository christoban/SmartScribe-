from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Union

from app.core.logger import get_logger
from app.services.ia.groq_client import groq_client

logger = get_logger("ia.transcriber")

# Limite officielle de l'API Groq Whisper (25 Mo)
GROQ_AUDIO_SIZE_LIMIT = 25 * 1024 * 1024 

class Transcriber:
    async def process_audio_to_text(self, audio_path: Union[str, Path]) -> Dict[str, Any]:
        path = Path(audio_path)
        
        # --- VÉRIFICATION DE LA TAILLE ---
        file_size = os.path.getsize(path)
        if file_size > GROQ_AUDIO_SIZE_LIMIT:
            logger.error("❌ Fichier trop volumineux (%s Mo). Limite Groq: 25 Mo.", file_size / (1024*1024))
            # TODO: Implémenter le chunking (Mois 6)
            return {
                "error": "FILE_TOO_LARGE",
                "message": "Le fichier audio dépasse la limite de 25 Mo. Le découpage automatique sera disponible au Mois 6."
            }

        logger.info("🎤 Début transcription: %s (%s Mo)", path.name, round(file_size / (1024*1024), 2))

        # 1. Transcription brute
        raw_data = await groq_client.transcribe(path)
        
        if not raw_data.get("text"):
            return self._empty_response()

        # 2. Raffinage
        refined_text = await groq_client.refine_text(raw_data["text"])

        return {
            "raw_text": raw_data["text"],
            "refined_text": refined_text,
            "segments": raw_data.get("segments", []),
            "language": raw_data.get("language", "fr"),
        }

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "raw_text": "",
            "refined_text": "Aucun contenu audio détecté.",
            "segments": [],
            "language": "fr",
        }

transcriber = Transcriber()