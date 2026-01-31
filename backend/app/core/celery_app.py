from celery import Celery
from app.core.config import get_settings
from app.core.logger import get_logger
from celery.schedules import crontab  # 1. Ajoute cet import en haut

settings = get_settings()
logger = get_logger("celery_app")

celery_app = Celery(
    "smartscribe",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    # --- Sécurité & Format ---
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # --- Robustesse (Essentiel pour l'IA) ---
    task_acks_late=True,           # La tâche reste dans Redis si le worker crash
    task_reject_on_worker_lost=True,
    task_time_limit=3600,          # 1h max pour éviter les process fantômes
    
    # --- Performance GPU/RAM ---
    worker_prefetch_multiplier=1,  # Ne réserve qu'une tâche à la fois
    worker_concurrency=1,          # RECOMMANDÉ : 1 seul process lourd à la fois sur Windows
)

# 2. Ajoute le planning ici (C'est le "métronome" de Celery)
celery_app.conf.beat_schedule = {
    "cleanup-exports-every-hour": {
        "task": "cleanup_exports_task", # Le nom exact défini dans @celery_app.task
        "schedule": crontab(minute=0),   # S'exécute à chaque heure pile (:00)
        "args": (24,),                  # On passe l'argument max_age_hours
    },
}

# --- Détection automatique des tâches ---
# On pointe vers le dossier où nous allons mettre nos fichiers de tâches
celery_app.autodiscover_tasks([
    "app.services.tasks.cleanup_exports_task",
    "app.services.tasks.process_full_media",
    "app.services.tasks.worker"
], force=True)

@celery_app.task(name="check_health")
def check_health():
    logger.info("🚀 Celery Worker est en ligne et prêt pour ScolarAI !")
    return "OK"

logger.info("[START] Celery configuré pour le traitement IA...")