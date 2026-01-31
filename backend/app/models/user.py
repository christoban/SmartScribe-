from pydantic import EmailStr, Field, field_validator
from app.models.base import MongoBaseModel
from typing import Optional

class UserModel(MongoBaseModel):
    # On force l'email en minuscules pour éviter les doublons accidentels
    email: EmailStr = Field(..., description="Email unique de l'utilisateur")
    hashed_password: str = Field(..., description="Mot de passe haché (bcrypt)")
    full_name: Optional[str] = None
    role: str = "user" 
    is_active: bool = Field(default=True)

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()

    # Configuration spécifique au modèle User
    model_config = {
        "collection": "users", # Utile pour ton futur UserRepository
    }