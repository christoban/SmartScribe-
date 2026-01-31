"""
Regroupe tous les routeurs de l'API v1
"""
from fastapi import APIRouter
from app.api.v1.routes import (
    auth,
    users,
    media,
    live,
    transcription,
    notes,
    export,
    history,
    websocket,
    health
)

api_router = APIRouter()

# Inclusion de tous les routeurs
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(users.router, prefix="/users", tags=["Utilisateurs"])
api_router.include_router(media.router, prefix="/media", tags=["Média & Upload"])
api_router.include_router(live.router, prefix="/live", tags=["Mode Live"])
api_router.include_router(transcription.router, prefix="/transcription", tags=["Transcription"])
api_router.include_router(notes.router, prefix="/notes", tags=["Notes & Structuration"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(history.router, prefix="/history", tags=["Historique"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(health.router, prefix="/health", tags=["Health Check"])
