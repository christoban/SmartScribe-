"""
Schémas Pydantic pour les notes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_type: str = Field(default="auto", max_length=50)


class NoteCreate(NoteBase):
    user_id: str
    transcription_id: str
    media_id: Optional[str] = None

    generation_params: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = Field(None, max_length=50)

    summary: Optional[str] = None
    qcm: Optional[List[Dict[str, Any]]] = None
    flashcards: Optional[List[Dict[str, Any]]] = None
    exercises: Optional[List[Dict[str, Any]]] = None

    status: Optional[str] = Field(None, max_length=30)


class NoteOut(NoteBase):
    id: str  # <-- exposé côté API
    user_id: str
    transcription_id: str
    media_id: Optional[str] = None

    summary: Optional[str] = None
    qcm: Optional[List[Dict[str, Any]]] = None
    flashcards: Optional[List[Dict[str, Any]]] = None
    exercises: Optional[List[Dict[str, Any]]] = None

    status: str = "draft"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

