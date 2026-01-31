"""
Routes WebSocket pour la communication en temps réel
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.websocket")

class ConnectionManager:
    """Gère les connexions WebSocket"""
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("🔌 Connexion WebSocket établie: %s", session_id)
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
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
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Réception de données audio (chunks)
            data = await websocket.receive_bytes()
            
            # TODO: Traiter le chunk audio
            # TODO: Transcrire en temps réel
            # TODO: Envoyer la transcription partielle
            
            # Exemple de réponse
            await manager.send_personal_message({
                "type": "transcription_partial",
                "text": "Transcription partielle...",
                "is_final": False,
                "timestamp": None
            }, session_id)
            
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
