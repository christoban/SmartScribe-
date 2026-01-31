"""
Repository pour les notes (pattern instance)
"""
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


class NoteRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["notes"]

    async def create(self, note: Note) -> Note:
        """Crée une nouvelle note"""
        doc = note.model_dump(by_alias=True, exclude_none=True)
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc.setdefault("updated_at", now)
        doc.setdefault("status", "draft")

        result = await self.collection.insert_one(doc)
        note.id = str(result.inserted_id)
        return note

    async def get_by_id(self, note_id: str) -> Optional[Note]:
        if not ObjectId.is_valid(note_id):
            return None

        doc = await self.collection.find_one({"_id": ObjectId(note_id)})
        return Note(**doc) if doc else None

    async def get_by_transcription_id(self, transcription_id: str, user_id: str) -> List[Note]:
        if not ObjectId.is_valid(transcription_id) or not ObjectId.is_valid(user_id):
            return []

        cursor = self.collection.find({
            "transcription_id": ObjectId(transcription_id),
            "user_id": ObjectId(user_id),
        })

        docs = await cursor.to_list(length=100)
        return [Note(**doc) for doc in docs]

    async def get_user_notes(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Note]:
        if not ObjectId.is_valid(user_id):
            return []

        cursor = (
            self.collection
            .find({"user_id": ObjectId(user_id)})
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )

        docs = await cursor.to_list(length=limit)
        return [Note(**doc) for doc in docs]

    async def update(self, note_id: str, update_data: NoteUpdate) -> Optional[Note]:
        if not ObjectId.is_valid(note_id):
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(note_id)},
            {"$set": update_dict},
            return_document=ReturnDocument.AFTER,
        )

        return Note(**result) if result else None

    async def delete(self, note_id: str) -> bool:
        if not ObjectId.is_valid(note_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(note_id)})
        return result.deleted_count > 0
