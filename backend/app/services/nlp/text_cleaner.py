"""
Nettoyage textuel "pur" (regex, normalisation).
"""

from __future__ import annotations

import re
from typing import Final


_MULTI_SPACE: Final[re.Pattern[str]] = re.compile(r"[ \t]{2,}")
_MULTI_NEWLINES: Final[re.Pattern[str]] = re.compile(r"\n{3,}")


class TextCleaner:
    def clean(self, text: str) -> str:
        if not text:
            return ""
            
        # 1. Normalisation des retours à la ligne
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # 2. Supprimer les espaces en fin de chaque ligne (TRÈS IMPORTANT)
        text = "\n".join(line.rstrip() for line in text.splitlines())
        
        # 3. Réduire les espaces multiples (milieu de ligne)
        text = _MULTI_SPACE.sub(" ", text)
        
        # 4. Réduire les sauts de ligne excessifs (max 2 pour aérer)
        text = _MULTI_NEWLINES.sub("\n\n", text)
        
        return text.strip()

text_cleaner = TextCleaner()

