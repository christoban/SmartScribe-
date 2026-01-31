from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

# Configuration du hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Exception standard pour la sécurité
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# --- HACHAGE ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT ---
def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Génère un JWT court pour l'authentification active."""
    to_encode = {"sub": str(user_id)} # 'sub' est le standard pour l'ID utilisateur
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Génère un JWT long (ex: 7 jours) pour renouveler l'access token."""
    to_encode = {"sub": str(user_id)}
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if not payload.get("sub"):
            raise CREDENTIALS_EXCEPTION
        return payload
    except ExpiredSignatureError:
        # On peut lever une 401 spécifique ou ajouter un détail "Token expired"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise CREDENTIALS_EXCEPTION


def decode_access_token(token: str) -> dict:
    """Compat: décode un access token (vérifie aussi le type)."""
    payload = decode_token(token)
    if payload.get("type") not in (None, "access"):
        raise CREDENTIALS_EXCEPTION
    return payload