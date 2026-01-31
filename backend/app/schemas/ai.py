"""
Schémas Pydantic pour les requêtes IA
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class ContentTypeDetectionRequest(BaseModel):
    """Requête pour la détection automatique du type de contenu"""
    transcription: str = Field(..., min_length=10)

class ContentTypeDetectionResponse(BaseModel):
    """Réponse de détection du type de contenu"""
    content_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class NoteGenerationRequest(BaseModel):
    """Requête pour la génération de notes"""
    transcription_id: str
    content_type: Optional[str] = None
    custom_instructions: Optional[str] = None
    generate_summary: bool = True
    generate_qcm: bool = False
    generate_flashcards: bool = False
    generate_exercises: bool = False

class QCMGenerationRequest(BaseModel):
    """Requête pour la génération d'un QCM"""
    transcription_id: str
    num_questions: int = Field(default=10, ge=1, le=50)

class FlashcardGenerationRequest(BaseModel):
    """Requête pour la génération de flashcards"""
    transcription_id: str
    num_cards: int = Field(default=20, ge=1, le=100)

class ExerciseGenerationRequest(BaseModel):
    """Requête pour la génération d'exercices"""
    transcription_id: str
    num_exercises: int = Field(default=5, ge=1, le=20)
    difficulty: Optional[str] = Field(None, pattern="^(facile|moyen|difficile)$")
