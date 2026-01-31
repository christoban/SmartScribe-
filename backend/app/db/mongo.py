from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("database")


class MongoDB:
    """Conteneur global de connexion (API + worker)."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db_instance = MongoDB()


async def connect_to_mongo() -> None:
    """Initialise la connexion Mongo (idempotent)."""
    if db_instance.client is not None and db_instance.db is not None:
        return

    logger.info("📡 Connexion à MongoDB en cours...")
    try:
        # Optimisation du Pool pour les traitements lourds (IA)
        db_instance.client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=50,
            # En dev/CI, minPoolSize élevé ouvre trop de connexions inutiles
            minPoolSize=0,
            serverSelectionTimeoutMS=5000,
        )
        
        await db_instance.client.admin.command("ping")
        db_instance.db = db_instance.client[settings.MONGO_DB_NAME]
        
        logger.info("✅ MongoDB opérationnel : %s", settings.MONGO_DB_NAME)
    except Exception as e:  # noqa: BLE001 (on encapsule en ConnectionError)
        logger.error("❌ Échec critique MongoDB : %s", e)
        db_instance.client = None
        db_instance.db = None
        raise ConnectionError(f"Impossible de joindre MongoDB : {e}") from e


async def close_mongo_connection() -> None:
    """Ferme proprement la connexion Mongo."""
    if db_instance.client is not None:
        db_instance.client.close()
        db_instance.client = None
        db_instance.db = None
        logger.info("🔌 Connexion MongoDB fermée proprement.")


def get_database() -> AsyncIOMotorDatabase:
    """Récupère l'instance de la DB avec une sécurité."""
    if db_instance.db is None:
        # Au lieu de juste logguer, on peut lever une exception explicite
        # Cela évite que le repo ne crash avec un message obscur plus loin
        msg = "La connexion MongoDB n'est pas initialisée. Vérifiez le cycle de vie (Lifespan/Worker Init)."
        logger.critical(msg)
        raise ConnectionError(msg)
    return db_instance.db


def get_collection(name: str) -> AsyncIOMotorCollection:
    """Accès sécurisé à une collection."""
    return get_database()[name]