from fastapi import HTTPException, status
from app.db.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate
from app.core.security import verify_password, hash_password
from app.core.logger import get_logger

class AuthService:
    def __init__(self):
        self._logger = get_logger("auth_service")

    async def register_user(self, user_in: UserCreate):
        """Gère la logique d'inscription : validation, hachage et stockage."""
        
        # 1. Vérification si l'email existe déjà
        existing_user = await UserRepository.get_by_email(user_in.email)
        if existing_user:
            self._logger.warning("⚠️ Tentative d'inscription doublon : %s", user_in.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà enregistré."
            )
        
        # 2. Hachage du mot de passe (CRUCIAL : ne jamais stocker en clair)
        hashed = hash_password(user_in.password)
        
        # 3. Préparation des données pour le modèle
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed
        del user_data["password"] # On supprime le mot de passe en clair
        
        # 4. Création via le Repository
        new_user = await UserRepository.create(user_data)
        self._logger.info("👤 Nouvel utilisateur créé : %s", new_user.email)
        return new_user

    async def authenticate_user(self, email: str, password: str):
        """Vérifie les identifiants pour le login."""
        user = await UserRepository.get_by_email(email)
        if not user:
            return False
        
        if not verify_password(password, user.hashed_password):
            return False
            
        return user

# On exporte une instance unique (Singleton)
auth_service = AuthService()