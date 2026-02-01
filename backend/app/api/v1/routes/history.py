"""  
Routes pour l'historique et la recherche  
"""  
from fastapi import APIRouter, Depends, Query  
from typing import Optional, List  
from app.api.deps import get_current_user  
from app.db.repositories.media_repo import MediaRepository  
from app.db.repositories.transcription_repo import TranscriptionRepository  
from app.db.repositories.note_repo import NoteRepository  
from app.db.mongo import get_database  
from app.core.logger import get_logger  
  
router = APIRouter()  
logger = get_logger("routes.history")  
  
@router.get("/media")  
async def get_media_history(  
    skip: int = Query(0, ge=0),  
    limit: int = Query(20, ge=1, le=100),  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    """Récupère l'historique des médias de l'utilisateur"""  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    media_repo = MediaRepository(db)  
    media_list = await media_repo.get_user_media(str(current_user.id))  
    return media_list[skip:skip+limit]  
  
@router.get("/transcriptions")  
async def get_transcription_history(  
    skip: int = Query(0, ge=0),  
    limit: int = Query(20, ge=1, le=100),  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 Dépendance déjà présente, cohérence maintenue  
):  
    """Récupère l'historique des transcriptions"""  
    repo = TranscriptionRepository(db)  
    # TODO: Implémenter get_user_transcriptions dans TranscriptionRepository  
    # transcriptions = await repo.get_user_transcriptions(str(current_user.id), skip=skip, limit=limit)  
    return []  
  
@router.get("/notes")  
async def get_notes_history(  
    skip: int = Query(0, ge=0),  
    limit: int = Query(20, ge=1, le=100),  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    """Récupère l'historique des notes"""  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    note_repo = NoteRepository(db)  
    notes = await note_repo.get_user_notes(str(current_user.id), skip=skip, limit=limit)  
    return notes  
  
@router.get("/search")  
async def search_content(  
    query: str = Query(..., min_length=1, description="Terme de recherche"),  
    content_type: Optional[str] = Query(None, description="Type: media, transcription, note"),  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 Dépendance déjà présente, cohérence maintenue  
):  
    """  
    Recherche dans le contenu de l'utilisateur  
    """  
    results = {}  
      
    if not content_type or content_type == "media":  
        # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
        media_repo = MediaRepository(db)  
        # TODO: Implémenter la recherche dans les médias  
        results["media"] = []  
      
    if not content_type or content_type == "transcription":  
        transcription_repo = TranscriptionRepository(db)  
        # TODO: Implémenter la recherche dans les transcriptions  
        results["transcriptions"] = []  
      
    if not content_type or content_type == "note":  
        # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
        note_repo = NoteRepository(db)  
        # TODO: Implémenter la recherche dans les notes  
        results["notes"] = []  
      
    logger.info("🔍 Recherche '%s' pour user=%s", query, current_user.id)  
      
    return {  
        "query": query,  
        "results": results  
    }