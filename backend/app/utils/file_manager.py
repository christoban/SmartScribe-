"""
Gestionnaire de fichiers - Utilitaires pour la manipulation de fichiers
"""
from pathlib import Path
from typing import Optional
import mimetypes
from app.core.logger import get_logger

class FileManager:
    """Utilitaires pour la gestion de fichiers"""
    
    def __init__(self):
        self.logger = get_logger("file_manager")
    
    def get_file_extension(self, filename: str) -> str:
        """Récupère l'extension d'un fichier"""
        return Path(filename).suffix.lower().lstrip('.')
    
    def get_mime_type(self, file_path: str) -> Optional[str]:
        """Récupère le type MIME d'un fichier"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
    
    def is_audio_file(self, filename: str) -> bool:
        """Vérifie si un fichier est un fichier audio"""
        audio_extensions = {'mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac', 'wma'}
        return self.get_file_extension(filename) in audio_extensions
    
    def is_video_file(self, filename: str) -> bool:
        """Vérifie si un fichier est un fichier vidéo"""
        video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv'}
        return self.get_file_extension(filename) in video_extensions
    
    def is_document_file(self, filename: str) -> bool:
        """Vérifie si un fichier est un document"""
        doc_extensions = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'}
        return self.get_file_extension(filename) in doc_extensions
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Récupère la taille d'un fichier en Mo"""
        path = Path(file_path)
        if path.exists():
            return path.stat().st_size / (1024 * 1024)
        return 0.0
    
    def ensure_directory(self, directory_path: str) -> Path:
        """Crée un répertoire s'il n'existe pas"""
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier pour éviter les caractères problématiques"""
        import re
        # Supprimer les caractères non autorisés
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limiter la longueur
        if len(filename) > 255:
            name, ext = Path(filename).stem, Path(filename).suffix
            filename = name[:255-len(ext)] + ext
        return filename

# Instance globale
file_manager = FileManager()
