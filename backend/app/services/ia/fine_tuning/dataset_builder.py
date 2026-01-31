from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("ia.fine_tuning.dataset_builder")


@dataclass(frozen=True)
class DatasetSample:
    prompt: str
    completion: str


class DatasetBuilder:
    """
    Builder simple de dataset (instruction → réponse) pour fine-tuning.
    """

    def __init__(self, dataset_path: Path = settings.DATASET_PATH) -> None:
        self.dataset_path = dataset_path
        self.dataset_path.mkdir(parents=True, exist_ok=True)

    def write_jsonl(self, samples: Iterable[DatasetSample], filename: str = "dataset.jsonl") -> Path:
        out = self.dataset_path / filename
        with out.open("w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps({"prompt": s.prompt, "completion": s.completion}, ensure_ascii=False) + "\n")
        logger.info("Dataset écrit: %s", out)
        return out


dataset_builder = DatasetBuilder()

