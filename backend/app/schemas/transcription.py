from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator

# Type personnalisé pour gérer les ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

def get_now():
    """Génère un timestamp UTC conscient du fuseau horaire (offset-aware)"""
    return datetime.now(timezone.utc)

# -------------------------------
# 🔹 Segments pour API
# -------------------------------
class SegmentSchema(BaseModel):
    start_time: float
    end_time: float
    text: str
    speaker_id: str = "Unknown"

# -------------------------------
# 🔹 Transcription API
# -------------------------------
class TranscriptionBase(BaseModel):
    media_id: PyObjectId
    user_id: Optional[PyObjectId] = None
    language: str = "fr"
    model_name: str = Field(..., alias="model")

class TranscriptionCreate(TranscriptionBase):
    text: str
    segments: List[SegmentSchema] = []
    raw_text: Optional[str] = None
    visual_context: Optional[str] = None

class TranscriptionUpdate(BaseModel):
    text: Optional[str] = None
    segments: Optional[List[SegmentSchema]] = None
    # Correction ici : Utilisation de la factory get_now
    updated_at: datetime = Field(default_factory=get_now)

class TranscriptionOut(TranscriptionBase):
    id: PyObjectId = Field(alias="_id")
    text: str
    segments: List[Dict[str, Any]] = []
    raw_text: Optional[str] = None
    visual_context: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True, # Très important pour transformer les modèles Mongo en Schemas
    }