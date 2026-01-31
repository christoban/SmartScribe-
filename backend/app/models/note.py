"""
Modèle pour les notes structurées (DB / Mongo)
"""
from typing import Optional, List
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId


class Note(MongoBaseModel):
    """
    Modèle DB pour stocker les notes structurées.
    """
    user_id: PyObjectId = Field(...)
    transcription_id: PyObjectId = Field(..., description="ID de la transcription source")
    media_id: Optional[PyObjectId] = Field(None, description="ID du média source")

    title: str = Field(..., description="Titre de la note")
    content: str = Field(..., description="Contenu structuré de la note (Markdown)")
    content_type: str = Field(default="auto", description="Type de contenu: cours, podcast, tutoriel, etc.")

    # Métadonnées IA
    generation_params: Optional[dict] = Field(None)
    model_used: Optional[str] = Field(None)

    # Supports pédagogiques
    summary: Optional[str] = None
    qcm: Optional[List[dict]] = None
    flashcards: Optional[List[dict]] = None
    exercises: Optional[List[dict]] = None

    status: str = Field(default="draft", description="draft, completed, published")

    class Settings:
        name = "notes"
