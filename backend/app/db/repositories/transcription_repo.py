from typing import Optional, List  
from bson import ObjectId  
from motor.motor_asyncio import AsyncIOMotorDatabase  
from app.models.transcription import Transcription  
from app.schemas.transcription import TranscriptionUpdate  
from app.core.logger import get_logger  
from datetime import datetime, timezone  
from pymongo import ReturnDocument  
  
logger = get_logger("TranscriptionRepository")  
  
class TranscriptionRepository:  
    def __init__(self, db: AsyncIOMotorDatabase):  
        self.collection = db["transcriptions"]  
  
    async def create(self, transcription: Transcription) -> Transcription:  
        """Insère une nouvelle transcription."""  
        # On utilise by_alias pour Mongo (_id) et on exclut les None  
        doc = transcription.model_dump(by_alias=True, exclude_none=True)  
        result = await self.collection.insert_one(doc)  
        transcription.id = str(result.inserted_id)  
        return transcription  
  
    async def get_by_id(self, transcription_id: str) -> Optional[Transcription]:  
        """Récupère une transcription par son ID."""  
        if not ObjectId.is_valid(transcription_id):  
            return None  
        doc = await self.collection.find_one({"_id": ObjectId(transcription_id)})  
        if doc:  
            return Transcription(**doc)  
        return None  
      
    async def get_by_media_id(self, media_id: str) -> Optional[Transcription]:  
        """Récupère LA transcription d'un média (Un média = Une transcription)."""  
        doc = await self.collection.find_one({"media_id": media_id})  
        if doc:  
            return Transcription(**doc)  
        return None  
  
    async def update(self, transcription_id: str, update_data: TranscriptionUpdate) -> Optional[Transcription]:  
        """Met à jour proprement les segments ou le texte."""  
        update_dict = update_data.model_dump(exclude_unset=True)  
        if update_dict:  
            update_dict["updated_at"] = datetime.now(timezone.utc)  
            result = await self.collection.find_one_and_update(  
                {"_id": ObjectId(transcription_id)},  
                {"$set": update_dict},  
                return_document=ReturnDocument.AFTER,  
            )  
            if result:  
                return Transcription(**result)  
        return None  
  
    async def delete(self, transcription_id: str) -> bool:  
        """Supprime par ID technique."""  
        result = await self.collection.delete_one({"_id": ObjectId(transcription_id)})  
        return result.deleted_count > 0  
      
    async def update_status(self, transcription_id: str, status: str) -> Optional[Transcription]:  
        """Met à jour uniquement le statut de la transcription."""  
        if not ObjectId.is_valid(transcription_id):  
            return None  
  
        result = await self.collection.find_one_and_update(  
            {"_id": ObjectId(transcription_id)},  
            {  
                "$set": {  
                    "status": status,  
                    "updated_at": datetime.now(timezone.utc),  
                }  
            },  
            return_document=ReturnDocument.AFTER,  
        )  
  
        if result:  
            return Transcription(**result)  
        return None  
  
    # 🔧 CORRECTION IMPORTANTE : Ajout de la méthode manquante  
    async def get_user_transcriptions(  
        self,   
        user_id: str,   
        skip: int = 0,   
        limit: int = 20  
    ) -> List[Transcription]:  
        """  
        Récupère les transcriptions d'un utilisateur avec pagination.  
          
        Cette méthode est utilisée dans history.py pour afficher l'historique  
        des transcriptions de l'utilisateur.  
        """  
        if not ObjectId.is_valid(user_id):  
            return []  
          
        cursor = self.collection.find(  
            {"user_id": ObjectId(user_id)}  
        ).sort("created_at", -1).skip(skip).limit(limit)  
          
        transcriptions = await cursor.to_list(length=limit)  
        return [Transcription(**doc) for doc in transcriptions]