import time
from fastapi import Request
from app.core.logger import get_logger

logger = get_logger("middleware")

async def add_process_time_header(request: Request, call_next):
    """
    Mesure le temps de traitement de chaque requête.
    Ajoute un header 'X-Process-Time' à la réponse.
    """
    start_time = time.perf_counter() # Plus précis que time.time() pour les mesures de durée
    
    response = await call_next(request)
    
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    
    # On logue uniquement si c'est significatif (ex: > 1s) ou pour le debug
    logger.debug(f"Path: {request.url.path} | Time: {process_time:.4f}s")
    
    return response