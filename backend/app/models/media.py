from typing import Optional, List
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class Media(MongoBaseModel):
    """
    Modèle DB pour stocker les médias.
    Hérite de MongoBaseModel pour la gestion automatique des IDs et Dates.
    """
    user_id: PyObjectId = Field(...)
    filename: str = Field(...)
    file_type: str = Field(..., description="ex: mp3, wav, mp4")
    media_type: str = Field(..., description="audio, video, document")
    file_path: str = Field(...)
    size: int = Field(..., description="Taille en bytes")
    
    # Métadonnées optionnelles ou calculées plus tard
    duration: Optional[float] = Field(None, description="Durée en secondes")
    status: str = Field(default="uploaded", description="uploaded, processing, completed, error")
    
    # Pipeline IA
    cleaned_path: Optional[str] = Field(None, description="Chemin de l'audio après NoiseCleaner")

    class Settings:
        name = "media" # Utile si tu utilises Beanie plus tard