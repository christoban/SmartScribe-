from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("ia.local.unsloth_engine")


@dataclass(frozen=True)
class FineTuneConfig:
    dataset_path: Path = settings.DATASET_PATH
    output_dir: Path = settings.LORA_OUTPUT_DIR
    base_model: str = settings.LOCAL_LLM_MODEL


class UnslothEngine:
    """
    Wrapper local pour fine-tuning (placeholder).

    Le fine-tuning réel dépend fortement de l'environnement (GPU, VRAM, CUDA, etc.).
    """

    async def train(self, config: Optional[FineTuneConfig] = None) -> Path:
        config = config or FineTuneConfig()
        logger.info("Fine-tuning placeholder. dataset=%s output=%s", config.dataset_path, config.output_dir)
        config.output_dir.mkdir(parents=True, exist_ok=True)
        # Placeholder: créer un fichier "marker" pour indiquer la sortie.
        marker = config.output_dir / "TRAINING_NOT_IMPLEMENTED.txt"
        marker.write_text(
            "Fine-tuning local non implémenté dans cette V1.\n",
            encoding="utf-8",
        )
        return marker


unsloth_engine = UnslothEngine()

