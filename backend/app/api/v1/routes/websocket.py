"""  
Routes WebSocket pour la communication en temps réel  
"""  
from fastapi import APIRouter, WebSocket, WebSocketDisconnect  
from pathlib import Path  
import tempfile  
import uuid  
from app.core.logger import get_logger  
from app.db.mongo import get_database  
from app.db.repositories.transcription_repo import TranscriptionRepository  
from app.models.transcription import Transcription  
from app.services.ia.transcriber import transcriber  
  
router = APIRouter()  
logger = get_logger("routes.websocket")  
  
class ConnectionManager:  
    """Gère les connexions WebSocket"""  
    def __init__(self):  
        self.active_connections: dict[str, WebSocket] = {}  
        # Stockage des transcriptions en cours par session_id  
        self.active_transcriptions: dict[str, str] = {}  # session_id -> transcription_id  
        # Buffer audio temporaire par session  
        self.audio_buffers: dict[str, list] = {}  
      
    async def connect(self, websocket: WebSocket, session_id: str):  
        await websocket.accept()  
        self.active_connections[session_id] = websocket  
        self.audio_buffers[session_id] = []  
        logger.info("🔌 Connexion WebSocket établie: %s", session_id)  
      
    def disconnect(self, session_id: str):  
        if session_id in self.active_connections:  
            del self.active_connections[session_id]  
        if session_id in self.audio_buffers:  
            del self.audio_buffers[session_id]  
        if session_id in self.active_transcriptions:  
            del self.active_transcriptions[session_id]  
        logger.info("🔌 Déconnexion WebSocket: %s", session_id)  
      
    async def send_personal_message(self, message: dict, session_id: str):  
        if session_id in self.active_connections:  
            await self.active_connections[session_id].send_json(message)  
      
    async def broadcast(self, message: dict):  
        for connection in self.active_connections.values():  
            await connection.send_json(message)  
  
manager = ConnectionManager()  
  
@router.websocket("/live/{session_id}")  
async def websocket_live_transcription(websocket: WebSocket, session_id: str):  
    """  
    WebSocket pour la transcription en temps réel  
    Reçoit les chunks audio, transcrit, et renvoie la transcription partielle  
    """  
    await manager.connect(websocket, session_id)  
      
    # Créer une transcription en DB dès la connexion  
    db = get_database()  
    transcription_repo = TranscriptionRepository(db)  
      
    # Créer la transcription initiale  
    transcription = Transcription(  
        user_id=session_id,  # Temporaire - sera mis à jour par /live/start  
        media_id=session_id,  
        text="",  
        raw_text="",  
        visual_context=None,  
        segments=[],  
        language="fr",  
        model_name="whisper-large-v3",  
        status="processing"  
    )  
      
    saved_transcription = await transcription_repo.create(transcription)  
    transcription_id = str(saved_transcription.id)  
    manager.active_transcriptions[session_id] = transcription_id  
      
    logger.info("📝 Transcription créée: %s pour session %s", transcription_id, session_id)  
      
    # Accumulateur de texte  
    accumulated_text = ""  
    chunk_count = 0  
      
    try:  
        while True:  
            # Réception de données audio (chunks)  
            data = await websocket.receive_bytes()  
            chunk_count += 1  
              
            logger.info("🎙️ Chunk audio reçu #%d (%d bytes) pour session %s",   
                       chunk_count, len(data), session_id)  
              
            # Accumuler les chunks audio  
            manager.audio_buffers[session_id].append(data)  
              
            # Traiter tous les 3 chunks pour éviter trop d'appels API  
            if len(manager.audio_buffers[session_id]) >= 3:  
                # Créer un fichier temporaire avec les chunks accumulés  
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_audio:  
                    for chunk in manager.audio_buffers[session_id]:  
                        temp_audio.write(chunk)  
                    temp_audio_path = Path(temp_audio.name)  
                  
                try:  
                    # Transcrire le chunk audio  
                    logger.info("🔄 Transcription du chunk audio...")  
                    result = await transcriber.process_audio_to_text(temp_audio_path)  
                      
                    if result.get("refined_text"):  
                        partial_text = result["refined_text"]  
                        accumulated_text += " " + partial_text  
                          
                        # Mettre à jour la transcription en DB  
                        await transcription_repo.update(transcription_id, {  
                            "text": accumulated_text.strip(),  
                            "raw_text": accumulated_text.strip(),  
                            "segments": result.get("segments", []),  
                            "language": result.get("language", "fr")  
                        })  
                          
                        # Envoyer la transcription partielle au frontend  
                        await manager.send_personal_message({  
                            "type": "transcription_partial",  
                            "text": partial_text,  
                            "accumulated_text": accumulated_text.strip(),  
                            "is_final": False,  
                            "timestamp": None  
                        }, session_id)  
                          
                        logger.info("✅ Transcription partielle envoyée: %s", partial_text[:50])  
                      
                except Exception as e:  
                    logger.error("❌ Erreur transcription: %s", e)  
                    await manager.send_personal_message({  
                        "type": "error",  
                        "message": f"Erreur de transcription: {str(e)}"  
                    }, session_id)  
                  
                finally:  
                    # Nettoyer le fichier temporaire  
                    if temp_audio_path.exists():  
                        temp_audio_path.unlink()  
                    # Vider le buffer  
                    manager.audio_buffers[session_id] = []  
              
    except WebSocketDisconnect:  
        manager.disconnect(session_id)  
        logger.info("🔌 WebSocket déconnecté: %s", session_id)  
  
@router.websocket("/status/{job_id}")  
async def websocket_job_status(websocket: WebSocket, job_id: str):  
    """  
    WebSocket pour suivre le statut d'un job de traitement  
    """  
    await manager.connect(websocket, job_id)  
      
    try:  
        while True:  
            # TODO: Envoyer les mises à jour de statut du job  
            await manager.send_personal_message({  
                "type": "status_update",  
                "job_id": job_id,  
                "status": "processing",  
                "progress": 0.5  
            }, job_id)  
              
            # Attendre un peu avant la prochaine mise à jour  
            import asyncio  
            await asyncio.sleep(1)  
              
    except WebSocketDisconnect:  
        manager.disconnect(job_id)