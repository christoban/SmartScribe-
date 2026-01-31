"""
Service d'analyse vidéo - Extraction de keyframes (images clés)
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import cv2
from app.core.logger import get_logger

class VideoAnalyzer:
    """Analyse les vidéos et extrait des images clés (keyframes)"""
    
    def __init__(self):
        self.logger = get_logger("video_analyzer")
    
    def extract_keyframes(
        self,
        video_path: str | Path,
        output_dir: Optional[str | Path] = None,
        interval_seconds: int = 30,
        max_frames: Optional[int] = None
    ) -> List[Path]:
        """
        Extrait des images clés d'une vidéo
        
        Args:
            video_path: Chemin vers la vidéo
            output_dir: Répertoire de sortie (optionnel)
            interval_seconds: Intervalle en secondes entre chaque keyframe
            max_frames: Nombre maximum de frames à extraire
        
        Returns:
            Liste des chemins des images extraites
        """
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            raise FileNotFoundError(f"Vidéo non trouvée: {video_path}")
        
        # Déterminer le répertoire de sortie
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = video_path_obj.parent / "keyframes"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Ouvrir la vidéo
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Impossible d'ouvrir la vidéo: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval_seconds)
        
        extracted_frames: List[Path] = []
        frame_count = 0
        saved_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extraire une frame tous les X frames
                if frame_count % frame_interval == 0:
                    if max_frames and saved_count >= max_frames:
                        break
                    
                    frame_filename = f"keyframe_{saved_count:04d}_{frame_count}.jpg"
                    frame_path = output_path / frame_filename
                    
                    cv2.imwrite(str(frame_path), frame)
                    extracted_frames.append(frame_path)
                    saved_count += 1
                    
                    self.logger.info(f"📸 Keyframe extraite: {frame_filename}")
                
                frame_count += 1
            
            self.logger.info(f"✅ {saved_count} keyframes extraites de {video_path}")
            
        finally:
            cap.release()
        
        return extracted_frames
    
    def extract_slides(
        self,
        video_path: str | Path,
        output_dir: Optional[str | Path] = None,
        similarity_threshold: float = 0.95
    ) -> List[Path]:
        """
        Extrait les slides/diapositives d'une vidéo en détectant les changements significatifs
        
        Args:
            video_path: Chemin vers la vidéo
            output_dir: Répertoire de sortie
            similarity_threshold: Seuil de similarité pour détecter un changement de slide
        
        Returns:
            Liste des chemins des slides extraites
        """
        video_path_obj = Path(video_path)
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = video_path_obj.parent / "slides"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Impossible d'ouvrir la vidéo: {video_path}")
        
        extracted_slides: List[Path] = []
        prev_frame = None
        slide_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if prev_frame is not None:
                    # Calculer la similarité entre les frames
                    similarity = self._calculate_similarity(prev_frame, frame)
                    
                    if similarity < similarity_threshold:
                        # Changement significatif détecté - probablement une nouvelle slide
                        slide_filename = f"slide_{slide_count:04d}.jpg"
                        slide_path = output_path / slide_filename
                        cv2.imwrite(str(slide_path), frame)
                        extracted_slides.append(slide_path)
                        slide_count += 1
                        self.logger.info(f"📊 Slide détectée: {slide_filename}")
                
                prev_frame = frame.copy()
            
            self.logger.info(f"✅ {slide_count} slides extraites")
            
        finally:
            cap.release()
        
        return extracted_slides
    
    def _calculate_similarity(self, frame1, frame2) -> float:
        """Calcule la similarité entre deux frames"""
        # Convertir en niveaux de gris
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculer la corrélation
        result = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
        similarity = result[0][0]
        
        return similarity

# Instance globale
video_analyzer = VideoAnalyzer()
