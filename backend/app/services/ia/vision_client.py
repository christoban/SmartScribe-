from __future__ import annotations

from pathlib import Path
from typing import List

from app.core.logger import get_logger
from app.services.media.ocr_engine import ocr_engine
import asyncio


logger = get_logger("ia.vision_client")



class VisionClient:
    """
    Client "Vision" (côté IA).

    Dans cette V1, on s'appuie sur l'OCR local (Tesseract/PaddleOCR) via `services.media.ocr_engine`.
    Ce module sert de point d'extension pour brancher plus tard un modèle vision cloud (GPT-4o, LLaVA, etc.).
    """
    async def get_visual_context(self, image_paths: List[Path]) -> str:
        if not image_paths:
            return ""

        # ✅ On délègue à un thread pour ne pas bloquer l'Event Loop
        extracted = await asyncio.to_thread(
            ocr_engine.extract_text_from_keyframes, 
            image_paths
        )
        
        lines = [t.strip() for t in extracted.values() if t and t.strip()]
        unique_lines = list(dict.fromkeys(lines))
        
        # Sécurité : On limite à 5000 caractères de contexte visuel pour Groq
        full_context = "\n".join(unique_lines)
        return full_context[:5000] if len(full_context) > 5000 else full_context


vision_client = VisionClient()

 
