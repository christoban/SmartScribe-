from __future__ import annotations  
  
from functools import lru_cache  
from pathlib import Path  
  
from pydantic_settings import BaseSettings, SettingsConfigDict  
  
  
_BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/  
  
class Settings(BaseSettings):  
    # 🔹 Informations générales  
    APP_NAME: str = "SmartScribe"  
    APP_VERSION: str = "1.0.0"  
    DEBUG: bool = False  
    API_V1_STR: str = "/api/v1"  
  
    # 🔹 Base de données  
    MONGO_URI: str  
    MONGO_DB_NAME: str = "smartscribe"  
  
    # 🔹 Sécurité  
    JWT_SECRET_KEY: str  
    JWT_ALGORITHM: str = "HS256"  
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h  
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  
  
    # 🔹 Infrastructure (Redis & Celery)  
    REDIS_URL: str = "redis://localhost:6379/0"  
  
    # 🔹 Chemins (Gestion des médias et IA)  
    BASE_DIR: Path = _BACKEND_DIR  
    STORAGE_PATH: Path = BASE_DIR / "storage"  
      
    # Arborescence média  
    UPLOAD_DIR: Path = STORAGE_PATH / "uploads"  
    AUDIO_DIR: Path = STORAGE_PATH / "audio"  
    VIDEO_DIR: Path = STORAGE_PATH / "video"  
    FRAMES_DIR: Path = STORAGE_PATH / "keyframes"  # <-- Indispensable pour la Vision  
    DOCS_DIR: Path = STORAGE_PATH / "exports"  
  
    # 🔹 IA Cloud (Groq & Gemini)  
    GROQ_API_KEY: str  
    GOOGLE_API_KEY: str = ""  
    HF_TOKEN: str = "" # Pour télécharger les modèles si besoin  
  
    # 🔹 IA Locale (Ollama & Fine-Tuning)  
    OLLAMA_BASE_URL: str = "http://localhost:11434"  
    LOCAL_LLM_MODEL: str = "mistral-smartscribe:latest" # Ton modèle fine-tuné  
    VISION_MODEL: str = "moondream:latest"             # Ton modèle de vision léger  
      
    # Paramètres Fine-tuning (Unsloth)  
    DATASET_PATH: Path = STORAGE_PATH / "datasets"  
    LORA_OUTPUT_DIR: Path = STORAGE_PATH / "lora_adapters"  
  
    # 🔹 Configuration Pydantic  
    model_config = SettingsConfigDict(  
        # Chemin absolu => robuste quel que soit le cwd (root repo, backend/, docker, etc.)  
        env_file=_BACKEND_DIR / ".env",  
        env_file_encoding="utf-8",  
        extra="ignore" # Ignore les variables inutiles dans le .env  
    )  
  
    # ✅ Méthode pour créer les dossiers au démarrage  
    def ensure_directories(self) -> None:  
        directories = [  
            self.UPLOAD_DIR, self.AUDIO_DIR, self.VIDEO_DIR,   
            self.FRAMES_DIR, self.DOCS_DIR, self.DATASET_PATH,  
            self.LORA_OUTPUT_DIR  
        ]  
        for folder in directories:  
            folder.mkdir(parents=True, exist_ok=True)  
  
    # --- Compat (ancien code) ---  
    @property  
    def UPLOAD_PATH(self) -> Path:  # noqa: N802 (legacy)  
        # Certains modules historiques utilisent settings.UPLOAD_PATH.  
        return self.UPLOAD_DIR  
  
    # 🔧 CORRECTION BLOQUANTE : Ajout de STORAGE_DIR pour compatibilité  
    @property  
    def STORAGE_DIR(self) -> Path:  # noqa: N802  
        """  
        Alias pour STORAGE_PATH (compatibilité avec orchestrator.py).  
        Le code utilise settings.STORAGE_DIR dans orchestrator.py ligne 167,  
        mais seul STORAGE_PATH existait. Cette propriété résout l'AttributeError.  
        """  
        return self.STORAGE_PATH  
  
  
@lru_cache()  
def get_settings() -> Settings:  
    # On initialise ici pour que le cache gère l'instance unique  
    _settings = Settings()  
    # On s'assure que les dossiers existent seulement quand on récupère les réglages  
    _settings.ensure_directories()  
    return _settings  
  
settings = get_settings()