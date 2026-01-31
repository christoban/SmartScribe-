import uuid
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

def get_now_utc() -> datetime:
    """Retourne l'heure actuelle en UTC (standard 2026)."""
    return datetime.now(timezone.utc)

def generate_unique_filename(original_name: str) -> str:
    """Génère un nom de fichier unique tout en gardant l'extension originale."""
    extension = original_name.split(".")[-1] if "." in original_name else "bin"
    return f"{uuid.uuid4().hex}.{extension}"

def slugify(text: str) -> str:
    """Transforme un titre de cours en nom de fichier propre."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)

def format_api_response(data: Any, message: str = "Success") -> dict:
    """Standardise toutes les réponses de l'API SmartScribe."""
    return {
        "status": "success",
        "message": message,
        "timestamp": get_now_utc().isoformat(),
        "data": data
    }