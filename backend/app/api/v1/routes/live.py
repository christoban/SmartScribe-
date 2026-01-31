"""
Routes pour le mode Live (transcription en temps réel)
"""
import uuid
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.api.deps import get_current_user
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.live")

@router.post("/start")
async def start_live_session(
    content_type: str = None,  # Optionnel : type de contenu (cours, podcast, etc.)
    current_user = Depends(get_current_user)
):
    """
    Démarre une session de transcription en temps réel
    content_type: Type de contenu (optionnel) - cours, podcast, tutoriel, etc.
    """
    session_id = str(uuid.uuid4())
    logger.info("🎙️ Démarrage session Live %s pour user=%s", session_id, current_user.id)
    
    # TODO: Créer une session en base de données
    # TODO: Initialiser le transcriber en mode streaming
    
    return {
        "session_id": session_id,
        "status": "started",
        "message": "Session Live démarrée. Connectez-vous via WebSocket pour envoyer l'audio."
    }

@router.post("/stop/{session_id}")
async def stop_live_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Arrête une session Live et génère les notes finales"""
    logger.info("🛑 Arrêt session Live %s", session_id)
    
    # TODO: Arrêter le transcriber
    # TODO: Générer les notes finales
    # TODO: Sauvegarder en base
    
    return {
        "session_id": session_id,
        "status": "stopped",
        "message": "Session arrêtée. Notes en cours de génération."
    }

@router.websocket("/stream/{session_id}")
async def websocket_live_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket pour recevoir l'audio en streaming et renvoyer la transcription
    """
    await websocket.accept()
    logger.info("🔌 Connexion WebSocket pour session %s", session_id)
    
    try:
        while True:
            # Réception de l'audio (chunks)
            data = await websocket.receive_bytes()
            
            # TODO: Traiter le chunk audio
            # TODO: Transcrire en temps réel
            # TODO: Envoyer la transcription partielle
            
            # Exemple de réponse
            await websocket.send_json({
                "text": "Transcription partielle...",
                "is_final": False
            })
            
    except WebSocketDisconnect:
        logger.info("🔌 Déconnexion WebSocket pour session %s", session_id)
