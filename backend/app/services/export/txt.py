import re
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Optional
from app.core.logger import get_logger
from app.core.config import settings

class TXTExporter:
    """Génère des fichiers TXT propres et lisibles sans balises parasites."""
    
    def __init__(self):
        self.logger = get_logger("export.txt")
        self.output_dir = Path(settings.DOCS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _clean_text(self, text: str) -> str:
        """Nettoyage des caractères spéciaux pour une compatibilité TXT maximale."""
        if not text: return ""
        # On garde les émojis ici car le TXT en UTF-8 les supporte bien, 
        # contrairement au PDF standard
        return text.strip()

    async def generate_txt(self, note_data: Dict, filename: Optional[str] = None) -> tuple[str, int]:
        try:
            if filename is None:
                filename = f"export_{uuid.uuid4().hex}.txt"
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            file_path = self.output_dir / filename
            
            title = self._clean_text(note_data.get('title', 'Notes'))
            content = note_data.get('content', '')

            # --- NETTOYAGE DES BALISES D'IMAGES ---
            # On remplace ![alt](path) par [ILLUSTRATION]
            clean_content = re.sub(r'!\[(.*?)\]\(.*?\)', r'[ILLUSTRATION : \1]', content)

            # Nettoyage des sauts de lignes excessifs
            clean_content = re.sub(r'\n{3,}', '\n\n', clean_content)
            
            # Formatage visuel du TXT
            header_line = "=" * min(len(title), 80)
            text_content = f"{header_line}\n{title.upper()}\n{header_line}\n\n{clean_content}"
            
            # SAUVEGARDE ASYNCHRONE
            # On utilise asyncio.to_thread pour ne pas bloquer l'event loop pendant l'écriture disque
            await asyncio.to_thread(self._write_file, file_path, text_content)
            
            file_size = file_path.stat().st_size
            self.logger.info(f"✅ TXT généré avec succès: {file_path}")
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la génération TXT: {e}")
            raise e

    def _write_file(self, path: Path, content: str):
        """Méthode synchrone appelée dans un thread."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

# Instance globale et alias
txt_exporter = TXTExporter()
generate_txt = txt_exporter.generate_txt