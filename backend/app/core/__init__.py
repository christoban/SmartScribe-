from .config import settings
from .celery_app import celery_app
from .logger import get_logger

# On prépare l'export pour faciliter les imports ailleurs dans le projet
# Exemple : from app.core import settings, celery_app
__all__ = ["settings", "celery_app", "get_logger"]