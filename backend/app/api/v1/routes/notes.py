"""
Routes pour la structuration et génération de notes intelligentes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.api.deps import get_current_user
from app.db.repositories.note_repo import NoteRepository
from app.db.repositories.transcription_repo import TranscriptionRepository
from app.db.mongo import get_database
from app.schemas.note import NoteOut, NoteUpdate
from app.core.logger import get_logger
from app.services.ia.manager import ia_manager
from app.services.nlp.text_cleaner import text_cleaner
from app.models.note import Note

router = APIRouter()
logger = get_logger("routes.notes")


@router.post("/generate/{transcription_id}", response_model=NoteOut)
async def generate_notes(
    transcription_id: str,
    content_type: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    repo_trans = TranscriptionRepository(db)
    repo_note = NoteRepository(db)

    transcription = await repo_trans.get_by_id(transcription_id)
    if not transcription or str(transcription.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Transcription introuvable")

    logger.info("📝 Génération de notes pour transcription %s", transcription_id)

    effective_content_type = content_type or "auto"
    if effective_content_type == "auto":
        effective_content_type = await ia_manager.detect_content_type(transcription.text)

    generated = await ia_manager.generate_notes(
        transcription=transcription.text,
        content_type=effective_content_type,
        visual_context=getattr(transcription, "visual_context", "") or "",
    )

    generated = text_cleaner.clean(generated)

    new_note = Note(
        transcription_id=transcription_id,
        user_id=str(current_user.id),
        title=f"Notes - {effective_content_type.capitalize()}",
        content=generated,
        content_type=effective_content_type,
        status="completed",
        model_used="llama-3.3-70b",
    )

    saved_note = await repo_note.create(new_note)
    return saved_note


@router.get("/", response_model=List[NoteOut])
async def list_notes(
    transcription_id: Optional[str] = None,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Liste toutes les notes de l'utilisateur"""
    repo_note = NoteRepository(db)

    if transcription_id:
        return await repo_note.get_by_transcription_id(transcription_id, str(current_user.id))

    return await repo_note.get_user_notes(str(current_user.id))


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(
    note_id: str,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Récupère une note spécifique"""
    repo_note = NoteRepository(db)
    note = await repo_note.get_by_id(note_id)

    if not note or str(note.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Note non trouvée")

    return note


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Met à jour une note"""
    repo_note = NoteRepository(db)
    note = await repo_note.get_by_id(note_id)

    if not note or str(note.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Note non trouvée")

    updated_note = await repo_note.update(note_id, note_update)
    return updated_note


@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Supprime une note"""
    repo_note = NoteRepository(db)
    note = await repo_note.get_by_id(note_id)

    if not note or str(note.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Note non trouvée")

    await repo_note.delete(note_id)
    return {"status": "deleted", "id": note_id}


@router.post("/{note_id}/regenerate")
async def regenerate_note(
    note_id: str,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Régénère une note avec les paramètres actuels"""
    repo_note = NoteRepository(db)
    note = await repo_note.get_by_id(note_id)

    if not note or str(note.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Note non trouvée")

    logger.info("🔄 Régénération de la note %s", note_id)

    # Tu pourras brancher ici un vrai pipeline plus tard
    return {"status": "regenerating", "note_id": note_id}

@router.get("/", response_model=List[NoteOut])  
async def list_notes(  
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),  
    limit: int = Query(20, ge=1, le=100, description="Nombre d'éléments à retourner"),  
    transcription_id: Optional[str] = None,  
    current_user=Depends(get_current_user),  
    db=Depends(get_database),  
):  
    """Liste toutes les notes de l'utilisateur avec pagination"""  
    repo_note = NoteRepository(db)  
  
    if transcription_id:  
        # Si transcription_id fourni, on filtre par transcription  
        # Note: get_by_transcription_id ne supporte pas skip/limit actuellement  
        return await repo_note.get_by_transcription_id(transcription_id, str(current_user.id))  
  
    # Pagination pour toutes les notes de l'utilisateur  
    return await repo_note.get_user_notes(str(current_user.id), skip=skip, limit=limit)
