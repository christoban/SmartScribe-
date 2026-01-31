from typing import Optional
from bson import ObjectId
from datetime import datetime, timezone
from app.db.mongo import get_collection
from app.models.user import UserModel
from app.core.security import hash_password
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

class UserRepository:
    
    @classmethod
    async def _get_collection(cls) -> AsyncIOMotorCollection:
        """Récupère la collection de manière asynchrone."""
        return get_collection("users")

    @classmethod
    async def create(cls, user_create_data: dict) -> UserModel:
        collection = await cls._get_collection()
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

        result = await collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return UserModel(**user_data)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[UserModel]:
        collection = await cls._get_collection()
        # On utilise .lower() pour être cohérent avec le validateur du modèle
        user_dict = await collection.find_one({"email": email.lower()})
        return UserModel(**user_dict) if user_dict else None

    @classmethod
    async def get_by_id(cls, user_id: str) -> Optional[UserModel]:
        if not user_id or not ObjectId.is_valid(user_id):
            return None
        collection = await cls._get_collection()
        user_dict = await collection.find_one({"_id": ObjectId(user_id)})
        return UserModel(**user_dict) if user_dict else None

    @classmethod
    async def update(cls, user_id: str, update_data: dict) -> Optional[UserModel]:
        if not ObjectId.is_valid(user_id):
            return None
            
        collection = await cls._get_collection()
        
        # Préparation des données d'update
        data = update_data.copy()
        if "password" in data:
            data["hashed_password"] = hash_password(data.pop("password"))
        
        data["updated_at"] = datetime.now(timezone.utc)

        # find_one_and_update est plus atomique et efficace
        updated_doc = await collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER,  # Renvoie le document APRES modification
        )
        
        return UserModel(**updated_doc) if updated_doc else None
    
    @classmethod
    async def delete(cls, user_id: str) -> bool:
        """Supprime un utilisateur"""
        if not ObjectId.is_valid(user_id):
            return False
        collection = await cls._get_collection()
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0