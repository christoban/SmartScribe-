from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class MediaBase(BaseModel):
    filename: str
    file_type: str
    media_type: str
    size: int
    duration: Optional[float] = None

class MediaCreate(MediaBase):
    user_id: str
    file_path: str

class MediaUpdate(BaseModel):
    status: Optional[str] = None
    duration: Optional[float] = None
    cleaned_path: Optional[str] = None
    chunks: Optional[List[str]] = None

class MediaOut(MediaBase):
    id: str
    status: str
    created_at: datetime
    # On ajoute ces champs pour que le front sache où en est le traitement
    cleaned_path: Optional[str] = None
    chunks: List[str] = []

    model_config = ConfigDict(from_attributes=True)