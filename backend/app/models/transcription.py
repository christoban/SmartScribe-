from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel, PyObjectId


class Segment(BaseModel):
    """
    Segment de transcription (optionnel).

    Note: selon le provider STT, le schéma peut varier. Dans la DB, on accepte aussi
    des segments bruts (dict) via `Transcription.segments`.
    """

    start_time: float
    end_time: float
    text: str
    speaker_id: str = "Unknown"


class Transcription(MongoBaseModel):
    """Document stocké dans la collection `transcriptions`."""
    status: str = "pending"  # 👈 Indispensable pour la cohérence avec le Repo

    user_id: Optional[PyObjectId] = None
    media_id: PyObjectId

    # STT
    raw_text: Optional[str] = None
    text: str  # transcription "refined"
    segments: List[Dict[str, Any]] = Field(default_factory=list)

    # Vision/OCR
    visual_context: Optional[str] = None

    language: str = "fr"
    model_name: str = Field(..., alias="model")