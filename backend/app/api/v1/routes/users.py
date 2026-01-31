"""
Routes pour la gestion du profil utilisateur
"""
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.schemas.user import UserOut, UserUpdate
from app.db.repositories.user_repo import UserRepository

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Récupère le profil de l'utilisateur connecté"""
    return current_user

@router.put("/me", response_model=UserOut)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user)
):
    """Met à jour le profil de l'utilisateur connecté"""
    updated_user = await UserRepository.update(str(current_user.id), user_update.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return updated_user

@router.delete("/me")
async def delete_current_user(current_user = Depends(get_current_user)):
    """Supprime le compte de l'utilisateur connecté"""
    deleted = await UserRepository.delete(str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"status": "deleted", "message": "Compte supprimé avec succès"}
