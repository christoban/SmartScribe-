from fastapi import HTTPException, status

class AppException(HTTPException):
    """Base pour toutes les exceptions de SmartScribe."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class FileTooLargeException(AppException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop lourd. Limite : {max_size_mb} MB"
        )

class InvalidFileTypeException(AppException):
    def __init__(self, allowed_extensions: list):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format non supporté. Extensions autorisées : {allowed_extensions}"
        )

class NotFoundException(AppException):
    """Utilisé quand un User, un Media ou une Note n'existe pas."""
    def __init__(self, resource: str = "Ressource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} introuvable."
        )

class AIProcessingException(AppException):
    """Erreur spécifique au traitement Gemini ou Whisper."""
    def __init__(self, detail: str = "Erreur lors du traitement IA"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )