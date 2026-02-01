"""  
Tâche Celery pour le traitement des documents (PDF, DOCX, TXT)  
"""  
import asyncio  
from pathlib import Path  
from celery import Task  
from groq import InternalServerError, RateLimitError, APIConnectionError  
  
from app.core.celery_app import celery_app  
from app.core.logger import get_logger  
from app.db.repositories.media_repo import MediaRepository  
from app.db.mongo import get_database  
from app.services.document.text_extractor import extract_text_from_document  
from app.services.orchestrator import orchestrator  
  
logger = get_logger("process_document_task")  
  
  
def _get_loop() -> asyncio.AbstractEventLoop:  
    """Récupère ou crée un event loop pour les appels async."""  
    try:  
        return asyncio.get_event_loop()  
    except RuntimeError:  
        loop = asyncio.new_event_loop()  
        asyncio.set_event_loop(loop)  
        return loop  
  
  
@celery_app.task(  
    name="process_document_task",  
    bind=True,  
    max_retries=3,  
    default_retry_delay=60  
)  
def process_document_task(  
    self: Task,  
    media_id: str,  
    file_path: str,  
    user_id: str  
) -> bool:  
    """  
    Pipeline de traitement pour documents :  
    1. Extraction du texte (PDF/DOCX/TXT)  
    2. Génération de notes via IA  
    3. Structuration et export  
    """  
    loop = _get_loop()  
      
    try:  
        logger.info("📄 Début traitement document: media_id=%s, path=%s", media_id, file_path)  
          
        # Vérification de l'existence du fichier  
        doc_path = Path(file_path)  
        if not doc_path.exists():  
            logger.error("❌ Fichier introuvable: %s", file_path)  
            loop.run_until_complete(  
                MediaRepository.update(media_id, {"status": "failed"})  
            )  
            return False  
          
        # Extraction du texte du document  
        extracted_text = extract_text_from_document(doc_path)  
          
        if not extracted_text or len(extracted_text.strip()) < 50:  
            logger.error("❌ Texte extrait insuffisant ou vide")  
            loop.run_until_complete(  
                MediaRepository.update(media_id, {"status": "failed"})  
            )  
            return False  
          
        logger.info("✅ Texte extrait: %d caractères", len(extracted_text))  
          
        # Traitement via l'orchestrateur (génération de notes)  
        success = loop.run_until_complete(  
            orchestrator.process_document_text(  
                media_id=media_id,  
                text_content=extracted_text,  
                user_id=user_id,  
                export_formats=["pdf", "docx", "txt"]  
            )  
        )  
          
        if success:  
            logger.info("✅ Document traité avec succès: media_id=%s", media_id)  
            db = get_database()  
            media_repo = MediaRepository(db)  
            loop.run_until_complete(media_repo.update(media_id, {"status": "ready"}))  
            return True  
        else:  
            logger.error("❌ Échec du traitement document: media_id=%s", media_id)  
            db = get_database()  
            media_repo = MediaRepository(db)  
            loop.run_until_complete(media_repo.update(media_id, {"status": "failed"}))  
            return False  
              
    except (InternalServerError, RateLimitError, APIConnectionError) as exc:  
        logger.warning("⚠️ Erreur API récupérable, retry: %s", exc)  
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))  
          
    except Exception as exc:  
        logger.error("❌ ERREUR FATALE traitement document %s: %s", media_id, exc)  
        db = get_database()  
        media_repo = MediaRepository(db)  
        loop.run_until_complete(media_repo.update(media_id, {"status": "error"}))  
        return False