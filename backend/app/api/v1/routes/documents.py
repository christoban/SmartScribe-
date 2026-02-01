"""  
Routes pour l'upload et le traitement de documents (PDF, DOCX, TXT)  
"""  
import uuid  
import shutil  
import asyncio  
from pathlib import Path  
from typing import Optional  
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException  
  
from app.api.deps import get_current_user  
from app.db.repositories.media_repo import MediaRepository  
from app.db.mongo import get_database  
from app.schemas.media import MediaOut  
from app.models.media import Media  
from app.core.config import settings  
from app.core.logger import get_logger  
from app.services.tasks.process_document_task import process_document_task  
  
router = APIRouter()  
logger = get_logger("routes.documents")  
  
# Extensions autorisées pour les documents  
ALLOWED_DOC_EXTENSIONS = {"pdf", "docx", "txt", "doc"}  
  
@router.post("/upload", response_model=MediaOut)  
async def upload_document(  
    file: UploadFile = File(...),  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  
):  
    """  
    Upload d'un document textuel (PDF, DOCX, TXT).  
    Le document sera traité pour extraire le texte et générer des notes.  
    """  
    # 1. Validation de l'extension  
    if not file.filename:  
        raise HTTPException(status_code=400, detail="Nom de fichier manquant")  
      
    ext = file.filename.split(".")[-1].lower()  
    if ext not in ALLOWED_DOC_EXTENSIONS:  
        raise HTTPException(  
            status_code=400,   
            detail=f"Format .{ext} non supporté. Formats acceptés : {', '.join(ALLOWED_DOC_EXTENSIONS)}"  
        )  
  
    # 2. Préparation du stockage  
    user_id_str = str(current_user.id)  
    unique_filename = f"{uuid.uuid4()}.{ext}"  
    user_dir = Path(settings.UPLOAD_DIR) / user_id_str  
    user_dir.mkdir(parents=True, exist_ok=True)  
    file_path = user_dir / unique_filename  
  
    # 3. Écriture asynchrone du fichier  
    try:  
        logger.info("📄 Réception du document %s pour user=%s", file.filename, user_id_str)  
  
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
        media_type="document",  # Type spécifique pour les documents  
        file_path=str(file_path),  
        size=file_path.stat().st_size,  
        status="processing"  
    )  
      
    # Utilisation du pattern instance pour MediaRepository  
    media_repo = MediaRepository(db)  
    media_id = await media_repo.create(media_obj)  
  
    # 5. Lancement du worker Celery pour traitement du document  
    process_document_task.delay(  
        media_id=str(media_id),   
        file_path=str(file_path),   
        user_id=user_id_str  
    )  
      
    logger.info("🚀 Task de traitement document envoyée au worker: media_id=%s", media_id)  
    return await media_repo.get_by_id(media_id)