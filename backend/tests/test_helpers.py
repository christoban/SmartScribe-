import pytest
from datetime import datetime
from app.utils.helpers import (
    get_now_utc, 
    generate_unique_filename, 
    slugify, 
    format_api_response
)

def test_get_now_utc():
    now = get_now_utc()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None  # Vérifie que c'est bien de l'UTC (offset-aware)

def test_generate_unique_filename():
    original = "cours_algebre.mp3"
    unique_name = generate_unique_filename(original)
    
    # Vérifie que l'extension est conservée
    assert unique_name.endswith(".mp3")
    # Vérifie que le nom a été modifié (UUID fait 32 chars + .mp3 = 36 chars)
    assert len(unique_name) > len(original)
    assert unique_name != original

def test_slugify():
    raw_text = "Cours d'Algèbre : 2026! 😊"
    result = slugify(raw_text)
    # Vérifie la normalisation (pas d'accents, pas d'emojis, minuscules, tirets)
    assert result == "cours-dalgebre-2026"

def test_format_api_response():
    data = {"user_id": 123}
    response = format_api_response(data, message="Test réussi")
    
    assert response["status"] == "success"
    assert response["message"] == "Test réussi"
    assert response["data"] == data
    assert "timestamp" in response