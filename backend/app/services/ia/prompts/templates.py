"""
Templates de prompts (V1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class PromptTemplates:
    templates: Dict[str, str] = None  # type: ignore[assignment]

    def __post_init__(self):
        object.__setattr__(
            self,
            "templates",
            {
                "content_type_detection": (
                    "Analyse ce texte et réponds uniquement par un mot parmi: "
                    "cours, formation, podcast, tutoriel, réunion, journal.\n\n"
                    "TEXTE:\n{transcription}\n"
                ),
                "note_structure": (
                    "Tu es un excellent étudiant. Transforme la transcription suivante en notes structurées "
                    "en Markdown. Mets l'essentiel, reformule, et organise.\n\n"
                    "CONTEXTE VISUEL (si présent):\n{visual_context}\n\n"
                    "TRANSCRIPTION:\n{transcription}\n"
                ),
                "course": (
                    "Tu es un professeur pédagogue. À partir de la transcription, produis un cours complet "
                    "structuré en Markdown:\n"
                    "- plan\n- définitions\n- explications\n- exemples\n- résumé\n\n"
                    "CONTEXTE VISUEL (si présent):\n{visual_context}\n\n"
                    "TRANSCRIPTION:\n{transcription}\n"
                ),
                "summary": (
                    "Fais une fiche de révision concise en Markdown (points clés + formules/termes).\n\n"
                    "{transcription}\n"
                ),
                "qcm": (
                    "Génère {num_questions} QCM en JSON (question, choices[], answer, explanation) "
                    "à partir du texte.\n\n"
                    "{transcription}\n"
                ),
                "flashcard": (
                    "Génère {num_cards} flashcards en JSON (front, back) à partir du texte.\n\n"
                    "{transcription}\n"
                ),
                "exercise": (
                    "Génère {num_exercises} exercices + corrigés en Markdown.\n\n"
                    "{transcription}\n"
                ),
            },
        )

    def format_template(self, template_name: str, **kwargs: Any) -> str:
        tpl = self.templates.get(template_name)
        if not tpl:
            raise KeyError(f"Unknown template: {template_name}")
        return tpl.format(**kwargs)

