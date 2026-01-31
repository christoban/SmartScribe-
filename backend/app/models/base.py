from datetime import datetime, timezone
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict, BeforeValidator, Field

# 🔹 Transformation magique : convertit l'ObjectId de Mongo en String pour le Python
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    """
    Base pour tous les documents MongoDB de SmartScribe.
    """
    # L'id est optionnel car au moment de la création (In), Mongo ne l'a pas encore généré
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    
    # On utilise timezone.utc pour être conforme aux standards de 2026
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        extra="ignore", 
        # Permet d'utiliser 'id' dans ton code et '_id' pour la DB
        populate_by_name=True,
        # Autorise les types complexes comme datetime
        arbitrary_types_allowed=True,
        # Pratique pour le JSON (convertit automatiquement les dates en ISO)
        json_schema_extra={
            "example": {
                "id": "60d5ecb8b392d032e82b3a1a",
                "created_at": "2026-01-19T23:00:00Z",
                "updated_at": "2026-01-19T23:00:00Z"
            }
        }
    )