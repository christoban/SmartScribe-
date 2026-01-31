from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.core.logger import get_logger
from app.services.ia.local.unsloth_engine import FineTuneConfig, unsloth_engine

logger = get_logger("ia.fine_tuning.trainer")


class ModelTrainer:
    """Orchestration du fine-tuning (placeholder)."""

    async def train(self, config: Optional[FineTuneConfig] = None) -> Path:
        logger.info("Démarrage training (placeholder).")
        return await unsloth_engine.train(config=config)


model_trainer = ModelTrainer()

