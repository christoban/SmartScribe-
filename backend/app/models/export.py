"""
Modèle pour les exports (PDF, DOCX, TXT)
"""
from typing import Optional
from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class Export(MongoBaseModel):
    """
    Modèle DB pour stocker les exports générés.
    """
    user_id: PyObjectId = Field(...)
    note_id: PyObjectId = Field(..., description="ID de la note exportée")
    
    format: str = Field(..., description="Format d'export: pdf, docx, txt")
    file_path: str = Field(..., description="Chemin du fichier exporté")
    file_size: int = Field(..., description="Taille du fichier en bytes")
    
    # Métadonnées
    generated_at: Optional[datetime] = Field(None, description="Date de génération")
    
    class Settings:
        name = "exports"
