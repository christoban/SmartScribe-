from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import auth_service # Instance plutôt que classe
from app.db.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, TokenOut, UserOut
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token, # Utilise la fonction unifiée qu'on a créée
    verify_password
)

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """Inscription : Crée l'identité de l'utilisateur."""
    # On utilise l'instance auth_service pour gérer le hachage et les doublons
    return await auth_service.register_user(user_in)


@router.post("/login", response_model=TokenOut)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # On délègue la vérification au service
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    return {
        "access_token": create_access_token(user_id=str(user.id)),
        "refresh_token": create_refresh_token(user_id=str(user.id)),
        "token_type": "bearer",
    }

@router.post("/refresh-token", response_model=TokenOut)
async def refresh_token(refresh_token: str):
    """Renouvellement de session via Refresh Token."""
    # On utilise decode_token qui vérifie la signature et l'expiration
    payload = decode_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token de type invalide")

    user_id = payload.get("sub")
    user = await UserRepository.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    return {
        "access_token": create_access_token(user_id=str(user.id)),
        "refresh_token": create_refresh_token(user_id=str(user.id)),
        "token_type": "bearer",
    }