"""
Gestionnaire de prompts - Gère la sélection et le formatage des prompts
"""
from typing import Optional, Dict
from app.services.ia.prompts.templates import PromptTemplates
from app.core.logger import get_logger
from app.services.ia.groq_client import groq_client
from app.core.constants import ContentType # Importation

class PromptManager:
    """Gère les prompts pour la génération de contenu"""
    
    def __init__(self):
        self.templates = PromptTemplates()
        self.logger = get_logger("prompt_manager")
    
    def get_prompt_for_content_type(
        self,
        content_type: str,
        transcription: str,
        **kwargs
    ) -> str:
        """
        Récupère le prompt adapté au type de contenu
        
        Args:
            content_type: Type de contenu (cours, podcast, tutoriel, etc.)
            transcription: Transcription à traiter
            **kwargs: Paramètres additionnels
        
        Returns:
            Prompt formaté
        """
        # Mapping des types de contenu vers les templates
        template_mapping = {
            ContentType.COURSE : "course",
            ContentType.FORMATION : "course",
            ContentType.PODCAST : "note_structure",
            ContentType.TUTORIAL : "note_structure",
            ContentType.REUNION : "note_structure",
            ContentType.JOURNAL : "note_structure",
            ContentType.REPORTAGE : "note_structure",
            ContentType.AUTO : "auto"
        }
        
        # On cherche dans le mapping, sinon par défaut "note_structure"
        template_name = template_mapping.get(content_type, "note_structure")  

        return self.templates.format_template(
            template_name=template_name,
            transcription=transcription,
            content_type=content_type,
            **kwargs
        )
    

    def get_prompt_for_generation_type(
        self,
        generation_type: str,
        transcription: str,
        **kwargs
    ) -> str:
        """
        Récupère le prompt pour un type de génération spécifique
        
        Args:
            generation_type: Type de génération (qcm, flashcard, exercise, summary)
            transcription: Transcription à traiter
            **kwargs: Paramètres (num_questions, num_cards, etc.)
        
        Returns:
            Prompt formaté
        """
        template_mapping = {
            "qcm": "qcm",
            "flashcard": "flashcard",
            "flashcards": "flashcard",
            "exercise": "exercise",
            "exercises": "exercise",
            "summary": "summary",
            "fiche": "summary",
        }
        
        template_name = template_mapping.get(generation_type.lower(), "note_structure")
        
        return self.templates.format_template(
            template_name=template_name,
            transcription=transcription,
            **kwargs
        )
    
    def build_custom_prompt(
        self,
        base_template: str,
        transcription: str,
        custom_instructions: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Construit un prompt personnalisé
        
        Args:
            base_template: Nom du template de base
            transcription: Transcription à traiter
            custom_instructions: Instructions personnalisées
            **kwargs: Variables additionnelles
        
        Returns:
            Prompt personnalisé
        """
        prompt = self.templates.format_template(
            template_name=base_template,
            transcription=transcription,
            **kwargs
        )
        
        if custom_instructions:
            prompt += f"\n\nInstructions supplémentaires:\n{custom_instructions}"
        
        return prompt

# Instance globale
prompt_manager = PromptManager()
