from pathlib import Path
import time
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("tasks.maintenance")

@celery_app.task(name="cleanup_exports_task")
def cleanup_exports_task(max_age_hours: int = 24):
    """
    Tâche de fond pour nettoyer les exports périmés.
    """
    directory = Path(settings.DOCS_DIR)
    if not directory.exists():
        return "Directory does not exist"

    now = time.time()
    count = 0
    
    for file in directory.glob("*"):
        if file.is_file():
            age = now - file.stat().st_mtime
            if age > max_age_hours * 3600:
                file.unlink()
                count += 1
                
    logger.info(f"🧹 Nettoyage terminé : {count} fichiers supprimés.")
    return f"Deleted {count} files"