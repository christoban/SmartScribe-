from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _get_log_dir() -> Path:
    # On centralise les logs dans `storage/` (runtime, gitignored).
    log_dir = settings.STORAGE_PATH / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Logger applicatif unifié.

    Important:
    - Toujours appeler `get_logger(__name__)` (et pas `get_logger.info`).
    - Expose aussi un logger global `logger` pour compat.
    """
    logger_name = name or "smartscribe"
    log = logging.getLogger(logger_name)

    if log.handlers:
        return log

    # Niveau global
    log.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT)

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # Fichier rotatif
    log_file = _get_log_dir() / "smartscribe.log"
    fh = RotatingFileHandler(
        str(log_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # Évite que les logs remontent au root logger (duplicats).
    log.propagate = False

    return log


# Compat: certains modules font `from app.core.logger import logger`
logger = get_logger()
