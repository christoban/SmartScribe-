"""
Schémas Pydantic pour les exports
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ExportBase(BaseModel):
    """Schéma de base pour un export"""
    format: str = Field(..., pattern="^(pdf|docx|txt)$")
    note_id: str

class ExportCreate(ExportBase):
    """Schéma pour la création d'un export"""
    user_id: str
    file_path: str
    file_size: int

class ExportOut(ExportBase):
    """Schéma de sortie pour un export"""
    id: str = Field(..., alias="_id")
    user_id: str
    file_path: str
    file_size: int
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True, "populate_by_name": True}
