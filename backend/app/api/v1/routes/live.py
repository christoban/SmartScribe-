"""  
Routes pour le mode Live (transcription en temps réel)  
"""  
import uuid  
from fastapi import APIRouter, Depends, HTTPException  
from app.api.deps import get_current_user  
from app.core.logger import get_logger  
from app.db.mongo import get_database  
from app.db.repositories.transcription_repo import TranscriptionRepository  
from app.api.v1.routes.websocket import manager  
  
router = APIRouter()  
logger = get_logger("routes.live")  
  
@router.post("/start")  
async def start_live_session(  
    content_type: str = None,  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  
):  
    """  
    Démarre une session de transcription en temps réel  
    """  
    session_id = str(uuid.uuid4())  
    logger.info("🎙️ Démarrage session Live %s pour user=%s", session_id, current_user.id)  
      
    # La transcription sera créée lors de la connexion WebSocket  
    # On stocke juste l'association user_id -> session_id  
      
    return {  
        "session_id": session_id,  
        "status": "started",  
        "user_id": str(current_user.id),  
        "websocket_url": f"/api/v1/ws/live/{session_id}",  
        "message": "Session Live démarrée. Connectez-vous via WebSocket pour envoyer l'audio."  
    }  
  
@router.post("/stop/{session_id}")  
async def stop_live_session(  
    session_id: str,  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  
):  
    """Arrête une session Live et finalise la transcription"""  
    logger.info("🛑 Arrêt session Live %s", session_id)  
      
    # Récupérer la transcription associée  
    if session_id in manager.active_transcriptions:  
        transcription_id = manager.active_transcriptions[session_id]  
        transcription_repo = TranscriptionRepository(db)  
          
        # Marquer comme completed  
        await transcription_repo.update(transcription_id, {  
            "status": "completed",  
            "user_id": str(current_user.id)  # Mettre à jour avec le vrai user_id  
        })  
          
        # Nettoyer la session  
        manager.disconnect(session_id)  
          
        logger.info("✅ Transcription %s finalisée", transcription_id)  
          
        return {  
            "session_id": session_id,  
            "transcription_id": transcription_id,  
            "status": "stopped",  
            "message": "Session arrêtée. Transcription sauvegardée."  
        }  
    else:  
        raise HTTPException(status_code=404, detail="Session non trouvée")