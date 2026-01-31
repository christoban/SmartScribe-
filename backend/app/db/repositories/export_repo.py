"""
Repository pour les exports
"""
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from app.models.export import Export
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

class ExportRepository:
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialisation avec l'instance de la DB passée par l'Orchestrator"""
        self.collection: AsyncIOMotorCollection = db.get_collection("exports")
    
    async def create(self, export_data: dict) -> str:
        """Crée un nouvel export et retourne son ID"""
        # On utilise directement self.collection défini dans le __init__
        
        # Préparation des données
        data = export_data.copy()
        now = datetime.now(timezone.utc)
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        data.setdefault("generated_at", now)
        
        # Conversion des IDs en ObjectId si nécessaire
        if "user_id" in data and isinstance(data["user_id"], str):
            data["user_id"] = ObjectId(data["user_id"])
        if "note_id" in data and isinstance(data["note_id"], str):
            data["note_id"] = ObjectId(data["note_id"])
        
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)
    
    async def get_by_id(self, export_id: str) -> Optional[Export]:
        """Récupère un export par son ID"""
        if not export_id or not ObjectId.is_valid(export_id):
            return None
            
        export_dict = await self.collection.find_one({"_id": ObjectId(export_id)})
        return Export(**export_dict) if export_dict else None
    
    async def get_by_note_id(self, note_id: str, user_id: str) -> List[Export]:
        """Récupère tous les exports d'une note"""
        if not ObjectId.is_valid(note_id) or not ObjectId.is_valid(user_id):
            return []

        cursor = self.collection.find({
            "note_id": ObjectId(note_id),
            "user_id": ObjectId(user_id)
        })
        exports = await cursor.to_list(length=100)
        return [Export(**export) for export in exports]
    
    async def get_user_exports(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Export]:
        """Récupère tous les exports d'un utilisateur"""
        if not ObjectId.is_valid(user_id):
            return []

        cursor = self.collection.find({"user_id": ObjectId(user_id)}) \
                                .skip(skip) \
                                .limit(limit) \
                                .sort("created_at", -1)
        
        exports = await cursor.to_list(length=limit)
        return [Export(**export) for export in exports]
    
    async def delete(self, export_id: str) -> bool:
        """Supprime un export"""
        if not ObjectId.is_valid(export_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(export_id)})
        return result.deleted_count > 0