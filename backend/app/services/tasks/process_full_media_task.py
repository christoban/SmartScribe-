"""
Tâche Celery: orchestration complète d'un média.

Upload → Traitement média → Transcription → OCR/Vision → Structuration NLP → Export → Sauvegarde DB
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from groq import APIConnectionError, InternalServerError, RateLimitError

from app.core import constants
from app.core.celery_app import celery_app
from app.core.logger import get_logger
from app.db.repositories.media_repo import MediaRepository
from app.services.orchestrator import orchestrator

logger = get_logger("celery.process_full_media_task")


def _get_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@celery_app.task(
    name="process_full_media_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_full_media_task(self, media_id: str, file_path: str, user_id: Optional[str] = None):
    logger.info("[JOB START] media_id=%s", media_id)

    path = Path(file_path)
    if not path.exists():
        logger.error("Fichier introuvable: %s", file_path)
        loop = _get_loop()
        loop.run_until_complete(MediaRepository.update(media_id, {"status": constants.STATUS_FAILED}))
        return False

    loop = _get_loop()

    try:
        result = loop.run_until_complete(
            orchestrator.process_full_media(media_id=media_id, file_path=path, user_id=user_id)
        )

        if result:
            logger.info("[JOB SUCCESS] %s", media_id)
            loop.run_until_complete(MediaRepository.update(media_id, {"status": constants.STATUS_COMPLETED}))
            return True

        loop.run_until_complete(MediaRepository.update(media_id, {"status": constants.STATUS_FAILED}))
        return False

    except (InternalServerError, RateLimitError, APIConnectionError) as exc:
        logger.warning("Erreur API temporaire (%s). Retry %s/3...", media_id, self.request.retries)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

    except Exception as exc:
        logger.error("[JOB FATAL ERROR] %s: %s", media_id, exc)
        loop.run_until_complete(MediaRepository.update(media_id, {"status": "error"}))
        return False

