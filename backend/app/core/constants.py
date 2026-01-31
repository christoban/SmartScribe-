# app/core/constants.py

# -------------------
# Types de fichiers autorisés
# -------------------
ALLOWED_AUDIO = ['mp3', 'wav', 'm4a', 'flac']
ALLOWED_VIDEO = ['mp4', 'mov', 'avi', 'mkv', 'webm']
ALLOWED_DOCS  = ['pdf', 'docx', 'txt']

# -------------------
# Types de médias
# -------------------
MEDIA_TYPE_AUDIO = "audio"
MEDIA_TYPE_VIDEO = "video"
MEDIA_TYPE_DOC   = "document"

# -------------------
# Limites
# -------------------
MAX_UPLOAD_SIZE_MB = 500  # Augmenté à 500 car les vidéos de cours sont lourdes
CHUNK_SIZE = 1024 * 1024  # 1MB pour les flux de lecture/écriture

# -------------------
# État du pipeline (Status) - Cohérence avec la DB
# -------------------
STATUS_PENDING = "pending"       # Reçu, en attente dans la file
STATUS_PROCESSING = "processing" # En cours de traitement (OCR/STT)
STATUS_COMPLETED = "completed"   # Terminé et prêt à être lu
STATUS_FAILED = "failed"         # Erreur rencontrée

# -------------------
# Paramètres IA (Groq & Vision)
# -------------------
# On utilise Whisper Large V3 sur Groq pour une précision maximale
WHISPER_MODEL = "whisper-large-v3" 
# Le modèle de raffinement Llama
LLM_MODEL = "llama-3.3-70b-versatile"
DEFAULT_LANGUAGE = "fr"

# -------------------
# Vision (PaddleOCR)
# -------------------
KEYFRAME_INTERVAL_SEC = 2  # On prend une image toutes les 2 secondes
OCR_LANG = "fr"
MAX_CPU_THREADS = 2        # Pour ton Semaphore

# -------------------
# Celery
# -------------------
CELERY_TASK_QUEUE = "smart_scribe_tasks"

from enum import Enum

class ContentType(str, Enum):
    COURSE = "course"
    FORMATION = "formation"
    PODCAST = "podcast"
    REUNION = "reunion"
    REPORTAGE = "reportage"
    JOURNAL = "journal"
    # Tutorial peut être mappé sur formation ou course
    TUTORIAL = "formation" 
    AUTO = "auto"
