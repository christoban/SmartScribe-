"""
Service OCR - Extraction de texte depuis les images
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import pytesseract
from PIL import Image
from app.core.logger import get_logger

# Logger module
logger = get_logger("ocr_engine")

# Optionnel: Support pour PaddleOCR si disponible
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.warning("PaddleOCR non disponible, utilisation de Tesseract uniquement")

class OCREngine:
    """Moteur OCR pour extraire le texte des images"""
    
    def __init__(self, engine: str = "tesseract"):
        """
        Args:
            engine: "tesseract" ou "paddleocr"
        """
        self.engine = engine
        self.logger = logger
        
        if engine == "paddleocr" and not PADDLEOCR_AVAILABLE:
            self.logger.warning("PaddleOCR non disponible, basculement vers Tesseract")
            self.engine = "tesseract"
        
        if engine == "paddleocr" and PADDLEOCR_AVAILABLE:
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='fr')
    
    def extract_text(self, image_path: str | Path, lang: str = "fra+eng") -> str:
        """
        Extrait le texte d'une image
        
        Args:
            image_path: Chemin vers l'image
            lang: Langue(s) pour Tesseract (ex: "fra+eng")
        
        Returns:
            Texte extrait
        """
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Image non trouvée: {image_path}")
        
        if self.engine == "tesseract":
            return self._extract_with_tesseract(str(image_path_obj), lang)
        elif self.engine == "paddleocr":
            return self._extract_with_paddleocr(str(image_path_obj))
        else:
            raise ValueError(f"Engine OCR inconnu: {self.engine}")
    
    def _extract_with_tesseract(self, image_path: str, lang: str) -> str:
        """Extraction avec Tesseract"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang)
            self.logger.info(f"📝 Texte extrait avec Tesseract: {len(text)} caractères")
            return text.strip()
        except Exception as e:
            self.logger.error(f"❌ Erreur Tesseract: {e}")
            return ""
    
    def _extract_with_paddleocr(self, image_path: str) -> str:
        """Extraction avec PaddleOCR"""
        if not PADDLEOCR_AVAILABLE:
            return ""
        
        try:
            result = self.paddle_ocr.ocr(image_path, cls=True)
            text_lines = []
            
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) > 1:
                        text_lines.append(line[1][0])
            
            text = "\n".join(text_lines)
            self.logger.info(f"📝 Texte extrait avec PaddleOCR: {len(text)} caractères")
            return text.strip()
        except Exception as e:
            self.logger.error(f"❌ Erreur PaddleOCR: {e}")
            return ""
    
    def extract_text_batch(self, image_paths: List[str], lang: str = "fra+eng") -> List[str]:
        """
        Extrait le texte de plusieurs images
        
        Args:
            image_paths: Liste des chemins d'images
            lang: Langue(s) pour Tesseract
        
        Returns:
            Liste des textes extraits
        """
        results = []
        for image_path in image_paths:
            try:
                text = self.extract_text(image_path, lang)
                results.append(text)
            except Exception as e:
                self.logger.error(f"❌ Erreur lors de l'extraction de {image_path}: {e}")
                results.append("")
        
        return results
    
    def extract_text_from_keyframes(
        self,
        keyframe_paths: List[str | Path],
        lang: str = "fra+eng"
    ) -> dict:
        """
        Extrait le texte de plusieurs keyframes et retourne un dictionnaire
        
        Args:
            keyframe_paths: Liste des chemins des keyframes
            lang: Langue(s) pour Tesseract
        
        Returns:
            Dictionnaire {chemin_image: texte_extrait}
        """
        results = {}
        for keyframe_path in keyframe_paths:
            text = self.extract_text(keyframe_path, lang)
            if text:
                results[str(keyframe_path)] = text
        
        return results

# Instance globale (par défaut Tesseract)
ocr_engine = OCREngine(engine="tesseract")
