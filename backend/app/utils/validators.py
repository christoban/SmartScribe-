from fastapi import UploadFile
from typing import List
from app.core.constants import MAX_UPLOAD_SIZE_MB
from app.utils.exceptions import FileTooLargeException, InvalidFileTypeException

def validate_upload(file: UploadFile, allowed_extensions: List[str]) -> None:
    """
    Validation de haut niveau utilisant nos exceptions personnalisées.
    """
    # 1. Validation de l'extension
    filename = file.filename or ""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        # On lance notre propre exception au lieu d'une HTTPException générique
        raise InvalidFileTypeException(allowed_extensions=allowed_extensions)

    # 2. Validation de la taille (Optimisée)
    max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > max_size_bytes:
        # On passe la constante pour que le message d'erreur soit dynamique
        raise FileTooLargeException(max_size_mb=MAX_UPLOAD_SIZE_MB)