from __future__ import annotations
from app.core.logger import get_logger
from app.services.ia.groq_client import groq_client
from app.services.ia.prompts.manager import prompt_manager
from app.core.constants import ContentType

logger = get_logger("ia.manager")

class IAManager:
    async def detect_content_type(self, transcription: str) -> str:
        """Détecte la catégorie globale du contenu pour orienter le prompt."""
        prompt = prompt_manager.templates.format_template(
            template_name="content_type_detection",
            transcription=transcription[:2000],
        )

        try:
            out = await groq_client.generate_completion(
                prompt=prompt, 
                system_msg="Tu es un classificateur de documents rapide et précis. Réponds uniquement par le nom de la catégorie."
            )
            out = out.strip().lower()
            
            for c in ContentType:
                if c.value in out:
                    return c.value
                    
        except Exception as exc:
            logger.warning("Detection content type fallback: %s", exc)
            
        return ContentType.COURSE.value
        
    async def generate_notes(self, transcription: str, content_type: str, visual_context: str = "") -> str:
        """Génère des notes expertes, illustrées et adaptées au domaine et au format."""
        
        # 🛡️ Protection contre les textes trop massifs
        max_chars = 60000 
        if len(transcription) > max_chars:
            logger.warning("⚠️ Transcription trop longue, tronquée")
            transcription = transcription[:max_chars] + "... [Tronqué pour optimisation]"

        # 🎯 DÉFINITION DU FORMAT SELON LE TYPE (Stratégie de rédaction)
        format_logic = {
            "course": "Format PÉDAGOGIQUE : Objectifs, définitions théoriques, schémas conceptuels et résumé.",
            "formation": "Format PRATIQUE : Étapes méthodologiques, guides de manipulation, sécurité et check-lists.",
            "podcast": "Format SYNTHÈSE : Idées majeures, verbatim ou citations clés, et structure par thèmes.",
            "reunion": "Format COMPTE-RENDU : Ordre du jour, décisions, points de blocage et To-Do list.",
            "reportage": "Format NARRATIF : Chronologie des faits, témoignages clés et analyse de contexte.",
            "journal": "Format ACTUALITÉ : Faits saillants, dates clés et synthèse rigoureuse."
        }
        selected_format = format_logic.get(content_type.lower(), format_logic["course"])

        # 🧠 SYSTEM PROMPT DÉVELOPPÉ (Expertise, Visuel et Structure)
        system_msg = (
            "### ROLE ET MISSION\n"
            "Tu es une IA experte multi-domaines spécialisée dans la synthèse pédagogique de haut niveau. "
            "Ton objectif est de transformer une transcription brute en un document 'Gold Standard'. "
            "Analyse le texte, identifie le domaine (Mécanique, IT, Droit, etc.) et incarne un 'Expert Senior' de ce secteur.\n\n"
            
            f"### STRATÉGIE DE RÉDACTION : {content_type.upper()}\n"
            f"Adopte impérativement ce style : {selected_format}\n\n"
            
            "### INSTRUCTIONS SPÉCIFIQUES VIDÉO ET VISUEL\n"
            "1. CONTEXTE VISUEL : Tu as accès à des descriptions de captures d'écran. Utilise-les pour enrichir tes explications. "
            "Si l'orateur est imprécis mais que le contexte visuel identifie une pièce ou un écran, utilise le terme technique exact.\n"
            "2. INSERTION D'IMAGES : Lorsqu'un concept, un composant ou un moment de la vidéo est crucial, insère la balise unique ` изображение `.\n"
            "3. LÉGENDE : Juste après la balise, ajoute une légende explicative entre parenthèses, ex: (Capture vidéo : Vue détaillée du composant X).\n"
            "4. PLACEMENT : La balise ` изображение ` doit être seule sur sa ligne, après le paragraphe qu'elle illustre.\n\n"
            "5. ABSENCE DE CONTEXTE : Même si le contexte visuel est faible ou absent (Audio), insère tout de même la balise ` изображение ` là où un schéma technique serait pertinent pour un lecteur. Ton rôle est de prévoir l'illustration.\n"
            
            "### DIRECTIVES DE STRUCTURE ET QUALITÉ\n"
            "1. HIÉRARCHIE : Utilise Markdown (H1 pour le titre, H2 pour les modules, H3 pour les sections).\n"
            "2. RIGUEUR TECHNIQUE : Rectifie les erreurs de l'orateur. Si l'orateur parle par l'absurde (ex: 'il faut enlever la batterie' alors qu'il veut dire l'inverse), rétablis la vérité technique.\n"
            "3. MISE EN FORME : Utilise du **gras** pour les termes clés, des émojis thématiques (⚙️, 💻, ⚖️) et des listes à puces.\n"
            "4. SÉCURITÉ : Isole les points critiques dans des blocs d'emphase : > ⚠️ **IMPORTANT**.\n"
            "5. TON : Professionnel, didactique, sans tics de langage ('euh', 'voilà'). Transforme l'oral en un écrit fluide et structuré."
            "6. TRANSFORMATION RADICALE : Ne résume pas. Réécris. Transforme le langage parlé familier en un langage écrit technique et soutenu.\n"
            "7. PRÉCISION DES CHIFFRES : Conserve impérativement tous les chiffres, prix (ex: 700 000 FCFA), distances et mesures. Ce sont des données critiques.\n"
            "8. PLACEMENT DE L'ILLUSTRATION : Tu DOIS insérer au moins 3 à 5 fois la balise ` изображение ` dans le document, dès qu'une pièce technique ou une méthode est décrite.\n"
        )

        # On fusionne la transcription et le contexte visuel pour le prompt final
        enriched_transcription = f"CONTEXTE VISUEL DISPONIBLE :\n{visual_context}\n\nTRANSCRIPTION BRUTE :\n{transcription}"

        prompt = prompt_manager.get_prompt_for_content_type(
            content_type=content_type,
            transcription=enriched_transcription,
            visual_context=visual_context,
        )

        return await groq_client.generate_completion(
            prompt=prompt, 
            system_msg=system_msg, 
            temperature=0.15 
        )

ia_manager = IAManager()