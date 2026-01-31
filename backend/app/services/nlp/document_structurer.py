"""
Service de structuration de documents avant export
"""
from typing import Dict, List, Optional
from app.core.logger import get_logger
import re

class DocumentStructurer:
    """Structure les documents avant l'export"""
    
    def __init__(self):
        self.logger = get_logger("document_structurer")
    
    def structure_for_export(
        self,
        content: str,
        content_type: str = "note",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Structure un contenu pour l'export en extrayant le titre et les sections.
        """
        if metadata is None:
            metadata = {}
        
        # 1. Tenter d'extraire le titre du contenu si non présent dans metadata
        extracted_title = self._extract_main_title(content)
        final_title = metadata.get("title") or extracted_title or "Notes de cours"
        
        structured = {
            "title": final_title,
            "content_type": content_type,
            "sections": self._extract_sections(content),
            "metadata": metadata,
            "raw_content": content # Vital pour les exporters qui gèrent le Markdown
        }
        
        return structured

    def _extract_main_title(self, content: str) -> Optional[str]:
        """Cherche la première ligne commençant par # pour définir le titre."""
        match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Découpe le texte en blocs basés sur les titres H1."""
        sections = []
        lines = content.split('\n')
        
        current_section = {"title": "Introduction", "content": []}
        
        for line in lines:
            # Détection des titres H1 (# Titre)
            h1_match = re.match(r'^#\s+(.*)', line)
            if h1_match:
                # Si on a déjà du contenu accumulé, on ferme la section précédente
                if current_section["content"]:
                    current_section["content"] = '\n'.join(current_section["content"]).strip()
                    sections.append(current_section)
                
                current_section = {
                    "title": h1_match.group(1).strip(),
                    "content": []
                }
            else:
                current_section["content"].append(line)

        # Ajout de la dernière section
        if current_section["content"] or len(sections) == 0:
            current_section["content"] = '\n'.join(current_section["content"]).strip()
            sections.append(current_section)
        
        return sections

    def format_for_pdf(self, structured_doc: Dict) -> Dict:
        return {
            "title": structured_doc["title"],
            "sections": structured_doc["sections"],
            "metadata": structured_doc["metadata"]
        }
    
    def format_for_docx(self, structured_doc: Dict) -> Dict:
        return {
            "title": structured_doc["title"],
            "sections": structured_doc["sections"],
            "metadata": structured_doc["metadata"]
        }
    
    def format_for_txt(self, structured_doc: Dict) -> str:
        """Version propre pour l'export texte brut."""
        lines = [structured_doc["title"], "=" * len(structured_doc["title"]), ""]
        
        for section in structured_doc["sections"]:
            if section["title"] != "Introduction":
                lines.append(f"\n{section['title']}")
                lines.append("-" * len(section["title"]))
            lines.append(section["content"])
        
        return '\n'.join(lines)

# Instance globale
document_structurer = DocumentStructurer()