from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.repositories.user_repo import UserRepository
from app.models.user import UserModel

# Définit où l'API doit chercher le token (le "cadenas" dans la doc Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Vérifie le JWT et récupère l'utilisateur en base.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session non valide. Accès refusé.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Décodage du token (récupère le dict payload)
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (JWTError, AttributeError):
        raise credentials_exception

    # 2. Récupération de l'utilisateur (Méthode asynchrone correcte)
    user = await UserRepository.get_by_id(user_id)
    
    if not user:
        raise credentials_exception
        
    return user

async def get_ai_context(current_user: UserModel = Depends(get_current_user)):
    """
    Prépare le terrain pour le RAG et la personnalisation IA.
    Injecte les préférences de l'utilisateur dans les prompts futurs.
    """
    # Ici, on pourra plus tard charger des préférences depuis UserModel (ex: style de note)
    return {
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "tier": getattr(current_user, "tier", "free"),
        "ai_style": "pédagogique_structuré" 
    }