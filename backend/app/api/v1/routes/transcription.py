from fastapi import APIRouter, UploadFile, Depends
import uuid
import shutil
from pathlib import Path
from app.services.tasks.process_full_media_task import process_full_media_task
from app.api.deps import get_current_user 
from app.core.config import settings
import aiofiles # À installer : pip install aiofiles


router = APIRouter()

@router.post("/process", status_code=202)
async def start_transcription(media_file: UploadFile, current_user = Depends(get_current_user)):
    job_id = str(uuid.uuid4())
    temp_dir = Path(settings.UPLOAD_DIR).resolve() / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / f"{job_id}_{media_file.filename}" 

    # ✅ Utilisation de aiofiles pour ne pas bloquer l'Event Loop
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await media_file.read(1024 * 1024): # Read by chunks of 1MB
            await out_file.write(content)

    process_full_media_task.delay(
        media_id=job_id, 
        file_path=str(file_path), 
        user_id=str(current_user.id)
    )

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Traitement lancé. Consultez le terminal Celery pour le suivi IA."
    }
