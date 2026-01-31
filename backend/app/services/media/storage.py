"""
Service de gestion du stockage des fichiers média
"""
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.core.logger import get_logger
import uuid
import asyncio

class StorageService:
    """Gère le stockage des fichiers média"""
    
    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIR)
        self.temp_path = self.base_path / "temp"
        self._ensure_directories()
        self._logger = get_logger("storage")
    
    def _ensure_directories(self):
        """Crée les répertoires nécessaires"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
    
    def get_user_directory(self, user_id: str) -> Path:
        """Retourne le répertoire de l'utilisateur"""
        user_dir = self.base_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def save_file(self, file_content: bytes, filename: str, user_id: str) -> Path:
        """
        Sauvegarde un fichier dans le répertoire de l'utilisateur
        Retourne le chemin complet du fichier sauvegardé
        """
        user_dir = self.get_user_directory(user_id)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = user_dir / unique_filename
        
        with file_path.open("wb") as f:
            f.write(file_content)
        
        self._logger.info("💾 Fichier sauvegardé: %s", file_path)
        return file_path

    async def save_file_async(self, file_content: bytes, filename: str, user_id: str) -> Path:
        """Version async (I/O disque dans un thread)."""
        return await asyncio.to_thread(self.save_file, file_content, filename, user_id)
    
    def save_temp_file(self, file_content: bytes, filename: str) -> Path:
        """
        Sauvegarde un fichier temporaire
        Retourne le chemin complet du fichier temporaire
        """
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = self.temp_path / unique_filename
        
        with file_path.open("wb") as f:
            f.write(file_content)
        
        return file_path
    
    def delete_file(self, file_path: str) -> bool:
        """Supprime un fichier"""
        path = Path(file_path)
        if path.exists():
            path.unlink()
            self._logger.info("🗑️ Fichier supprimé: %s", file_path)
            return True
        return False
    
    def get_file_size(self, file_path: str) -> int:
        """Retourne la taille d'un fichier en octets"""
        path = Path(file_path)
        if path.exists():
            return path.stat().st_size
        return 0
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Nettoie les fichiers temporaires plus anciens que X heures"""
        import time
        current_time = time.time()
        threshold = older_than_hours * 3600
        
        cleaned = 0
        for file_path in self.temp_path.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > threshold:
                    file_path.unlink()
                    cleaned += 1
        
        if cleaned > 0:
            self._logger.info("🧹 %s fichiers temporaires nettoyés", cleaned)

# Instance globale
storage_service = StorageService()
