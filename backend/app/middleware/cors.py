from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    """
    Configure les accès cross-origin.
    En production, on limite aux domaines de confiance.
    """
    # En phase de dev, on peut utiliser ["*"]
    # Mais préparons déjà le terrain pour la prod
    origins = [
        "http://localhost:3000", # Port par défaut de Next.js / React
        "http://127.0.0.1:3000",
        "https://scolar-ai.com",  # Ton futur domaine
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if not settings.DEBUG else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )