import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.stt.whisper_service import WhisperService

@pytest.fixture
def fake_audio_path(tmp_path):
    file = tmp_path / "test_audio.wav"
    file.write_bytes(b"fake audio content")
    return file

@pytest.mark.asyncio
@patch("app.services.stt.whisper_service.whisper.load_model")
async def test_transcribe_segmented_audio(mock_load_model, fake_audio_path):
    # Setup
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {"text": "Bonjour test"}
    mock_load_model.return_value = fake_model

    service = WhisperService()
    # On teste la méthode de base
    result = await service.transcribe_audio(fake_audio_path)

    assert result == "Bonjour test"
    assert fake_model.transcribe.called

@pytest.mark.asyncio
@patch("app.services.stt.whisper_service.get_database")
@patch("app.services.stt.whisper_service.whisper.load_model")
async def test_process_and_save_success(mock_load_model, mock_get_db, fake_audio_path):
    # Mock du modèle
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {"text": "Transcription sauvée"}
    mock_load_model.return_value = fake_model

    # Mock de la DB
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_db.transcriptions = mock_collection
    mock_get_db.return_value = mock_db

    service = WhisperService()
    media_id = "test-123"
    
    result = await service.process_and_save(fake_audio_path, media_id)

    assert result == "Transcription sauvée"
    # Vérifie que insert_one a été appelé avec les bonnes données
    assert mock_collection.insert_one.called
    args = mock_collection.insert_one.call_args[0][0]
    assert args["media_id"] == media_id
    assert args["text"] == "Transcription sauvée"