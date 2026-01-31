from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.core.logger import get_logger
from contextlib import asynccontextmanager
from app.core.redis_cache import redis_cache
from app.api.v1.api import api_router

logger = get_logger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- DÉMARRAGE ---
    logger.info("🚀 Initialisation de SmartScribe...")
    await connect_to_mongo()
    await redis_cache.connect() # 👈 Ajoute ceci
    yield
    # --- ARRÊT ---
    logger.info("🛑 Fermeture de SmartScribe...")
    await redis_cache.disconnect() # 👈 Et ceci
    await close_mongo_connection()

app = FastAPI(
    title="SmartScribe API",
    description="Système multimodal d'extraction de notes de cours (Audio + Vision)",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS (Essentiel pour ton futur Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DES ROUTES ---
# Utilisation du routeur principal qui regroupe toutes les routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)