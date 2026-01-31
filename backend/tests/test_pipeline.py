import pytest
from pathlib import Path
from app.services.orchestrator import processing_service
from app.db.mongo import connect_to_mongo, close_mongo_connection

@pytest.mark.asyncio
async def test_full_pipeline():
    """
    Test du pipeline complet pour Pytest.
    Pytest détecte automatiquement les fonctions commençant par 'test_'
    """
    await connect_to_mongo()
    
    test_file = Path("Audio_test.aac") 
    media_id = "test_123"
    
    if not test_file.exists():
        pytest.skip(f"Fichier {test_file} introuvable à la racine.")

    print("\n🚀 Lancement du test pipeline...")
    result = await processing_service.process_media(media_id, test_file)
    
    # Avec pytest, on utilise 'assert' pour valider le résultat
    assert result is not None, "Le pipeline a renvoyé None"
    print(f"✅ Succès ! Transcription ID: {result.id}")
    print(f"📝 Extrait : {result.text[:100]}...")
    
    await close_mongo_connection()