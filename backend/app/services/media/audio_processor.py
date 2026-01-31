import subprocess
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from app.core.config import settings
from app.core.logger import logger

class AudioProcessor:
    def __init__(self):
        self.output_format = "mp3"
        self.sample_rate = 16000
        self.chunk_duration = 600
        self._check_dependencies()

    def _check_dependencies(self):
        """Vérifie si FFmpeg est installé sur le système."""
        if not shutil.which("ffmpeg"):
            logger.critical("FFmpeg n'est pas installé sur le système !")
            raise RuntimeError("FFmpeg dependency missing")

    def get_duration(self, file_path: Path) -> float:
        """Récupère la durée de manière robuste."""
        command = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Impossible de lire la durée de {file_path.name} : {e}")
            return 0.0
        
    def extract_audio(self, input_path: Path) -> Path:
        """Extrait l'audio initial (version compressée pour économiser l'espace)"""
        if not input_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {input_path}")

        unique_filename = f"{uuid.uuid4()}_{input_path.stem}.{self.output_format}"
        output_path = settings.AUDIO_DIR / unique_filename

        # On baisse un peu le bitrate (64k) car c'est un fichier de travail intermédiaire
        command = [
            "ffmpeg", "-i", str(input_path),
            "-vn", "-ac", "1", "-ar", str(self.sample_rate),
            "-ab", "64k", 
            "-y", str(output_path)
        ]

        try:
            logger.info(f"🔄 Extraction audio : {input_path.name}")
            subprocess.run(command, check=True, capture_output=True, timeout=300)
            return output_path
        except Exception as e:
            logger.error(f"❌ Erreur extraction : {e}")
            raise

    def split_audio(self, input_path: Path) -> List[Path]:
        """
        Découpe et convertit simultanément en MP3 légers.
        """
        file_id = f"chunk_{uuid.uuid4().hex[:8]}"
        output_pattern = settings.AUDIO_DIR / f"{file_id}_%03d.{self.output_format}"

        # On force l'encodage libmp3lame à 64k pour garantir la petite taille
        command = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-f", "segment",
            "-segment_time", str(self.chunk_duration),
            "-c:a", "libmp3lame", 
            "-ac", "1", 
            "-ar", str(self.sample_rate),
            "-b:a", "64k",
            "-reset_timestamps", "1",
            str(output_pattern)
        ]

        try:
            logger.info(f"✂️ Découpage et compression en segments : {input_path.name}")
            # On utilise capture_output pour voir l'erreur si ça replante
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            chunks = sorted(list(settings.AUDIO_DIR.glob(f"{file_id}_*." + self.output_format)))
            
            if not chunks:
                logger.error("FFmpeg n'a généré aucun segment.")
                return [input_path]
                
            return chunks
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erreur FFmpeg (Split): {e.stderr}")
            return [input_path]

audio_processor = AudioProcessor()

