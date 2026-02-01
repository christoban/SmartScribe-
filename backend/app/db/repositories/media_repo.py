from typing import List, Optional  
from bson import ObjectId  
from motor.motor_asyncio import AsyncIOMotorDatabase  
from app.models.media import Media  
from app.core.logger import get_logger  
  
logger = get_logger("MediaRepository")  
  
# 🔧 CORRECTION BLOQUANTE : Passage du pattern classe au pattern instance  
# pour cohérence avec TranscriptionRepository, NoteRepository et ExportRepository  
class MediaRepository:  
    """Repository pour la gestion des médias (pattern instance)"""  
      
    COLLECTION_NAME = "media"  
  
    def __init__(self, db: AsyncIOMotorDatabase):  
        """  
        Initialisation avec l'instance de la DB.  
        Ce pattern est cohérent avec les autres repositories du projet.  
        """  
        self.collection = db[self.COLLECTION_NAME]  
  
    async def create(self, media_data: Media) -> str:  
        """Insère un nouveau média et retourne son ID."""  
        # model_dump(by_alias=True) transforme 'id' en '_id' pour Mongo  
        doc = media_data.model_dump(exclude_none=True, by_alias=True)  
        # Normaliser user_id en ObjectId si possible  
        if "user_id" in doc and isinstance(doc["user_id"], str) and ObjectId.is_valid(doc["user_id"]):  
            doc["user_id"] = ObjectId(doc["user_id"])  
        result = await self.collection.insert_one(doc)  
        return str(result.inserted_id)  
  
    async def get_by_id(self, media_id: str) -> Optional[Media]:  
        """Récupère un média par son identifiant unique."""  
        doc = await self.collection.find_one({"_id": ObjectId(media_id)})  
        return Media(**doc) if doc else None  
  
    async def get_user_media(self, user_id: str) -> List[Media]:  
        """Récupère tous les médias d'un utilisateur spécifique."""  
        query_user = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id  
        cursor = self.collection.find({"user_id": query_user}).sort("created_at", -1)  
        docs = await cursor.to_list(length=100)  
        return [Media(**doc) for doc in docs]  
  
    async def update(self, media_id: str, update_data: dict) -> bool:  
        """Met à jour un média en gérant intelligemment l'ID."""  
        # On essaie d'abord avec l'ObjectId, sinon on cherche par string direct  
        try:  
            query = {"_id": ObjectId(media_id)}  
        except Exception:  
            query = {"_id": media_id}  
              
        result = await self.collection.update_one(query, {"$set": update_data})  
        return result.modified_count > 0  
      
    async def delete(self, media_id: str) -> bool:  
        """Supprime un média de la base de données."""  
        result = await self.collection.delete_one({"_id": ObjectId(media_id)})  
        return result.deleted_count > 0