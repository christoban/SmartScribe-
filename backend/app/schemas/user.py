from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime, timezone

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    
class UserCreate(UserBase):
    # On impose une longueur minimale pour la sécurité
    password: str = Field(..., min_length=8, description="Le mot de passe doit faire au moins 8 caractères")

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    # Dans MongoDB, l'ID est souvent un ObjectId, on s'assure qu'il passe en string
    id: str = Field(..., alias="_id") 
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Configuration Pydantic V2 pour lire les objets ORM/ODM
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True # Permet d'utiliser 'id' au lieu de '_id' dans le JSON
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"