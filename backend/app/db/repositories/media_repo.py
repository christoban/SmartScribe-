from typing import List, Optional
from bson import ObjectId
from app.db.mongo import get_database # Ton utilitaire de connexion
from app.models.media import Media
from app.core.logger import get_logger

logger = get_logger("MediaRepository")

class MediaRepository:
    COLLECTION_NAME = "media"

    @classmethod
    async def _get_collection(cls):
        db = get_database()
        return db[cls.COLLECTION_NAME]

    @classmethod
    async def create(cls, media_data: Media) -> str:
        """Insère un nouveau média et retourne son ID."""
        collection = await cls._get_collection()
        # model_dump(by_alias=True) transforme 'id' en '_id' pour Mongo
        doc = media_data.model_dump(exclude_none=True, by_alias=True)
        # Normaliser user_id en ObjectId si possible
        if "user_id" in doc and isinstance(doc["user_id"], str) and ObjectId.is_valid(doc["user_id"]):
            doc["user_id"] = ObjectId(doc["user_id"])
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    async def get_by_id(cls, media_id: str) -> Optional[Media]:
        """Récupère un média par son identifiant unique."""
        collection = await cls._get_collection()
        doc = await collection.find_one({"_id": ObjectId(media_id)})
        return Media(**doc) if doc else None

    @classmethod
    async def get_user_media(cls, user_id: str) -> List[Media]:
        """Récupère tous les médias d'un utilisateur spécifique."""
        collection = await cls._get_collection()
        query_user = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        cursor = collection.find({"user_id": query_user}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [Media(**doc) for doc in docs]

    @classmethod
    async def update(cls, media_id: str, update_data: dict) -> bool:
        """Met à jour un média en gérant intelligemment l'ID."""
        collection = await cls._get_collection()
        
        # On essaie d'abord avec l'ObjectId, sinon on cherche par string direct
        try:
            query = {"_id": ObjectId(media_id)}
        except Exception:
            query = {"_id": media_id}
            
        result = await collection.update_one(query, {"$set": update_data})
        return result.modified_count > 0
    
    @classmethod
    async def delete(cls, media_id: str) -> bool:
        """Supprime un média de la base de données."""
        collection = await cls._get_collection()
        result = await collection.delete_one({"_id": ObjectId(media_id)})
        return result.deleted_count > 0