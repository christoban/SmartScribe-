import uuid  
import shutil  
import asyncio  
from pathlib import Path  
from typing import List  
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException  
  
from app.api.deps import get_current_user  
from app.db.repositories.media_repo import MediaRepository  
from app.db.mongo import get_database  # 🔧 CORRECTION BLOQUANTE : Import ajouté  
from app.schemas.media import MediaOut  
from app.models.media import Media  
from app.core.config import settings  
from app.core.logger import get_logger  
from app.services.tasks.process_full_media_task import process_full_media_task  
  
router = APIRouter()  
logger = get_logger("routes.media")  
  
ALLOWED_EXTENSIONS = {"mp4", "mp3", "wav", "m4a", "mov", "webm", "mkv"}  
  
@router.post("/upload", response_model=MediaOut)  
async def upload_media(  
    file: UploadFile = File(...),  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    # 1. Validation de l'extension  
    ext = file.filename.split(".")[-1].lower()  
    if ext not in ALLOWED_EXTENSIONS:  
        raise HTTPException(status_code=400, detail=f"Format .{ext} non supporté")  
  
    # 2. Préparation du stockage  
    user_id_str = str(current_user.id)  
    unique_filename = f"{uuid.uuid4()}.{ext}"  
    user_dir = Path(settings.UPLOAD_DIR) / user_id_str  
    user_dir.mkdir(parents=True, exist_ok=True)  
    file_path = user_dir / unique_filename  
  
    # 3. Écriture asynchrone (sans dépendance aiofiles)  
    try:  
        logger.info("📥 Réception du fichier %s pour user=%s", file.filename, user_id_str)  
  
        def _save():  
            with file_path.open("wb") as buffer:  
                shutil.copyfileobj(file.file, buffer)  
  
        await asyncio.to_thread(_save)  
    except Exception as e:  
        logger.error("❌ Erreur d'écriture disque : %s", e)  
        raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde du fichier")  
    finally:  
        await file.close()  
  
    # 4. Création de l'entrée en base (Status: Processing)  
    media_obj = Media(  
        user_id=user_id_str,  
        filename=file.filename,  
        file_type=ext,  
        media_type="audio" if ext in ["mp3", "wav", "m4a"] else "video",  
        file_path=str(file_path),  
        size=file_path.stat().st_size,  
        status="processing" # On passe direct en processing  
    )  
      
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    media_repo = MediaRepository(db)  
    media_id = await media_repo.create(media_obj)  
  
    # 5. Lancement du worker Celery  
    # C'est ici que l'Orchestrateur va prendre le relais  
    process_full_media_task.delay(  
        media_id=str(media_id),   
        file_path=str(file_path),   
        user_id=user_id_str  
    )  
      
    logger.info("🚀 Task envoyée au worker: media_id=%s", media_id)  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    return await media_repo.get_by_id(media_id)  
  
@router.get("/", response_model=List[MediaOut])  
async def list_my_media(  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    media_repo = MediaRepository(db)  
    return await media_repo.get_user_media(str(current_user.id))  
  
@router.delete("/{media_id}")  
async def delete_media(  
    media_id: str,   
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    media_repo = MediaRepository(db)  
    media = await media_repo.get_by_id(media_id)  
      
    if not media or str(media.user_id) != str(current_user.id):  
        raise HTTPException(status_code=404, detail="Média non trouvé")  
  
    # Nettoyage fichier physique  
    p = Path(media.file_path)  
    if p.exists():  
        p.unlink()  
      
    await media_repo.delete(media_id)  
    return {"status": "deleted", "id": media_id}