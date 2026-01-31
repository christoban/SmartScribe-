import pytest
from pathlib import Path
from backend.app.services.media.audio_processor import VideoToAudioService
from app.services.media.noise_cleaner import NoiseCleaner
from app.services.media.splitter import AudioSplitter

@pytest.mark.asyncio
async def test_full_media_pipeline():
    # 1. Préparation
    video_path = Path("jaiTest.mp4")
    if not video_path.exists():
        pytest.fail("Fichier jaiTest.mp4 introuvable à la racine.")

    # 2. Pipeline
    audio_raw = await VideoToAudioService.convert(str(video_path), "test_raw.wav")
    audio_clean = await NoiseCleaner.clean_audio(audio_raw, "test_clean.wav")
    
    # Assure-toi de passer un Path ou que le service convertit en Path
    chunks = await AudioSplitter.split_audio(audio_clean, "test_chunks")

    # 3. Assertions
    assert Path(audio_raw).exists()
    assert Path(audio_clean).exists()
    assert len(chunks) > 0
    print(f"✅ Pipeline validé : {len(chunks)} segments créés.")