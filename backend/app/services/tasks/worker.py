"""
Celery worker bootstrap.

Ce module est autodécouvert par Celery via `related_name="worker"`.
"""

from __future__ import annotations

import asyncio

from celery.signals import worker_process_init, worker_process_shutdown

from app.core.celery_app import celery_app
from app.core.logger import get_logger
from app.db.mongo import close_mongo_connection, connect_to_mongo

# Enregistrement des tâches (important: import side-effect)
from app.services.tasks.process_full_media_task import process_full_media_task  # noqa: F401

logger = get_logger("celery.worker")


def _run(coro) -> None:
    """Exécute un coroutine dans le loop du process worker."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # En pratique un worker Celery n'a pas de loop déjà "running" dans ce thread.
        raise RuntimeError("Event loop already running in worker thread")

    loop.run_until_complete(coro)


@worker_process_init.connect
def init_worker(**_kwargs):
    _run(connect_to_mongo())
    logger.info("[WORKER] Connexion MongoDB établie.")


@worker_process_shutdown.connect
def shutdown_worker(**_kwargs):
    try:
        _run(close_mongo_connection())
        logger.info("[WORKER] Connexion MongoDB fermée.")
    except Exception as exc:
        logger.error("Erreur shutdown worker: %s", exc)


@celery_app.task(name="check_health")
def check_health():
    logger.info("Celery Worker est en ligne.")
    return "OK"

