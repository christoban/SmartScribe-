import redis.asyncio as redis
import json
from typing import Any, Optional
from app.core.config import settings
from app.core.logger import get_logger

class RedisCache:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._logger = get_logger("redis_cache")

    async def connect(self):
        """Initialise la connexion à Redis."""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True
            )
            # Test de connexion
            await self.client.ping()
            self._logger.info("🚀 Connecté à Redis sur %s", settings.REDIS_URL)
        except Exception as e:
            self._logger.error("❌ Erreur de connexion Redis : %s", e)
            self.client = None

    async def disconnect(self):
        """Ferme proprement la connexion."""
        if self.client:
            await self.client.close()
            self._logger.info("🔌 Connexion Redis fermée.")

    async def set(self, key: str, value: Any, expire: int = 3600):
        """
        Stocke une donnée en cache.
        Convertit automatiquement les dict/list en JSON.
        """
        if not self.client:
            return
        
        try:
            # Si c'est un dictionnaire ou une liste, on sérialise en JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.client.set(key, value, ex=expire)
        except Exception as e:
            self._logger.error("Erreur lors de l'écriture Redis (%s) : %s", key, e)

    async def get(self, key: str) -> Optional[Any]:
        """
        Récupère une donnée du cache.
        Tente de désérialiser le JSON si possible.
        """
        if not self.client:
            return None
        
        try:
            data = await self.client.get(key)
            if not data:
                return None
            
            # Tentative de conversion JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        except Exception as e:
            self._logger.error("Erreur lors de la lecture Redis (%s) : %s", key, e)
            return None

    async def delete(self, key: str):
        """Supprime une clé du cache."""
        if self.client:
            await self.client.delete(key)

# Instance unique pour l'application
redis_cache = RedisCache()