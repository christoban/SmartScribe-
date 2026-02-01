from typing import Optional  
from bson import ObjectId  
from datetime import datetime, timezone  
from motor.motor_asyncio import AsyncIOMotorDatabase  
from app.models.user import UserModel  
from app.core.security import hash_password  
from pymongo import ReturnDocument  
  
# 🔧 CORRECTION BLOQUANTE : Passage du pattern classe au pattern instance  
# pour cohérence avec TranscriptionRepository, NoteRepository et ExportRepository  
class UserRepository:  
    """Repository pour la gestion des utilisateurs (pattern instance)"""  
      
    COLLECTION_NAME = "users"  
  
    def __init__(self, db: AsyncIOMotorDatabase):  
        """  
        Initialisation avec l'instance de la DB.  
        Ce pattern est cohérent avec les autres repositories du projet.  
        """  
        self.collection = db[self.COLLECTION_NAME]  
  
    async def create(self, user_create_data: dict) -> UserModel:  
        """Crée un nouvel utilisateur et retourne le modèle complet."""  
        user_data = user_create_data.copy()  
          
        # Sécurité : On nettoie et on prépare  
        user_data["role"] = "user"  
        user_data["is_active"] = True  
          
        if "password" in user_data:  
            user_data["hashed_password"] = hash_password(user_data.pop("password"))  
          
        # Ajout des dates si non présentes  
        now = datetime.now(timezone.utc)  
        user_data.setdefault("created_at", now)  
        user_data.setdefault("updated_at", now)  
  
        result = await self.collection.insert_one(user_data)  
        user_data["_id"] = result.inserted_id  
        return UserModel(**user_data)  
  
    async def get_by_email(self, email: str) -> Optional[UserModel]:  
        """Récupère un utilisateur par son email."""  
        # On utilise .lower() pour être cohérent avec le validateur du modèle  
        user_dict = await self.collection.find_one({"email": email.lower()})  
        return UserModel(**user_dict) if user_dict else None  
  
    async def get_by_id(self, user_id: str) -> Optional[UserModel]:  
        """Récupère un utilisateur par son ID."""  
        if not user_id or not ObjectId.is_valid(user_id):  
            return None  
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})  
        return UserModel(**user_dict) if user_dict else None  
  
    async def update(self, user_id: str, update_data: dict) -> Optional[UserModel]:  
        """Met à jour un utilisateur et retourne le document modifié."""  
        if not ObjectId.is_valid(user_id):  
            return None  
          
        # Préparation des données d'update  
        data = update_data.copy()  
        if "password" in data:  
            data["hashed_password"] = hash_password(data.pop("password"))  
          
        data["updated_at"] = datetime.now(timezone.utc)  
  
        # find_one_and_update est plus atomique et efficace  
        updated_doc = await self.collection.find_one_and_update(  
            {"_id": ObjectId(user_id)},  
            {"$set": data},  
            return_document=ReturnDocument.AFTER,  # Renvoie le document APRES modification  
        )  
          
        return UserModel(**updated_doc) if updated_doc else None  
      
    async def delete(self, user_id: str) -> bool:  
        """Supprime un utilisateur."""  
        if not ObjectId.is_valid(user_id):  
            return False  
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})  
        return result.deleted_count > 0