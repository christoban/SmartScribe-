"""  
Service d'extraction de texte depuis différents formats de documents  
"""  
from pathlib import Path  
from typing import Optional  
import PyPDF2  
from docx import Document  
  
from app.core.logger import get_logger  
  
logger = get_logger("text_extractor")  
  
def extract_text_from_pdf(file_path: Path) -> str:  
    """Extrait le texte d'un fichier PDF."""  
    try:  
        text_content = []  
        with open(file_path, 'rb') as file:  
            pdf_reader = PyPDF2.PdfReader(file)  
            for page_num, page in enumerate(pdf_reader.pages):  
                page_text = page.extract_text()  
                if page_text:  
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")  
          
        return "\n\n".join(text_content)  
    except Exception as e:  
        logger.error("❌ Erreur extraction PDF: %s", e)  
        raise  
   
def extract_text_from_docx(file_path: Path) -> str:  
    """Extrait le texte d'un fichier DOCX."""  
    try:  
        doc = Document(file_path)  
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]  
        return "\n\n".join(paragraphs)  
    except Exception as e:  
        logger.error("❌ Erreur extraction DOCX: %s", e)  
        raise  
  
def extract_text_from_txt(file_path: Path) -> str:  
    """Lit le contenu d'un fichier TXT."""  
    try:  
        with open(file_path, 'r', encoding='utf-8') as file:  
            return file.read()  
    except UnicodeDecodeError:  
        # Tentative avec un autre encodage  
        try:  
            with open(file_path, 'r', encoding='latin-1') as file:  
                return file.read()  
        except Exception as e:  
            logger.error("❌ Erreur lecture TXT: %s", e)  
            raise  
    except Exception as e:  
        logger.error("❌ Erreur lecture TXT: %s", e)  
        raise  
  
def extract_text_from_document(file_path: Path) -> Optional[str]:  
    """  
    Extrait le texte d'un document selon son extension.  
    Supporte : PDF, DOCX, DOC (via DOCX), TXT  
    """  
    ext = file_path.suffix.lower()  
      
    logger.info("📄 Extraction texte depuis %s (format: %s)", file_path.name, ext)  
      
    try:  
        if ext == ".pdf":  
            return extract_text_from_pdf(file_path)  
        elif ext in [".docx", ".doc"]:  
            return extract_text_from_docx(file_path)  
        elif ext == ".txt":  
            return extract_text_from_txt(file_path)  
        else:  
            logger.error("❌ Format non supporté: %s", ext)  
            return None  
    except Exception as e:  
        logger.error("❌ Échec extraction texte: %s", e)  
        return None