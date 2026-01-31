import html
import re
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
from app.core.logger import get_logger
from app.core.config import settings

class PDFExporter:
    def __init__(self):
        self.logger = get_logger("export.pdf")
        self.output_dir = Path(settings.DOCS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _escape_and_clean(self, text: str) -> str:
        """Échappe le XML et nettoie uniquement les caractères impossibles."""
        if not text: return ""
        # 1. Échappement des caractères réservés (&, <, >)
        text = html.escape(text)
        # 2. On garde les accents (latin-1) mais on vire les émojis complexes
        # On encode en latin-1 (qui contient les accents FR) et on ignore le reste (émojis)
        return text.encode('latin-1', 'ignore').decode('latin-1')

    async def generate_pdf(self, note_data: Dict, filename: Optional[str] = None) -> tuple[str, int]:
        try:
            if filename is None:
                filename = f"export_{uuid.uuid4().hex}.pdf"
            
            file_path = self.output_dir / filename
            # Ajout de marges pour un look plus pro
            doc = SimpleDocTemplate(
                str(file_path), 
                pagesize=A4,
                rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50
            )
            
            story = []
            styles = getSampleStyleSheet()

            # Style Titre principal
            title_style = ParagraphStyle(
                'CustomTitle', 
                parent=styles['Heading1'], 
                fontSize=24, 
                alignment=TA_CENTER, 
                spaceAfter=30,
                textColor='#2C3E50'
            )
            
            # Style pour les citations/warnings
            warning_style = ParagraphStyle(
                'Warning', 
                parent=styles['Normal'], 
                textColor='#34495E', 
                backColor='#F2F4F4', 
                borderPadding=10, 
                leftIndent=20,
                fontName='Helvetica-Oblique'
            )

            # 1. Titre
            clean_title = self._escape_and_clean(note_data.get('title', 'Notes'))
            story.append(Paragraph(clean_title, title_style))

            content = note_data.get('content', '')
            lines = content.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.1*inch))
                    continue

                # --- IMAGES ---
                image_match = re.match(r'!\[.*?\]\((.*?)\)', line)
                if image_match:
                    img_path = Path(image_match.group(1))
                    if img_path.exists():
                        try:
                            # Ajustement automatique de l'image
                            img = Image(str(img_path))
                            # Ratio pour ne pas dépasser la largeur de la page
                            max_width = 450 
                            if img.drawWidth > max_width:
                                ratio = max_width / img.drawWidth
                                img.drawWidth = max_width
                                img.drawHeight = img.drawHeight * ratio
                            
                            img.hAlign = 'CENTER'
                            story.append(Spacer(1, 0.1*inch))
                            story.append(img)
                            story.append(Spacer(1, 0.1*inch))
                        except Exception as e:
                            self.logger.error(f"Erreur image PDF: {e}")
                    continue

                # --- TEXTE ---
                if line.startswith('# '):
                    story.append(Paragraph(self._escape_and_clean(line[2:]), styles['Heading1']))
                elif line.startswith('## '):
                    story.append(Paragraph(self._escape_and_clean(line[3:]), styles['Heading2']))
                elif line.startswith('### '):
                    story.append(Paragraph(self._escape_and_clean(line[4:]), styles['Heading3']))
                elif line.startswith('> '):
                    story.append(Paragraph(self._escape_and_clean(line[2:]), warning_style))
                elif line.startswith('- ') or line.startswith('* '):
                    # Utilisation de puces HTML pour ReportLab
                    story.append(Paragraph(f"&bull; {self._escape_and_clean(line[2:])}", styles['Normal']))
                else:
                    story.append(Paragraph(self._escape_and_clean(line), styles['Normal']))

            # Construction asynchrone
            await asyncio.to_thread(doc.build, story)
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size

        except Exception as e:
            self.logger.error(f"❌ Erreur PDF: {str(e)}")
            raise e

pdf_exporter = PDFExporter()
generate_pdf = pdf_exporter.generate_pdf